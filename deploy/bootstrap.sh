#!/usr/bin/env bash
# One-shot setup of a fresh Ubuntu 22.04/24.04 VPS for compound.ie.
# Run as root:  bash bootstrap.sh https://github.com/<you>/compound.git [branch]
# Installs Python, git, Caddy and Claude Code; creates the `compound` user; clones the repo into
# /srv/compound; builds the venv; installs the systemd unit and Caddyfile. It does NOT start the bot:
# you log Claude Code in and fill .env first (the script prints the exact steps at the end).
set -euo pipefail

REPO="${1:?usage: bootstrap.sh <git-url> [branch]}"
BRANCH="${2:-main}"
HOME_DIR=/srv/compound

echo "== packages"
export DEBIAN_FRONTEND=noninteractive
apt-get update -q
apt-get install -y -q python3 python3-venv python3-pip git curl ca-certificates \
    debian-keyring debian-archive-keyring apt-transport-https gnupg

if ! command -v caddy >/dev/null; then
  echo "== caddy"
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' > /etc/apt/sources.list.d/caddy-stable.list
  apt-get update -q && apt-get install -y -q caddy
fi

echo "== user"
id compound >/dev/null 2>&1 || useradd -r -m -d "$HOME_DIR" -s /bin/bash compound

echo "== repo"
if [ ! -d "$HOME_DIR/.git" ]; then
  sudo -u compound git clone -b "$BRANCH" "$REPO" "$HOME_DIR"
else
  sudo -u compound git -C "$HOME_DIR" pull --ff-only
fi

echo "== python"
[ -x "$HOME_DIR/.venv/bin/python" ] || sudo -u compound python3 -m venv "$HOME_DIR/.venv"
sudo -u compound "$HOME_DIR/.venv/bin/pip" install -q -e "$HOME_DIR"

echo "== claude code (for the compound user; billed to the subscription you log in with)"
sudo -u compound -H bash -c 'command -v ~/.local/bin/claude >/dev/null || curl -fsSL https://claude.ai/install.sh | bash'

echo "== config"
if [ ! -f "$HOME_DIR/.env" ]; then
  sudo -u compound cp "$HOME_DIR/.env.example" "$HOME_DIR/.env"
  sudo -u compound sed -i \
    -e 's|^LLM_BACKEND=.*|LLM_BACKEND=claude-code|' \
    -e "s|^CLAUDE_CODE_BIN=.*|CLAUDE_CODE_BIN=$HOME_DIR/.local/bin/claude|" \
    -e 's|^SITE_BASE_URL=.*|SITE_BASE_URL=https://compound.ie|' \
    -e 's|^PREVIEW_BASE_URL=.*|PREVIEW_BASE_URL=https://compound.ie|' \
    "$HOME_DIR/.env"
fi
mkdir -p "$HOME_DIR/public" && chown compound:compound "$HOME_DIR/public"

echo "== services"
cp "$HOME_DIR/deploy/compound.service" /etc/systemd/system/compound.service
cp "$HOME_DIR/deploy/Caddyfile" /etc/caddy/Caddyfile
systemctl daemon-reload
systemctl enable --now caddy
systemctl reload caddy || true

cat <<MSG

Done. Three things left, in order:

1. Log Claude Code in as the compound user (opens a URL to paste into any browser; pick the
   subscription login):
     sudo -u compound -H $HOME_DIR/.local/bin/claude
   then type /exit.

2. Put your Telegram token and owner id in $HOME_DIR/.env (copy them from the PC's .env), and
   set INTERVIEW, MIN_RELEVANCE, SCHEDULE_HOURS and AUTO_PUBLISH the way you want them:
     sudo -u compound nano $HOME_DIR/.env

3. Start the bot and watch its log:
     systemctl enable --now compound && journalctl -u compound -f

Point compound.ie and www.compound.ie A records at this server's IP; Caddy fetches HTTPS
certificates automatically once DNS resolves.
MSG
