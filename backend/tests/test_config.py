from app.core.config import DEFAULT_STOCK_NAMES, DEFAULT_WATCHLIST, Settings


def test_default_watchlist_contains_fifteen_diversified_stocks() -> None:
    settings = Settings(
        database_url="sqlite://",
        llm_enabled=False,
        credentials_file="missing.ini",
        default_watchlist=DEFAULT_WATCHLIST,
    )

    assert len(settings.watchlist) == 15
    assert len(set(settings.watchlist)) == 15
    assert {"000001", "300750", "600519", "601899"} <= set(settings.watchlist)
    assert set(settings.watchlist) == set(DEFAULT_STOCK_NAMES)
    assert settings.llm_model == "deepseek-v4-pro"


def test_tushare_token_supports_project_and_shared_scoped_credentials(tmp_path) -> None:
    local = tmp_path / "local.ini"
    local.write_text("[tushare]\ntoken=local-token\n", encoding="utf-8")
    shared = tmp_path / "shared.ini"
    shared.write_text("[quant.tushare]\ntoken=shared-token\n", encoding="utf-8")

    local_settings = Settings(database_url="sqlite://", credentials_file=str(local))
    shared_settings = Settings(database_url="sqlite://", credentials_file=str(shared))

    assert local_settings.tushare_token == "local-token"
    assert shared_settings.tushare_token == "shared-token"
