from datetime import datetime
from html import escape

from config import TIMEZONE_LABEL
from modelos.corrida import corrigir_timezone


MENSAGEM_INICIAL = """🏎️ <b>Bem-vindo ao F1 Season Bot!</b>

Acompanhe a temporada de Fórmula 1 diretamente pelo Telegram.

<b>Comandos disponíveis:</b>
/next — Próxima corrida e horários
/countdown — Contagem regressiva para a próxima sessão
/calendar — Calendário da temporada
/qualifying — Resultado da última classificação
/weather — Previsão do tempo para o próximo GP
/drivers — Classificação dos pilotos
/teams — Classificação dos construtores
/notify — Ativar lembretes da próxima corrida
/listnotify — Consultar lembretes ativos
/settings — Configurar lembretes deste chat
/help — Ver ajuda e todos os comandos
/about — Sobre o bot"""

AJUDA = f"""🏎️ <b>Ajuda — F1 Season Bot</b>

<b>Corridas</b>
/next — Exibe a próxima corrida e a programação do fim de semana.
/countdown — Mostra quanto falta para a próxima sessão.
/calendar — Lista as corridas da temporada atual.
/qualifying — Mostra o resultado da última classificação.
/weather — Mostra a previsão do tempo para as sessões do próximo GP.

<b>Campeonato</b>
/drivers — Mostra a classificação dos pilotos.
/teams — Mostra a classificação dos construtores.

<b>Notificações</b>
/notify — Ativa lembretes para as sessões da próxima corrida.
/listnotify — Lista os lembretes ativos neste chat.
/clearnotify — Remove os lembretes deste chat (administradores em grupos).
/settings — Configura os lembretes deste chat (administradores em grupos).

<b>Outros</b>
/start — Exibe a mensagem inicial.
/about — Mostra informações sobre o bot.
/help — Exibe esta ajuda.

🕒 Os horários são exibidos no fuso de {TIMEZONE_LABEL}."""

SOBRE_O_BOT = f"""🏎️ <b>Sobre o F1 Season Bot</b>

Este bot ajuda você a acompanhar a temporada de Fórmula 1 pelo Telegram, com calendário, classificação, programação, contagem regressiva e lembretes das sessões.

🕒 Todos os horários são exibidos no fuso de {TIMEZONE_LABEL}.
📊 Os dados são fornecidos pela <a href="https://jolpi.ca/">Jolpica F1 API</a>.
💻 Projeto desenvolvido em Python com código disponível no <a href="https://github.com/vitors3n/f1-season-bot">GitHub</a>.

Este é um projeto independente e não possui vínculo oficial com a Fórmula 1."""

ERRO_CONSULTA = "⚠️ Não foi possível consultar os dados da Fórmula 1 agora. Tente novamente mais tarde."
NAO_AUTORIZADO = "⛔ Você não tem permissão para executar este comando."
NOTIFICACOES_REMOVIDAS = "🔕 Todas as notificações foram removidas."
PREVISAO_INDISPONIVEL = "🌦️ A previsão para o próximo GP ainda não está disponível. Tente novamente quando o evento estiver mais próximo."
HORARIOS_INDEFINIDOS = "🕒 Os horários das sessões da próxima corrida ainda não foram definidos."


def _horario(evento):
    if not evento.tem_horario:
        return evento.dia_hora()

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


def contagem_regressiva(corrida_nome, evento_nome, dia_hora, agora):
    segundos = max(0, int((dia_hora - agora).total_seconds()))
    minutos_totais = (segundos + 59) // 60
    dias, minutos_restantes = divmod(minutos_totais, 24 * 60)
    horas, minutos = divmod(minutos_restantes, 60)

    partes = []
    if dias:
        partes.append(f"{dias} dia{'s' if dias != 1 else ''}")
    if horas:
        partes.append(f"{horas} hora{'s' if horas != 1 else ''}")
    if minutos or not partes:
        partes.append(f"{minutos} minuto{'s' if minutos != 1 else ''}")

    tempo = ", ".join(partes)
    horario = dia_hora.strftime("%d/%m/%Y às %H:%M")
    return (
        f"⏳ <b>Faltam {tempo}</b>\n\n"
        f"🏁 {escape(corrida_nome)}\n"
        f"📌 {escape(evento_nome)}\n"
        f"🕒 {horario}"
    )


def nenhum_evento_futuro(corrida_nome):
    return f"🏁 Não há mais sessões futuras em <b>{escape(corrida_nome)}</b>."


