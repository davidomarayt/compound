from pathlib import Path

from compound.setup import read_env, write_env


def test_write_env_keeps_template_layout_and_existing_values(tmp_path: Path):
    template = tmp_path / ".env.example"
    template.write_text("# Telegram\nTELEGRAM_BOT_TOKEN=\nTELEGRAM_OWNER_ID=\nPOLL_INTERVAL_MINUTES=30\n")
    env = tmp_path / ".env"
    write_env(env, {"TELEGRAM_BOT_TOKEN": "123:abc"}, template)
    assert read_env(env) == {"TELEGRAM_BOT_TOKEN": "123:abc", "TELEGRAM_OWNER_ID": "", "POLL_INTERVAL_MINUTES": "30"}
    write_env(env, {"TELEGRAM_OWNER_ID": "42", "EXTRA": "x"}, template)
    text = env.read_text()
    assert text.startswith("# Telegram\nTELEGRAM_BOT_TOKEN=123:abc\nTELEGRAM_OWNER_ID=42\n")
    assert "EXTRA=x" in text
