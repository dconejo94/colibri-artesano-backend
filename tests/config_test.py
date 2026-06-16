from app.config import Settings


def test_allowed_origins_default_is_usable_list(monkeypatch):
    # Regression: the default must be a valid list[str] so that Settings()
    # can be instantiated without ALLOWED_ORIGINS being supplied by the env.
    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
    # JWT_SECRET_KEY is required (no default), so supply one for this check.
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret")

    settings = Settings(_env_file=None)

    assert isinstance(settings.ALLOWED_ORIGINS, list)
    assert settings.ALLOWED_ORIGINS == ["http://localhost:8081"]
