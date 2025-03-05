from sqlalchemy.orm import Session
from fastapi import Depends
from models import Checkpoint, Competitor, Enduro
from datetime import datetime, timedelta

def time_to_seconds(time_str: str) -> int:
    """Converte uma string de tempo HH:MM:SS para segundos."""
    time_obj = datetime.strptime(time_str, "%H:%M:%S")
    return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second

def calcular_pontuacao(competitor_id: int, enduro_id: int, db: Session):
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not competitor:
        return {"error": "Competidor não encontrado"}
    
    enduro = db.query(Enduro).filter(Enduro.id == enduro_id).first()
    if not enduro:
        return {"error": "Enduro não encontrado"}

    # Cada competidor larga com 1 minuto de diferença (atrasado)
    hora_largada = 0
    pontuacao = 0

    checkpoints = db.query(Checkpoint).filter(Checkpoint.enduro_id == enduro_id).all()

    for i, checkpoint in enumerate(checkpoints, start=1):
        # Ajuste para atrasar a largada e os checkpoints
        tempo_checkpoint = int(checkpoint.time) + hora_largada + (competitor_id - 1) * 60
        
        tempo_competidor = getattr(competitor, f'pc{i}', None)
        
        if tempo_competidor is None:
            pontuacao += 1800  # Penalidade por não registrar tempo
            continue
        
        tempo_competidor = time_to_seconds(tempo_competidor)
        diferenca = (tempo_competidor - tempo_checkpoint)
        
        n = 3

        if diferenca > 0:
            pontuacao += 3 * diferenca  # Penalidade de 3 pontos por segundo de atraso
            
        elif diferenca <= 0:
            pontuacao += abs(diferenca)  # Penalidade de 1 ponto por segundo adiantado

    return {"competitor_id": competitor_id, "pontuacao": pontuacao}