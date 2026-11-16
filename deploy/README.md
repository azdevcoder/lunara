# Deploy do Lunara

Alvo: `https://lunara.azdevcoder.com.br` → Cloudflare Tunnel → `gunicorn` em
`127.0.0.1:8000` no servidor.

## 1. No servidor (Linux Debian/Ubuntu)

Pré-requisitos: MySQL/MariaDB instalado e ativo, acesso root ao MySQL via
`sudo mysql` (ou informe `MYSQL_ROOT_PASSWORD`).

```bash
git clone https://github.com/azdevcoder/lunara.git
cd lunara
sudo TUNNEL_TOKEN="<token do túnel>" bash deploy/setup.sh
```

O script:

- cria o usuário `lunara`, baixa o código em `/opt/lunara`;
- gera `.env` com senha aleatória para o MySQL e `SECRET_KEY`;
- cria banco e usuário `lunara` no MySQL, roda `init_db.py`;
- instala dependências em `.venv` e o serviço `lunara.service` (gunicorn);
- instala o `cloudflared` e registra o conector com o token informado;
- valida `http://127.0.0.1:8000/healthz`.

Variáveis aceitas: `APP_DIR`, `APP_USER`, `PORT`, `REPO_URL`, `BRANCH`,
`DB_NAME`, `DB_USER`, `TUNNEL_TOKEN`, `MYSQL_ROOT_PASSWORD`.

## 2. No painel Cloudflare (obrigatório)

O token apenas conecta o túnel; a rota pública é configurada no painel:

1. Zero Trust → Networks → Tunnels → selecione o túnel.
2. Public Hostname → Add a public hostname.
3. Subdomain: `lunara` · Domain: `azdevcoder.com.br`
4. Service: `HTTP` · URL: `localhost:8000`
5. Salve e aguarde o DNS propagar.

Teste:

```bash
curl -s https://lunara.azdevcoder.com.br/healthz   # ok
```

## 3. Atualizar

```bash
cd /opt/lunara
sudo -u lunara git pull
sudo -u lunara .venv/bin/pip install -r requirements.txt
sudo systemctl restart lunara
```

## Observações

- `TRUST_PROXY=1` e `SESSION_COOKIE_SECURE=1` já vêm no `.env` gerado. Login só
  funciona em HTTPS (pelo domínio público), não por `http://IP:8000`.
- O limitador de login é em memória por worker (2 workers). Para limite exato,
  use `--workers 1` em `deploy/lunara.service`.
- Faça backup do MySQL (`mysqldump lunara`) antes de atualizações grandes.
- Se o servidor for Windows, este kit não se aplica: usar Waitress + NSSM e o
  `cloudflared.exe service install <token>`.
