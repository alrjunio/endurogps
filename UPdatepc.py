from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, get_db
from models import Competitor, UpdatePC,  UpdatePCList

from typing import List

app = FastAPI()




@app.post("/update_pc_bulk/")
def update_pc_bulk(data: UpdatePCList, db: Session = Depends(get_db)):
    updated_competitors = []

    for item in data.updates:
        # Buscar o competidor pelo número da placa
        competitor = db.query(Competitor).filter(Competitor.placa == item.placa).first()
        
        if not competitor:
            continue  # Ignora se o competidor não for encontrado
        
        # Atualizar o campo PC correspondente
        pc_field = f"pc{item.pc}"
        if hasattr(competitor, pc_field):
            setattr(competitor, pc_field, item.hora)
        else:
            continue  # Ignora se o PC for inválido

        db.commit()
        db.refresh(competitor)
        updated_competitors.append(competitor)

    return {"message": "PCs updated successfully", "updated_competitors": updated_competitors}


   # Executar o aplicativo
if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level='info' , reload=True )