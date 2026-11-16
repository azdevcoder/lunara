# Lunara

App pessoal de ciclo, corpo e bem-estar — feito em Flask + MySQL, com interface em português e PWA instalável no celular.

## O que tem dentro

- **Hoje**: visão do ciclo, fase atual, previsões, humor, água, pílula e atalhos.
- **Calendário**: mês completo com período, janela fértil, ovulação e TPM.
- **Novo ciclo**: informe o primeiro dia, os dias de fluxo e a duração média; o calendário e as previsões são recalculados na hora.
- **Registro diário**: fluxo, sintomas, humor, energia, sono, água, peso, temperatura, relações, corrimento, desejos, exercício, medicação e notas.
- **Insights**: padrões de sintomas e humor, histórico de ciclos, médias e gráficos.
- **Gestação**: modo gestação, semana atual, tamanho do bebê e contagem regressiva.
- **Biblioteca**: artigos sobre ciclo, fertilidade, TPM, contracepção, gestação e bem-estar.
- **Perfil**: dados, ciclo, temas, lembretes, contraceptivo e exportação CSV/JSON.
- **PWA**: manifest, service worker, modo offline e ícones para instalar na tela inicial.

## Requisitos

- Python 3.10+ (testado com 3.10 e 3.14)
- MySQL 8+ rodando em `127.0.0.1:3306`

## Como rodar

```powershell
cd lunara
python -m pip install -r requirements.txt
python init_db.py
python run.py
```

Abra `http://localhost:5000`, crie sua conta e faça o onboarding.

O `init_db.py` cria o banco `lunara` com `utf8mb4` e todas as tabelas. Se o seu MySQL tiver senha, ajuste `DB_PASSWORD` no `.env`.

## Configuração

O arquivo `.env` é lido pelo `config.py`. Comece copiando o exemplo:

```bash
cp .env.example .env
```

```ini
SECRET_KEY=troque-esta-chave
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=lunara
DB_PASSWORD=troque-esta-senha
DB_NAME=lunara
```

Gere a `SECRET_KEY` com:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

O `.env` real nunca deve ser versionado no git. Mantenha permissão `600`.

Para desenvolvimento com recarga automática:

```powershell
$env:FLASK_DEBUG="1"
python run.py
```

## Instalar no celular (PWA)

O service worker só funciona em `localhost` ou em uma origem **HTTPS**.

Na mesma rede Wi-Fi, o celular consegue abrir `http://SEU-IP:5000`, mas o navegador não permitirá instalar o PWA nem registrar o service worker. Para testar a instalação de verdade, use um túnel HTTPS:

```powershell
# opção 1: cloudflared
cloudflared tunnel --url http://localhost:5000

# opção 2: ngrok
ngrok http 5000
```

Abra a URL HTTPS no celular:

- **Android/Chrome**: menu ⋮ → “Instalar app” (ou o botão “Instalar Lunara” no perfil).
- **iPhone/Safari**: botão Compartilhar → “Adicionar à Tela de Início”.

## Rodando em produção (Linux)

Produção usa `gunicorn` + `wsgi.py`, com HTTPS terminando no `tailscale serve`
(ou nginx, se preferir). O service worker e a instalação do PWA só funcionam em
HTTPS.

### 1. Preparar o app

```bash
sudo useradd --system --create-home --shell /usr/sbin/nologin lunara
sudo -u lunara git clone <repo> /home/lunara/app && cd /home/lunara/app
sudo -u lunara python3 -m venv .venv
sudo -u lunara .venv/bin/pip install -r requirements.txt
sudo -u lunara cp .env.example .env
sudo -u lunara chmod 600 .env
```

Preencha o `.env` com `SECRET_KEY` e credenciais do MySQL. Para produção via
proxy HTTPS, acrescente:

```ini
TRUST_PROXY=1
SESSION_COOKIE_SECURE=1
```

Crie o banco e as tabelas (a primeira vez precisa de um usuário MySQL com
permissão de `CREATE DATABASE`):

```bash
sudo -u lunara .venv/bin/python init_db.py
```

### 2. Serviço systemd

`/etc/systemd/system/lunara.service`:

```ini
[Unit]
Description=Lunara (gunicorn)
After=network.target mysql.service

[Service]
User=lunara
Group=lunara
WorkingDirectory=/home/lunara/app
ExecStart=/home/lunara/app/.venv/bin/gunicorn \
    --workers 2 \
    --bind 127.0.0.1:8000 \
    --access-logfile - \
    --error-logfile -
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now lunara
curl -s http://127.0.0.1:8000/healthz   # -> ok
```

O limite de tentativas de login é em memória, por worker. Com 2 workers o
limite efetivo é aproximado; para precisão estrita use `--workers 1` ou troque
o `AttemptTracker` por Redis.

### 3. HTTPS com Tailscale

Na máquina do servidor, com o Tailscale conectado:

```bash
sudo tailscale serve --bg 8000
sudo tailscale serve status
```

O app fica em `https://<nome-da-maquina>.<tailnet>.ts.net`, com certificado
válido — condição necessária para o PWA. Para desfazer: `sudo tailscale serve reset`.

Se preferir nginx na frente do gunicorn, aponte o `proxy_pass` para
`http://127.0.0.1:8000` e repasse `Host`, `X-Forwarded-For` e
`X-Forwarded-Proto`; mantenha `TRUST_PROXY=1`.

### 4. Atualizar

```bash
cd /home/lunara/app
sudo -u lunara git pull
sudo -u lunara .venv/bin/pip install -r requirements.txt
sudo systemctl restart lunara
```

## Estrutura

```
lunara/
├── app/
│   ├── __init__.py       # app factory, CSRF, filtros de data, /sw.js
│   ├── auth.py           # login, registro, logout
│   ├── content.py        # sintomas, humores, objetivos, artigos
│   ├── cycle.py          # motor de previsão do ciclo
│   ├── models.py         # User e DailyLog
│   ├── ratelimit.py      # limite de tentativas de login
│   ├── views.py          # rotas e regras de negócio
│   ├── static/
│   │   ├── css/          # base, pages, auth e app (agregador)
│   │   ├── js/app.js
│   │   ├── icons/
│   │   ├── manifest.webmanifest
│   │   └── sw.js
│   └── templates/
├── tools/make_icons.py   # regenera os ícones PNG
├── config.py
├── init_db.py
├── run.py
├── wsgi.py                # entrypoint do gunicorn
├── .env.example
└── requirements.txt
```

## Privacidade

Cada conta só enxerga os próprios registros. Os dados ficam no seu MySQL local; a exportação em CSV/JSON serve como backup. Este app é informativo e não substitui orientação médica.
