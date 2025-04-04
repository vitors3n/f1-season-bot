from datetime import datetime
import pytz

def corrigir_timezone(dia, hora):
    dia_hora_string = f"{dia} {hora}"
    dia_hora_utc = datetime.strptime(dia_hora_string, "%Y-%m-%d %H:%M:%SZ").replace(tzinfo=pytz.UTC)
    dia_hora_local = dia_hora_utc.astimezone(pytz.timezone("America/Sao_Paulo"))
    return dia_hora_local

class Evento:

    def __init__(self, dia, hora):
        self.dia = dia
        self.hora = hora
    
    def dia_hora(self):
        dia_hora_local = corrigir_timezone(self.dia, self.hora)
        dia_hora_local = dia_hora_local.strftime("%d/%m/%Y, %H:%M")
        return dia_hora_local
    
    def dia_hora_datetime(self):
        dia_hora = corrigir_timezone(self.dia, self.hora)
        dia_hora = dia_hora.strftime("%Y-%m-%d %H:%M:%S")
        dia_hora_dt = datetime.strptime(dia_hora,"%Y-%m-%d %H:%M:%S")
        return dia_hora_dt

class DiaEvento(Evento):

    def __init__(self, nome, evento_json):
        super().__init__(evento_json['date'], evento_json['time'])
        self.nome = nome

class Corrida(Evento):

    def __init__(self, corrida_json):
        super().__init__(corrida_json['date'], corrida_json['time'])
        self.nome = corrida_json['raceName']
        self.circuito = corrida_json['Circuit']['circuitName']
        self.fp1 = DiaEvento('Treino Livre 1', corrida_json['FirstPractice'])
        self.fp2 = None
        self.fp3 = None
        self.sprint = None
        self.sprint_quali = None
        
        if "Sprint" not in corrida_json:
            self.fp2 = DiaEvento('Treino Livre 2', corrida_json['SecondPractice'])
            self.fp3 = DiaEvento('Treino Livre 3', corrida_json['ThirdPractice'])

        if "Sprint" in corrida_json:
            self.sprint_quali = DiaEvento('Qualificação Sprint', corrida_json['SprintQualifying'])
            self.sprint = DiaEvento('Sprint', corrida_json['Sprint'])
        
        self.quali = DiaEvento('Qualificação', corrida_json['Qualifying'])
