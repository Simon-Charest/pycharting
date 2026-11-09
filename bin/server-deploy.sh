#!/usr/bin/env bash
# bin/server-deploy.sh SERVICE [PORT]
# Runs on the server, inside the cloned repository (bin/deploy.ps1 calls it):
# installs what PyCharting needs, then installs and restarts its systemd service.
set -euo pipefail
service="${1:-pycharting.service}"
port="${2:-8000}"
cd "$(dirname "$0")/.."
dir="$(pwd)"

# bin/deploy.ps1 sends the sudo password on the first input line; without it, sudo asks as usual
password=""

if [ ! -t 0 ]; then
    IFS= read -r password || true
fi

run_sudo() {
    if [ -n "$password" ]; then
        printf '%s\n' "$password" | sudo -S -p "" "$@"
    else
        sudo "$@"
    fi
}

# Python's venv module is a separate package on Ubuntu
if ! python3 -c "import ensurepip" 2>/dev/null; then
    echo "Installing python3-venv..."
    run_sudo env DEBIAN_FRONTEND=noninteractive apt-get install -y python3-venv
fi

if [ ! -x .venv/bin/python ]; then
    python3 -m venv .venv
fi

.venv/bin/python -m pip install --quiet --upgrade pip
.venv/bin/python -m pip install --quiet -r requirements.txt

# The settings and the database are never in Git: they are copied by hand, once
database="$(grep -E '^DATABASE_FILE=' .env 2>/dev/null | cut -d= -f2- | tr -d '\r' || true)"
missing=0
[ -f .env ] || { echo "Missing: $dir/.env (copy the one from your PC)"; missing=1; }
[ -f "${database:-data/database.sqlite}" ] || { echo "Missing: $dir/${database:-data/database.sqlite} (copy the database from your PC)"; missing=1; }
[ "$missing" = 0 ] || exit 1

unit="$(mktemp)"
sed -e "s|@USER@|$(id -un)|g" -e "s|@DIR@|$dir|g" -e "s|@PORT@|$port|g" bin/pycharting.service > "$unit"
run_sudo install -m 644 "$unit" "/etc/systemd/system/$service"
rm -f "$unit"
run_sudo systemctl daemon-reload
run_sudo systemctl enable --quiet "$service"
run_sudo systemctl restart "$service"

for _ in $(seq 1 15); do
    if .venv/bin/python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:$port/health', timeout=2)" 2>/dev/null; then
        echo "$service is running on 127.0.0.1:$port"
        exit 0
    fi

    sleep 1
done

echo "$service did not answer on 127.0.0.1:$port. Recent logs:"
run_sudo journalctl -u "$service" -n 30 --no-pager
exit 1
