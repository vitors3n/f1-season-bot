import unittest

from modelos.corrida import Corrida, DiaEvento, Evento


def dados_corrida(sprint=False):
    corrida = {
        "date": "2026-10-18",
        "time": "15:00:00Z",
        "raceName": "GP de Teste",
        "Circuit": {
            "circuitName": "Circuito de Teste",
            "Location": {"lat": "-3.7319", "long": "-38.5267"},
        },
        "FirstPractice": {"date": "2026-10-16", "time": "14:30:00Z"},
        "Qualifying": {"date": "2026-10-17", "time": "18:00:00Z"},
    }

    if sprint:
        corrida["SprintQualifying"] = {"date": "2026-10-17", "time": "14:30:00Z"}
        corrida["Sprint"] = {"date": "2026-10-18", "time": "14:00:00Z"}
    else:
        corrida["SecondPractice"] = {"date": "2026-10-16", "time": "18:00:00Z"}
        corrida["ThirdPractice"] = {"date": "2026-10-17", "time": "14:30:00Z"}

    return corrida


class EventoTest(unittest.TestCase):
    def test_converte_horario_utc_para_fortaleza(self):
        evento = Evento("2026-10-18", "15:00:00Z")

        self.assertTrue(evento.tem_horario)
        self.assertEqual(evento.dia_hora(), "18/10/2026, 12:00")
        self.assertEqual(evento.dia_hora_datetime().strftime("%z"), "-0300")

    def test_sem_horario_preserva_data_e_retorna_none(self):
        evento = Evento("2026-10-18")

        self.assertFalse(evento.tem_horario)
        self.assertEqual(evento.dia_hora(), "18/10/2026, horário a definir")
        self.assertIsNone(evento.dia_hora_datetime())


class DiaEventoTest(unittest.TestCase):
    def test_mantem_nome_data_e_horario_da_api(self):
        evento = DiaEvento("Treino Livre 1", {"date": "2026-10-16", "time": "14:30:00Z"})

        self.assertEqual(evento.nome, "Treino Livre 1")
        self.assertEqual(evento.dia_hora(), "16/10/2026, 11:30")


class CorridaTest(unittest.TestCase):
    def test_fim_de_semana_convencional_cria_treinos_e_classificacao(self):
        corrida = Corrida(dados_corrida())

        self.assertEqual(corrida.nome, "GP de Teste")
        self.assertEqual(corrida.circuito, "Circuito de Teste")
        self.assertEqual(corrida.latitude, -3.7319)
        self.assertEqual(corrida.longitude, -38.5267)
        self.assertIsNotNone(corrida.fp1)
        self.assertIsNotNone(corrida.fp2)
        self.assertIsNotNone(corrida.fp3)
        self.assertIsNotNone(corrida.quali)
        self.assertIsNone(corrida.sprint)
        self.assertIsNone(corrida.sprint_quali)

    def test_fim_de_semana_sprint_cria_eventos_sprint(self):
        corrida = Corrida(dados_corrida(sprint=True))

        self.assertEqual(corrida.sprint_quali.nome, "Qualificação Sprint")
        self.assertEqual(corrida.sprint.nome, "Sprint")
        self.assertIsNone(corrida.fp2)
        self.assertIsNone(corrida.fp3)
        self.assertEqual(corrida.sprint.dia_hora(), "18/10/2026, 11:00")

