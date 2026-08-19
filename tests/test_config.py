from pathlib import Path
from wp_ai_publisher.config import load_config
def test_env_overrides_local(monkeypatch):
    tmp_path = Path(".test-artifacts/config"); tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "sites.yaml").write_text('sites:\n- id: one\n  base_url: https://one.example\n')
    (tmp_path / "settings.yaml").write_text('{}')
    (tmp_path / "sites.local.yaml").write_text('credentials:\n  one: {username: local, app_password: localpass}\n')
    monkeypatch.setenv("WP_ONE_USERNAME", "env")
    assert load_config(tmp_path).site("one").credentials.username == "env"
