from html import escape


MENSAGEM_INICIAL = """🏎️ <b>Bem-vindo ao F1 Season Bot!</b>

Acompanhe a temporada de Fórmula 1 diretamente pelo Telegram.

<b>Comandos disponíveis:</b>
/next — Próxima corrida e horários
/drivers — Classificação dos pilotos
/teams — Classificação dos construtores
/notify — Ativar lembretes da próxima corrida
/listnotify — Consultar lembretes ativos"""

ERRO_CONSULTA = "⚠️ Não foi possível consultar os dados da Fórmula 1 agora. Tente novamente mais tarde."
NAO_AUTORIZADO = "⛔ Você não tem permissão para executar este comando."
NOTIFICACOES_REMOVIDAS = "🔕 Todas as notificações foram removidas."


def _horario(evento):
    return evento.dia_hora().replace(", ", " às ")


def proxima_corrida(corrida):
    programacao = [f"• <b>Treino Livre 1:</b> {_horario(corrida.fp1)}"]
    if corrida.sprint:
        programacao.extend([
            f"• <b>Classificação Sprint:</b> {_horario(corrida.sprint_quali)}",
            f"• <b>Corrida Sprint:</b> {_horario(corrida.sprint)}",
        ])
    else:
        programacao.extend([
            f"• <b>Treino Livre 2:</b> {_horario(corrida.fp2)}",
            f"• <b>Treino Livre 3:</b> {_horario(corrida.fp3)}",
        ])
    programacao.extend([
        f"• <b>Classificação:</b> {_horario(corrida.quali)}",
        f"• <b>Corrida:</b> {_horario(corrida)}",
    ])
    programacao_formatada = "\n".join(programacao)
    return (
        f"🏁 <b>{escape(corrida.nome)}</b>\n"
        f"📍 {escape(corrida.circuito)}\n\n"
        f"<b>Programação:</b>\n{programacao_formatada}"
    )


def classificacao_pilotos(pilotos, ano):
    linhas = [f"🏆 <b>Campeonato de Pilotos — {ano}</b>", ""]
    for piloto in pilotos:
        dados = piloto['Driver']
        nome = escape(f"{dados['givenName']} {dados['familyName']}")
        linhas.append(f"{piloto['position']}. {nome} — {piloto['points']} pts")
    return "\n".join(linhas)


def classificacao_construtores(times, ano):
    linhas = [f"🏆 <b>Campeonato de Construtores — {ano}</b>", ""]
    for time in times:
        nome = escape(time['Constructor']['name'])
        linhas.append(f"{time['position']}. {nome} — {time['points']} pts")
    return "\n".join(linhas)


def lembrete(evento_nome, minutos):
    return f"⏰ <b>Faltam {minutos} minutos!</b>\n\n{escape(evento_nome)} começa em breve."


def notificacoes_ativadas(corrida_nome):
    return (
        "🔔 <b>Notificações ativadas!</b>\n\n"
        f"Você receberá lembretes dos eventos de {escape(corrida_nome)}."
    )


def lista_notificacoes(nomes):
    if not nomes:
        return "🔕 Nenhuma notificação está ativa neste chat."
    itens = "\n".join(f"• {escape(nome)}" for nome in nomes)
    return f"🔔 <b>Notificações ativas neste chat:</b>\n\n{itens}"