def calendario_temporada(corridas, ano, pagina=1, total_paginas=1):
    dias_da_semana = (
        "segunda-feira",
        "terça-feira",
        "quarta-feira",
        "quinta-feira",
        "sexta-feira",
        "sábado",
        "domingo",
    )
    titulo = f"🗓 <b>Calendário da Fórmula 1 — {ano}</b>"
    if total_paginas > 1:
        titulo += f"\nPágina {pagina} de {total_paginas}"
    linhas = [titulo, ""]

    for corrida in corridas:
        nome = escape(corrida["raceName"])
        if corrida.get("time"):
            dia_hora = corrigir_timezone(corrida["date"], corrida["time"])
            dia_da_semana = dias_da_semana[dia_hora.weekday()]
            data_formatada = dia_hora.strftime("%d/%m às %H:%M")
        else:
            dia = datetime.strptime(corrida["date"], "%Y-%m-%d")
            dia_da_semana = dias_da_semana[dia.weekday()]
            data_formatada = f'{dia.strftime("%d/%m")} (horário a definir)'

        linhas.append(
            f'<b>{corrida["round"]}. {nome}</b> — '
            f"{dia_da_semana}, {data_formatada}"
        )

    linhas.extend(["", f"🕒 Horários de {TIMEZONE_LABEL}"])
    return "\n".join(linhas)


def resultado_classificacao(corrida):
    nome_corrida = escape(corrida["raceName"])
    circuito = escape(corrida["Circuit"]["circuitName"])
    linhas = [
        "🏁 <b>Resultado da última classificação</b>",
        f"🏆 {nome_corrida}",
        f"📍 {circuito}",
        "",
    ]

    for resultado in corrida["QualifyingResults"]:
        piloto = resultado["Driver"]
        nome_piloto = escape(f'{piloto["givenName"]} {piloto["familyName"]}')
        codigo = escape(piloto.get("code") or resultado["number"])
        equipe = escape(resultado["Constructor"]["name"])

        sessao = next(
            (nome for nome in ("Q3", "Q2", "Q1") if resultado.get(nome)),
            None,
        )
        tempo = f" — {sessao}: {resultado[sessao]}" if sessao else ""
        linhas.append(
            f'<b>{resultado["position"]}. {codigo}</b> — '
            f"{nome_piloto} ({equipe}){tempo}"
        )

    return "\n".join(linhas)


def _descricao_tempo(codigo):
    if codigo == 0:
        return "☀️ Céu limpo"
    if codigo in (1, 2, 3):
        return "⛅ Parcialmente nublado"
    if codigo in (45, 48):
        return "🌫️ Nevoeiro"
    if codigo in (51, 53, 55, 56, 57):
        return "🌦️ Garoa"
    if codigo in (61, 63, 65, 66, 67):
        return "🌧️ Chuva"
    if codigo in (71, 73, 75, 77, 85, 86):
        return "🌨️ Neve"
    if codigo in (80, 81, 82):
        return "🌦️ Pancadas de chuva"
    if codigo in (95, 96, 99):
        return "⛈️ Trovoadas"
    return "🌡️ Condição variável"


def previsao_tempo(corrida_nome, circuito, sessoes):
    linhas = [
        f"🌦️ <b>Previsão — {escape(corrida_nome)}</b>",
        f"📍 {escape(circuito)}",
        "",
    ]

    for sessao in sessoes:
        horario = sessao["dia_hora"].strftime("%d/%m às %H:%M")
        linhas.extend([
            f'<b>{escape(sessao["nome"])}</b> — {horario}',
            _descricao_tempo(sessao["codigo"]),
            f'🌡️ {sessao["temperatura"]} °C · '
            f'🌧️ {sessao["chance_chuva"]}% · '
            f'💨 {sessao["vento"]} km/h',
            "",
        ])

    return "\n".join(linhas)


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


def configuracoes_chat(configuracoes, mostrar_sessoes=False):
    minutos = " e ".join(str(minuto) for minuto in configuracoes["reminder_minutes"])
    sessoes = configuracoes["sessions"]
    if mostrar_sessoes:
        descricao = "Escolha quais sessões receberão lembretes."
    elif len(sessoes) == 7:
        descricao = "Todas"
    else:
        descricao = f"{len(sessoes)} selecionada(s)"

    texto = (
        "⚙️ <b>Configurações deste chat</b>\n\n"
        f"🕒 Fuso: {configuracoes['timezone']}\n"
        f"⏰ Lembretes: {minutos} min antes\n"
        f"🏁 Sessões: {descricao}\n"
        "🌐 Idioma: Português\n\n"
    )
    if mostrar_sessoes:
        return texto + "Escolha as sessões abaixo:"
    return texto + "Use os botões abaixo para alterar as sessões dos próximos lembretes."
