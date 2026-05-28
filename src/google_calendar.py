from urllib.parse import urlencode
from datetime import datetime

def gerar_link_google_calendar(nome_vacina: str, data_evento: datetime) -> str:
    data_str = data_evento.strftime("%Y%m%dT090000")
    data_fim  = data_evento.strftime("%Y%m%dT100000")
    params = urlencode({
        "action": "TEMPLATE",
        "text": f"Vacina: {nome_vacina}",
        "dates": f"{data_str}/{data_fim}",
        "details": "Lembrete gerado pelo Bot Gotinha 💉",
    })
    return f"https://calendar.google.com/calendar/render?{params}"