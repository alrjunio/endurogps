from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import DeclarativeMeta

from database import SessionLocal
from models import Competitor


from datetime import datetime

def contar_registros(db: Session, model: DeclarativeMeta):
    """ Conta o número de registros de qualquer tabela """
    return db.query(func.count(model.id)).scalar()

def seconds_to_hms(seconds: float) -> str:
    """Converte segundos para o formato HH:MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"




# Função para converter "HH:MM:SS" para minutos desde a meia-noite
def time_to_seconds(time_str):
    time_obj = datetime.strptime(time_str, "%H:%M:%S")
    return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second

# Exemplo de uso
hora_largada_seconds = time_to_seconds("14:30:00")  # Retorna 52200
print(hora_largada_seconds)


def to_time_string(value):
    """Tenta converter uma string HH:MM:SS para o formato correto (string)."""
    try:
        return datetime.strptime(value, "%H:%M:%S").strftime("%H:%M:%S") if value else None
    except ValueError:
        return None
    
# Função para converter tempo em segundos
def time_to_seconds(time_str: str) -> int:
    time_obj = datetime.strptime(time_str, "%H:%M:%S")
    return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second