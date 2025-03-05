from fastapi import Depends
from tcxreader.tcxreader import TCXReader
from geopy.distance import geodesic
from pathlib import Path
import logging
import asyncio
from database import get_db
from models import Trackpoint, ResultadoComparacao, Checkpoint

from sqlalchemy.orm import Session, joinedload


logging.basicConfig(level=logging.DEBUG)


# Salva um trackpoint no banco de dados
async def salvar_trackpoint(trackpoint: Trackpoint, db: Session = Depends(get_db)):
    query = """
    INSERT INTO trackpoints (latitude, longitude, time, altitude, distance, heart_rate)
    VALUES (:latitude, :longitude, :time, :altitude, :distance, :heart_rate)
    """
    values = {
        "latitude": trackpoint.latitude,
        "longitude": trackpoint.longitude,
        "time": trackpoint.time.isoformat(),
        "altitude": trackpoint.altitude,
        "distance": trackpoint.distance,
        "heart_rate": trackpoint.heart_rate
    }
    await get_db.execute(query=query, values=values)

# Processa um arquivo TCX e salva no banco
async def processar_tcx(caminho_tcx: Path):
    try:
        logging.debug(f"Processando arquivo: {caminho_tcx}")
        if not caminho_tcx.exists():
            logging.error(f"Arquivo não encontrado: {caminho_tcx}")
            return

        tcx_reader = TCXReader()
        dados_tcx = tcx_reader.read(str(caminho_tcx))

        tarefas = [
            salvar_trackpoint(Trackpoint(
                latitude=tp.latitude,
                longitude=tp.longitude,
                time=tp.time,
                altitude=tp.elevation,
                distance=tp.distance,
                heart_rate=tp.heart_rate
            )) for tp in dados_tcx.trackpoints if tp.latitude and tp.longitude
        ]

        await asyncio.gather(*tarefas)
        logging.info(f"Arquivo {caminho_tcx} processado com sucesso.")

    except Exception as e:
        logging.error(f"Erro ao processar o arquivo TCX: {e}")
        
"""""

# Compara os dados do TCX com os checkpoints e salva os resultados no banco
async def comparar_com_checkpoints(caminho_tcx: Path, checkpoint_id: int, db: Session = Depends(get_db)):
    try:
        logging.debug(f"Comparando dados do arquivo {caminho_tcx} com checkpoints")

        tcx_reader = TCXReader()
        dados_tcx = tcx_reader.read(str(caminho_tcx))
        resultados = []

    checkpoints = db.query(Checkpoint).filter(Checkpoint.id == checkpoint_id).first()
        
    for trackpoint in dados_tcx.trackpoints:
        if trackpoint.latitude and trackpoint.longitude:
            for checkpoint in checkpoints:
                    distancia = geodesic(
                        (trackpoint.latitude, trackpoint.longitude),
                        (checkpoint['latitude'], checkpoint['longitude'])
                    ).meters
                    if distancia <= checkpoint['raio']:
                        resultado = ResultadoComparacao(
                            checkpoint_id=checkpoint['id'],
                            latitude=trackpoint.latitude,
                            longitude=trackpoint.longitude,
                            time=trackpoint.time,
                            distancia=distancia
                        )
                        resultados.append(resultado)

        # Salvar os resultados no banco
        await salvar_resultados(resultados)

        return [r.dict() for r in resultados]

        except Exception as e:
        logging.error(f"Erro ao comparar checkpoints: {e}")
        return []

# Salva os resultados da comparação no banco de dados
async def salvar_resultados(resultados):
   
    tarefas = [
        get_db.execute(query=query, values={
            "checkpoint_id": r.checkpoint_id,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "time": r.time.isoformat(),
            "distancia": r.distancia
        }) for r in resultados
    ]

    await asyncio.gather(*tarefas)
    logging.info(f"{len(resultados)} resultados salvos no banco.")
"""