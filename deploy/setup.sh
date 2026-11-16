#!/usr/bin/env bash
# Instala/atualiza o Lunara em um servidor Linux (Debian/Ubuntu).
#
# Uso:
#   sudo APP_DIR=/opt/lunara bash deploy/setup.sh
#   sudo TUNNEL_TOKEN="<token do túnel>" bash deploy/setup.sh
#
# Requisitos: MySQL/MariaDB rodando, acesso root via `mysql` (unix_socket)
# para criar o banco. Se o root do MySQL tiver senha, exporte MYSQL_ROOT_PASSWORD.
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/lunara}"
APP_USER="${APP_USER:-lunara}"
PORT="${PORT:-8000}"
REPO_URL="${REPO_URL:-https://github.com/azdevcoder/lunara.git}"
BRANCH="${BRANCH:-main}"
DB_NAME="${DB_NAME:-lunara}"
DB_USER="${DB_USER:-lunara}"
TUNNEL_TOKEN="${TUNNEL_TOKEN:-}"
MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD:-}"

if [ "$(id -u)" -ne 0 ]; then
  echo "Rode com sudo." >&2
  exit 1
fi

mysql_root() {
  if [ -n "$MYSQL_ROOT_PASSWORD" ]; then
    mysql -uroot -p"$MYSQL_ROOT_PASSWORD" "$@"
  else
    mysql -uroot "$@"
  fi
}

echo "==> Pacotes base"
apt-get update
apt-get install -y python3 python3-venv python3-pip git curl ca-certificates
apt-get install -y default-mysql-client || apt-get install -y mysql-client

if ! systemctl is-active --quiet mysql && ! systemctl is-active --quiet mariadb; then
  echo "MySQL/MariaDB não está ativo. Instale e inicie antes de continuar." >&2
  exit 1
fi

echo "==> Usuário do app"
if ! id -u "$APP_USER" >/dev/null 2>&1; then
  useradd --system --create-home --home-dir "/home/$APP_USER" --shell /usr/sbin/nologin "$APP_USER"
fi

echo "==> Código"
if [ -d "$APP_DIR/.git" ]; then
  sudo -u "$APP_USER" git -C "$APP_DIR" fetch origin "$BRANCH"
  sudo -u "$APP_USER" git -C "$APP_DIR" reset --hard "origin/$BRANCH"
else
  mkdir -p "$APP_DIR"
  chown "$APP_USER:$APP_USER" "$APP_DIR"
  sudo -u "$APP_USER" git clone --branch "$BRANCH" "$REPO_URL" "$APP_DIR"
fi

echo "==> .env e banco"
if [ ! -f "$APP_DIR/.env" ]; then
  DB_PASS="$(python3 -c 'import secrets; print(secrets.token_urlsafe(24))')"
  SECRET="$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')"

  mysql_root -e "CREATE DATABASE IF NOT EXISTS \`$DB_NAME\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
  mysql_root -e "CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS'; ALTER USER '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS'; GRANT ALL PRIVILEGES ON \`$DB_NAME\`.* TO '$DB_USER'@'localhost'; FLUSH PRIVILEGES;"

  umask 077
  cat > "$APP_DIR/.env" <<EOF
SECRET_KEY=$SECRET
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASS
DB_NAME=$DB_NAME
TRUST_PROXY=1
SESSION_COOKIE_SECURE=1
EOF
  chown "$APP_USER:$APP_USER" "$APP_DIR/.env"
  chmod 600 "$APP_DIR/.env"
  echo "    .env criado com senha aleatória."
else
  echo "    .env existente mantido."
fi

echo "==> Ambiente Python"
sudo -u "$APP_USER" python3 -m venv "$APP_DIR/.venv"
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/pip" install --quiet --upgrade pip
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/pip" install --quiet -r "$APP_DIR/requirements.txt"

echo "==> Tabelas"
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/python" "$APP_DIR/init_db.py"

echo "==> Serviço systemd"
sed "s|/opt/lunara|$APP_DIR|g; s|127.0.0.1:8000|127.0.0.1:$PORT|g" \
  "$APP_DIR/deploy/lunara.service" > /etc/systemd/system/lunara.service
systemctl daemon-reload
systemctl enable --now lunara
systemctl restart lunara

echo "==> Cloudflare Tunnel"
if [ -n "$TUNNEL_TOKEN" ]; then
  if ! command -v cloudflared >/dev/null 2>&1; then
    install -d -m 0755 /usr/share/keyrings
    curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg -o /usr/share/keyrings/cloudflare-main.gpg
    echo "deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared any main" \
      > /etc/apt/sources.list.d/cloudflared.list
    apt-get update
    apt-get install -y cloudflared
  fi
  cloudflared service install "$TUNNEL_TOKEN" >/dev/null
  systemctl enable --now cloudflared
  systemctl restart cloudflared
else
  echo "    TUNNEL_TOKEN não informado. Instale o conector depois com:"
  echo "    sudo cloudflared service install <TOKEN>"
fi

echo "==> Verificação"
for _ in $(seq 1 15); do
  if curl -fsS "http://127.0.0.1:$PORT/healthz" >/dev/null 2>&1; then
    echo "    http://127.0.0.1:$PORT/healthz -> ok"
    break
  fi
  sleep 1
done

systemctl --no-pager --lines=0 status lunara | head -5 || true
if command -v cloudflared >/dev/null 2>&1; then
  systemctl --no-pager --lines=0 status cloudflared | head -5 || true
fi

cat <<EOF

Deploy concluído.

Falta no painel Cloudflare Zero Trust:
  Networks > Tunnels > seu túnel > Public Hostname
  Subdomain: lunara
  Domain: azdevcoder.com.br
  Service: http://localhost:$PORT

Depois teste: https://lunara.azdevcoder.com.br/healthz
EOF
