# F1 Season Bot

Bot em Python que envia notificações para um grupo no Telegram sobre eventos da F1, incluindo treinos livres (FP), classificação (Quali), sprint e corridas.

### Tecnologias e Ferramentas Utilizadas
- `python-telegram-bot` — para interação com o Telegram  
- `APScheduler` — agendamento de notificações  
- `jolpica-f1 api` — fonte de dados sobre os eventos da F1  
- Cache em **SQLite** para reduzir consultas repetidas à API  
- Revisão de código com **SonarCloud**  

---

## Índice
1. [Pré-requisitos](#pré-requisitos)  
2. [Instalação](#instalação)  
3. [Configuração](#configuração)  
4. [Execução](#execução)  
5. [Personalização](#personalização)  
6. [Arquitetura do projeto](#arquitetura-do-projeto)  
7. [Contribuição](#contribuição)  
8. [Licença](#licença)  

---

## Pré-requisitos
- Python 3.10+  
- Acesso a um bot no Telegram (token)  
- Acesso à `jolpica-f1 api`

---

## Instalação

Clone o repositório e instale as dependências:

```bash
    git clone https://github.com/vitors3n/f1-season-bot.git
    cd f1-season-bot
    python -m venv venv
    source venv/bin/activate   # (Windows: venv\Scripts\activate)
    pip install -r requirements.txt
```
---

## Configuração

1. Crie um bot no Telegram e obtenha o `BOT_TOKEN`.  
2. Se necessário, configure acesso à API `jolpica-f1`.  
3. Configure os parâmetros (bot token, grupo/ID de chat, endpoints da API) no arquivo `config.py`, variável de ambiente ou outro método implementado.  
4. Opcional: revise ou personalize o cache SQLite (`cache.db`) no diretório do projeto.

---

## Execução

Para rodar o bot:

```
    python bot.py
```

O bot iniciará e começará a enviar notificações conforme as configurações agendadas.

---

## Personalização

- **Agendamento:** ajuste os horários de notificações diretamente no código (via `APScheduler`).  
- **Mensagens:** personalize o texto das notificações (como “FP começa em ...”, formatação, emojis, etc.).  
- **Novas funcionalidades:** crie comandos adicionais, filtros por piloto/equipe ou integração com outras APIs.

---

## Arquitetura do Projeto

```
├── bot.py # Ponto de entrada do bot
├── requirements.txt # Dependências do Python
├── comandos/ # Scripts ou módulos de comandos F1
├── modelos/ # Modelos de dados (ex: classes ou schemas)
├── utils/ # Funções e utilitários
├── docker/ # Configurações para execução via Docker
├── .github/workflows/ # Pipelines (CI/CD, SonarCloud, etc.)
└── README.md # Este documento
```

---

## Contribuição

Contribuições são bem-vindas! Sugestões de melhorias, correção de bugs, novas funções ou tradução do README são super bem-vindas. Faça um fork, crie uma branch feature/nova-funcionalidade e envie um pull request.

---

## Licença

Este projeto é licenciado sob os termos da [GNU GPLv3](LICENSE).
