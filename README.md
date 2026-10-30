# Lunara

App pessoal de ciclo, corpo e bem-estar — feito em Flask + MySQL, com interface em português e PWA instalável no celular.

## O que tem dentro

- **Hoje**: visão do ciclo, fase atual, previsões, humor, água, pílula e atalhos.
- **Calendário**: mês completo com período, janela fértil, ovulação e TPM.
- **Registro diário**: fluxo, sintomas, humor, energia, sono, água, peso, temperatura, relações, corrimento, desejos, exercício, medicação e notas.
- **Insights**: padrões de sintomas e humor, histórico de ciclos, médias e gráficos.
- **Gestação**: modo gestação, semana atual, tamanho do bebê e contagem regressiva.
- **Biblioteca**: artigos sobre ciclo, fertilidade, TPM, contracepção, gestação e bem-estar.
- **Perfil**: dados, ciclo, temas, lembretes, contraceptivo e exportação CSV/JSON.
- **PWA**: manifest, service worker, modo offline e ícones para instalar na tela inicial.

## Requisitos

- Python 3.11+ (testado com 3.14)
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

O arquivo `.env` é lido pelo `config.py`:

```ini
SECRET_KEY=troque-esta-chave
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=lunara
```

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

## Estrutura

```
lunara/
├── app/
│   ├── __init__.py       # app factory, CSRF, filtros de data, /sw.js
│   ├── auth.py           # login, registro, logout
│   ├── content.py        # sintomas, humores, objetivos, artigos
│   ├── cycle.py          # motor de previsão do ciclo
│   ├── models.py         # User e DailyLog
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
└── requirements.txt
```

## Privacidade

Cada conta só enxerga os próprios registros. Os dados ficam no seu MySQL local; a exportação em CSV/JSON serve como backup. Este app é informativo e não substitui orientação médica.
