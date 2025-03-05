from fastapi import Request,  Depends, HTTPException
from sqlalchemy import  text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from database import engine, get_db
from models import Enduro, Competitor, Tempo, Checkpoint, Category

from datetime import datetime, timedelta


# Função para adicionar uma nova coluna na tabela Tempo
def adicionar_coluna_tempo(nome_coluna):
    with engine.connect() as conn:
        try:
            conn.execute(text(f'ALTER TABLE tempos ADD COLUMN "{nome_coluna}" TEXT DEFAULT "";'))
            conn.commit()
        except Exception as e:
            print(f"Erro ao adicionar coluna: {e}")
    

def largada_list(hora_largada: int, competitors: int,  enduro_id: int,request: Request, db: Session = Depends(get_db)):
    enduro = db.query(Enduro).filter(Enduro.id == enduro_id).first()
    largada_list = []
    hora_largada_base = datetime.strptime(enduro.hora_largada, "%H:%M")  # Converte a hora de largada base para um objeto datetime

    for i, competitor in enumerate(competitors):
        # Adiciona i minutos à hora de largada base
        hora_largada_competitor = (hora_largada_base + timedelta(minutes=i)).strftime("%H:%M")
        
        # Busca o nome da categoria do competidor
        category = db.query(Category).filter(Category.id == competitor.categories_id).first()
        category_name = category.name if category else "Sem categoria"
        
        
        
def adicionar_tempo(enduro_id: int, checkpoint_id: int, competitor_id: int, largada: float, checkpoint_name: str):
    """
    Insere um novo registro na tabela 'tempos'.
    """
    try:
        with engine.connect() as connection:
            query = (
                f"INSERT INTO tempos (enduro_id, checkpoint_id, competitor_id, largada, {checkpoint_name}) "
                f"VALUES ({enduro_id}, {checkpoint_id}, {competitor_id}, {largada}, '{checkpoint_name}')"
            )
            connection.execute(query)
            print(f"Registro adicionado com sucesso!")
            
    except SQLAlchemyError as e:
        print(f"Erro ao adicionar tempo: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao adicionar tempo: {e}"
        )

    