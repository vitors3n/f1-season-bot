from datetime import datetime
import pytz

def corrida_passou(data_corrida):
    data_corrida_datetime = datetime.strptime(data_corrida, "%Y-%m-%d %H:%M:%SZ").replace(tzinfo=pytz.UTC)
    data_corrida_datetime = data_corrida_datetime.astimezone(pytz.timezone("America/Sao_Paulo"))
    data_hoje = datetime.now().astimezone(pytz.timezone("America/Sao_Paulo"))

    if data_corrida_datetime < data_hoje:
        return True
    return False