#!/usr/bin/env bash
set -euo pipefail

action="${1:-status}"
services=(ai-quant-api.service ai-quant-worker.service nginx.service)

case "$action" in
  start)
    systemctl enable --now ai-quant-cert-renew.timer
    systemctl start "${services[@]}"
    ;;
  restart)
    systemctl restart "${services[@]}"
    systemctl restart ai-quant-cert-renew.timer
    ;;
  stop)
    systemctl stop ai-quant-api.service ai-quant-worker.service nginx.service
    systemctl stop ai-quant-cert-renew.timer
    ;;
  status)
    systemctl --no-pager --full status "${services[@]}" || true
    ;;
  resources)
    systemctl show ai-quant-api.service ai-quant-worker.service nginx.service \
      --property=Id,ActiveState,SubState,MemoryCurrent,MemoryPeak,CPUUsageNSec
    free -h
    ;;
  *)
    echo "Usage: $0 {start|restart|stop|status|resources}" >&2
    exit 2
    ;;
esac
