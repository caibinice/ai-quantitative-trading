#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="${1:?app root is required}"
RELEASE_DIR="${2:?release dir is required}"
APP_USER="${3:?app user is required}"
PUBLIC_IP="${4:?public ip is required}"
SHARED="$APP_ROOT/shared"

echo "[1/8] Installing lightweight native runtime"
dnf -y --disablerepo='epel*' install nginx python3.11 python3.11-pip >/dev/null

if ! swapon --show --noheadings | grep -q .; then
  fallocate -l 1G /swapfile
  chmod 600 /swapfile
  mkswap /swapfile >/dev/null
  swapon /swapfile
  grep -q '^/swapfile ' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

echo "[2/8] Preparing Python environments"
mkdir -p "$SHARED"/{acme,certbot-work,certbot-logs,letsencrypt}
if [[ ! -x "$SHARED/venv/bin/python" ]]; then
  python3.11 -m venv "$SHARED/venv"
fi
"$SHARED/venv/bin/python" -m pip install --disable-pip-version-check --upgrade pip >/dev/null
"$SHARED/venv/bin/python" -m pip install --disable-pip-version-check \
  -r "$RELEASE_DIR/backend/requirements.txt" >/dev/null

if [[ ! -x "$SHARED/certbot/bin/certbot" ]]; then
  python3.11 -m venv "$SHARED/certbot"
fi
"$SHARED/certbot/bin/python" -m pip install --disable-pip-version-check \
  --upgrade 'certbot==5.4.0' >/dev/null

echo "[3/8] Activating release"
previous_release="$(readlink -f "$APP_ROOT/current" 2>/dev/null || true)"
ln -sfn "$RELEASE_DIR" "$APP_ROOT/current.next"
mv -Tf "$APP_ROOT/current.next" "$APP_ROOT/current"
mkdir -p "$APP_ROOT/www"
ln -sfn "$RELEASE_DIR/frontend/dist" "$APP_ROOT/www/quant.next"
mv -Tf "$APP_ROOT/www/quant.next" "$APP_ROOT/www/quant"
chown -R "$APP_USER:$APP_USER" "$RELEASE_DIR"
chown "$APP_USER:$APP_USER" "$SHARED/app.env"
chmod 600 "$SHARED/app.env"
chmod 755 "$APP_ROOT" "$APP_ROOT/releases" "$APP_ROOT/www" "$RELEASE_DIR" "$SHARED" "$SHARED/acme"

render() {
  sed \
    -e "s|__APP_ROOT__|$APP_ROOT|g" \
    -e "s|__APP_USER__|$APP_USER|g" \
    -e "s|__PUBLIC_IP__|$PUBLIC_IP|g" \
    "$1" > "$2"
}

echo "[4/8] Installing systemd services"
render "$RELEASE_DIR/deploy/systemd/ai-quant-api.service.template" \
  /etc/systemd/system/ai-quant-api.service
render "$RELEASE_DIR/deploy/systemd/ai-quant-worker.service.template" \
  /etc/systemd/system/ai-quant-worker.service
render "$RELEASE_DIR/deploy/systemd/ai-quant-cert-renew.service.template" \
  /etc/systemd/system/ai-quant-cert-renew.service
install -m 644 "$RELEASE_DIR/deploy/systemd/ai-quant-cert-renew.timer" \
  /etc/systemd/system/ai-quant-cert-renew.timer
systemctl daemon-reload
systemctl enable ai-quant-api.service ai-quant-worker.service ai-quant-cert-renew.timer >/dev/null
systemctl restart ai-quant-api.service ai-quant-worker.service

echo "[5/8] Configuring Nginx bootstrap endpoint"
UNIFIED_SITE=/etc/nginx/conf.d/ai-platform.conf
if [[ -f "$UNIFIED_SITE" ]] && grep -q 'ai-blog-unified-platform' "$UNIFIED_SITE"; then
  echo "Unified blog Nginx configuration detected; preserving it."
else
  if [[ ! -f /etc/nginx/nginx.conf.dist ]]; then
    cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.dist
  fi
  install -m 644 "$RELEASE_DIR/deploy/nginx/nginx.conf" /etc/nginx/nginx.conf
  rm -f /etc/nginx/conf.d/ai-quant.conf
  render "$RELEASE_DIR/deploy/nginx/http.conf.template" /etc/nginx/conf.d/ai-quant.conf
fi
nginx -t
systemctl enable --now nginx >/dev/null
systemctl restart nginx

if systemctl is-active --quiet firewalld; then
  firewall-cmd --permanent --add-service=http >/dev/null
  firewall-cmd --permanent --add-service=https >/dev/null
  firewall-cmd --reload >/dev/null
fi
if command -v getenforce >/dev/null && [[ "$(getenforce)" == "Enforcing" ]]; then
  setsebool -P httpd_can_network_connect 1
  chcon -R -t httpd_sys_content_t "$RELEASE_DIR/frontend/dist" "$SHARED/acme"
fi

echo "[6/8] Requesting or reusing trusted IP certificate"
certificate="$SHARED/letsencrypt/live/ai-quant-ip/fullchain.pem"
if [[ ! -s "$certificate" ]]; then
  "$SHARED/certbot/bin/certbot" certonly \
    --non-interactive \
    --agree-tos \
    --register-unsafely-without-email \
    --preferred-profile shortlived \
    --webroot \
    --webroot-path "$SHARED/acme" \
    --ip-address "$PUBLIC_IP" \
    --cert-name ai-quant-ip \
    --config-dir "$SHARED/letsencrypt" \
    --work-dir "$SHARED/certbot-work" \
    --logs-dir "$SHARED/certbot-logs"
fi

echo "[7/8] Enabling HTTPS and renewal"
if [[ ! -f "$UNIFIED_SITE" ]] || ! grep -q 'ai-blog-unified-platform' "$UNIFIED_SITE"; then
  render "$RELEASE_DIR/deploy/nginx/https.conf.template" /etc/nginx/conf.d/ai-quant.conf
fi
nginx -t
systemctl restart nginx
systemctl enable --now ai-quant-cert-renew.timer >/dev/null

echo "[8/8] Verifying services and pruning old releases"
healthy=false
for _attempt in {1..30}; do
  if curl --fail --silent http://127.0.0.1:8000/api/health >/dev/null; then
    healthy=true
    break
  fi
  sleep 1
done
if [[ "$healthy" != "true" ]]; then
  if [[ -n "$previous_release" && -d "$previous_release" ]]; then
    ln -sfn "$previous_release" "$APP_ROOT/current.next"
    mv -Tf "$APP_ROOT/current.next" "$APP_ROOT/current"
    ln -sfn "$previous_release/frontend/dist" "$APP_ROOT/www/quant.next"
    mv -Tf "$APP_ROOT/www/quant.next" "$APP_ROOT/www/quant"
    systemctl restart ai-quant-api.service ai-quant-worker.service nginx.service
  fi
  echo "API health check failed; previous release restored." >&2
  exit 1
fi

find "$APP_ROOT/releases" -mindepth 1 -maxdepth 1 -type d -printf '%T@ %p\n' \
  | sort -nr | tail -n +6 | cut -d' ' -f2- | xargs -r rm -rf

echo "Deployment completed: $RELEASE_DIR"
