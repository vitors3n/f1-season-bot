# F1 Season Bot

Bot do Telegram para acompanhar a temporada de Fórmula 1: próxima corrida, calendário, classificações, previsão do tempo e lembretes das sessões.

Os dados esportivos são consultados na [Jolpica F1 API](https://jolpi.ca/) e os horários são convertidos para o fuso configurado — por padrão, Fortaleza (CE).

## Início rápido

Você precisa apenas de um token de bot do Telegram e de Python 3.10 ou superior.

1. Crie um bot conversando com [@BotFather](https://t.me/BotFather) no Telegram e copie o token fornecido.
2. Clone o repositório e entre na pasta do projeto:

   ```bash
   git clone https://github.com/vitors3n/f1-season-bot.git
   cd f1-season-bot
   ```

3. Crie o arquivo de configuração a partir do exemplo:

   ```bash
   cp .env.example .env
   ```

   No Windows PowerShell, use:

   ```powershell
   Copy-Item .env.example .env
   ```

4. Abra `.env` e preencha somente o token:

   ```env
   BOT_TOKEN=cole_o_token_aqui
   ```

5. Crie um ambiente virtual, instale as dependências e inicie o bot:

   ```bash
   python -m venv .venv
   ```

   Windows PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python bot.py
   ```

   Linux/macOS:

   ```bash
   source .venv/bin/activate
   pip install -r requirements.txt
   python bot.py
   ```

6. Abra uma conversa com o bot no Telegram e envie `/start`.

> Nunca envie o arquivo `.env` ao Git. Ele já está listado no `.gitignore`.

## Executar com Docker

O Compose usa volumes para preservar o banco de lembretes e o cache entre atualizações. Antes de iniciar, ajuste os caminhos do host em `docker/docker-compose.yml` caso o servidor não use `/projetos/f1bot`.

Com `.env` configurado na raiz do projeto, execute:

```bash
docker compose --env-file .env -f docker/docker-compose.yml up -d --build
```

Para acompanhar os logs:

```bash
docker compose -f docker/docker-compose.yml logs -f f1bot
```

Para parar o bot:

```bash
docker compose -f docker/docker-compose.yml stop f1bot
```

## Comandos

| Comando | Descrição |
| --- | --- |
| `/next` | Próxima corrida e programação do fim de semana. |
| `/countdown` | Tempo restante para a próxima sessão. |
| `/calendar` | Calendário da temporada atual. |
| `/qualifying` | Resultado da última classificação. |
| `/weather` | Previsão para as próximas sessões do GP. |
| `/drivers` | Classificação dos pilotos. |
| `/teams` | Classificação dos construtores. |
| `/notify` | Ativa lembretes para o próximo GP. |
| `/listnotify` | Lista os lembretes deste chat. |
| `/clearnotify` | Remove os lembretes deste chat. |
| `/help` | Lista todos os comandos. |
| `/about` | Informações sobre o bot. |

## Configuração

As opções são carregadas de `.env`; valores não definidos usam os padrões de `config.py`.

| Variável | Padrão | Finalidade |
| --- | --- | --- |
| `BOT_TOKEN` | — | Token do bot. Obrigatório. |
| `DEFAULT_TIMEZONE` | `America/Fortaleza` | Fuso usado para horários e agendamento. |
| `TIMEZONE_LABEL` | `Fortaleza (CE)` | Nome apresentado nas mensagens. |
| `DATABASE_URL` | `sqlite:///data/lembretes.sqlite` | Banco dos lembretes do APScheduler. |
| `CACHE_DIRECTORY` | `jolpi_cache` | Diretório do cache das APIs. |
| `REQUEST_TIMEOUT` | `15` | Tempo máximo de espera por uma API, em segundos. |
| `REMINDER_MINUTES` | `10,5` | Minutos de antecedência dos lembretes. |
| `LOG_LEVEL` | `INFO` | Nível dos logs da aplicação. |

Os tempos de cache também podem ser configurados pelas variáveis `CACHE_TTL_*`; consulte `.env.example` para a lista completa.

## Estrutura do projeto

```text
├── bot.py                 # Ponto de entrada e registro dos comandos
├── config.py              # Leitura das configurações
├── comandos/              # Handlers e formatação das mensagens
├── modelos/               # Modelos de corrida e eventos
├── servicos/              # Integrações com APIs, cache e dados
├── data/                  # Banco SQLite dos lembretes (criado em execução)
├── docker/                # Dockerfile e Docker Compose
└── .github/workflows/     # Workflow de deploy
```

## Solução de problemas

- `ModuleNotFoundError: No module named 'config'`: reconstrua a imagem Docker usando `--build`.
- Bot não inicia: confirme que `BOT_TOKEN` está preenchido no `.env` ou nas variáveis de ambiente do container.
- Erro ao criar lembretes no Docker: confirme que os diretórios montados em `data` e `jolpi_cache` existem e permitem escrita para o container.
- Dados indisponíveis: a Jolpica ou a Open-Meteo podem estar temporariamente indisponíveis; tente novamente em alguns minutos.

## Contribuição

Contribuições são bem-vindas. Faça um fork, crie uma branch para a alteração e envie um pull request.

## Licença

Este projeto é licenciado sob os termos da [GNU GPLv3](LICENSE).
