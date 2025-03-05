from fastapi import FastAPI, Request, Form, Depends, HTTPException, Response, Query, APIRouter, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from pathlib import Path

import shutil

import asyncio

from typing import List

from sqlalchemy.orm import Session, joinedload

from models import Enduro, Competitor, Category, Checkpoint, CompetitorCreate, CompetitorResponse, Trackpoint, ResultadoComparacao, Resultados

from datetime import datetime, timedelta, time

from typing import Optional

from database import get_db

from calculos import time_to_seconds, to_time_string

from service import  salvar_trackpoint, processar_tcx

from tcxreader import tcxreader

# Configuração do Jinja2Templates
templates = Jinja2Templates(directory="templates")

router = APIRouter()










# Página inicial
@router.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Rotas para Enduros
@router.get("/enduros/create/", response_class=HTMLResponse)
def create_enduro_form(request: Request):
    return templates.TemplateResponse("create_enduro.html", {"request": request, "enduro": Enduro})

#Rota para inserir um enduro


@router.post("/enduros/")
async def create_enduro(
    request: Request,
    name: str = Form(...),
    location: str = Form(...),
    date: str = Form(...),
    hora_largada: str = Form(...),
    db: Session = Depends(get_db),
    response: Response = Response
):
  # Garante que a hora de largada sempre tenha segundos (HH:MM:SS)
    if len(hora_largada) == 5:  # Exemplo: "09:00"
        hora_largada += ":00"  # Converte para "09:00:00"


    # Criar o objeto Enduro
    enduro = Enduro(
        name=name,
        location=location,
        date=date,
        hora_largada=hora_largada
    )

    # Salvar no banco de dados com um gerenciador de sessão seguro
    db.add(enduro)
    db.commit()
    db.refresh(enduro)

    return RedirectResponse(url="/enduros/", status_code=303)

#Rota para visualizar enduros 
@router.get("/enduros/", response_class=HTMLResponse)
def list_enduros(request: Request, db: Session = Depends(get_db)):
    enduros = db.query(Enduro).all()
    
       
    return templates.TemplateResponse("list_enduros.html", {"request": request, "enduros": enduros})

@router.get("/enduros/{enduro_id}/")
def enduro_detail(enduro_id: int, request: Request, db: Session = Depends(get_db)):
    enduro = db.query(Enduro).filter(Enduro.id == enduro_id).first()
    if not enduro:
        raise HTTPException(status_code=404, detail="Enduro não encontrado")

    competitor = db.query(Competitor).filter(Competitor.enduro_id == enduro_id).all()

    return templates.TemplateResponse(
        "enduro_detail.html",
        {
            "request": request,
            "enduro": enduro,
            "competitor": competitor  # Passando os competidores para o template
        }
    )

# Rota para editar os enduros

@router.get("/enduros/{enduro_id}/edit/", response_class=HTMLResponse)
def edit_enduro_form(enduro_id: int, request: Request, db: Session = Depends(get_db)):
    enduro = db.query(Enduro).filter(Enduro.id == enduro_id).first()
    if not enduro:
        raise HTTPException(status_code=404, detail="Enduro não encontrado")
    return templates.TemplateResponse("edit_enduro.html", {"request": request, "enduro": enduro})

#Rota para editar os enduros
@router.post("/enduros/{enduro_id}/update/", response_class=RedirectResponse)
def update_enduro(
    enduro_id: int,
    request: Request,
    name: str = Form(...),
    location: str = Form(...),
    date: str = Form(...),
    hora_largada: str = Form(...),
    db: Session = Depends(get_db),
    response: Response = Response
):
    db_enduro = db.query(Enduro).filter(Enduro.id == enduro_id).first()
    if not db_enduro:
        raise HTTPException(status_code=404, detail="Enduro não encontrado")
    
    db_enduro.name = name
    db_enduro.location = location
    db_enduro.date = date
    db_enduro.hora_largada = hora_largada
   
    db.commit()
    db.refresh(db_enduro)
    
    return RedirectResponse(url="/enduros/", status_code=303)

# Rota para deletar os enduros

@router.post("/enduros/{enduro_id}/delete/", response_class=RedirectResponse)
def delete_enduro(
    enduro_id: int,
    db: Session = Depends(get_db),
    response: Response = Response
):
    db_enduro = db.query(Enduro).filter(Enduro.id == enduro_id).first()
    if not db_enduro:
        raise HTTPException(status_code=404, detail="Enduro não encontrado")
    
    
    db.delete(db_enduro)
    db.commit()    
   

    
    return RedirectResponse(url="/enduros/", status_code=303)

# Rotas para ver adicionar Competidores
@router.get("/enduros/{enduro_id}/competitors/create", response_class=HTMLResponse)
def create_competitor_form( enduro_id: int, request: Request, db: Session = Depends(get_db)):
    
    categories = db.query(Category).all()  # Buscar todas as categorias do banco
    enduro = db.query(Enduro).filter(Enduro.id == enduro_id).first()
    if not enduro:
        raise HTTPException(status_code=404, detail="Enduro não encontrado")
    return templates.TemplateResponse("create_competitor.html", 
                                      {"request": request, "enduro": enduro, "categories": categories})


#rota para adicionar competidores
@router.post("/enduros/{enduro_id}/competitors/", response_class=RedirectResponse)
def create_competitor(
    enduro_id: int,
    request: Request,
    name: str = Form(...),
    placa: str = Form(...),
    categories_id: int = Form(...),
    db: Session = Depends(get_db),
    response: Response = Response
):


    enduro = db.query(Enduro).filter(Enduro.id==enduro_id).first()
    if not enduro:
        raise HTTPException(status_code=404, detail="Enduro não encontrado")
    
    db_competitor = Competitor(name=name, enduro_id = enduro_id, placa=placa, categories_id = categories_id)
    db.add(db_competitor)
    db.commit()
    db.refresh(db_competitor)
    
    return RedirectResponse(url="/enduros/1/",  status_code=303)

# Rota para editar os competidores

@router.get("/enduros/{enduro_id}/competitors/{competitor_id}/edit/", response_class=HTMLResponse)
def edit_competitor_form(enduro_id: int, competitor_id: int, request: Request, db: Session = Depends(get_db)):
    # Busca o competidor pelo ID
    
    enduro = db.query(Enduro).filter(Enduro.id==enduro_id).first()
    if not enduro:
        raise HTTPException(status_code=404, detail="Enduro não encontrado")
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    # Busca todas as categorias disponíveis no banco de dados
    categories = db.query(Category).all()

    # Verifica se o competidor existe
    if not competitor:
        raise HTTPException(status_code=404, detail="Competidor não encontrado")

    # Envia os dados para o template
    return templates.TemplateResponse("edit_competitor.html", {
        "request": request,
        "competitor": competitor,
        "categories": categories,
        "enduro": enduro  # Passando o ID do enduro para o formulário
    })

# Rota para editar os competidores
@router.post("/enduros/{enduro_id}/competitors/{competitor_id}/update/", response_class=RedirectResponse)
def update_competitor(
    enduro_id: int,
    competitor_id: int, 
    request: Request,
    name: str = Form(...),
    placa: str = Form(...),
    categories_name: int = Form(...),  # Agora recebendo o ID da categoria
    db: Session = Depends(get_db),
):
    
    db_enduro = db.query(Enduro).filter(Enduro.id==enduro_id).first()
    if not db_enduro:
        raise HTTPException(status_code=404, detail="Enduro não encontrado")
    
    db_competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not db_competitor:
        raise HTTPException(status_code=404, detail="Competidor não encontrado")
    
    category = db.query(Category).filter(Category.id == categories_name).first()
    if category:
        db_competitor.category = category  # Atualizando o relacionamento entre Competitor e Category
    else:
        raise HTTPException(status_code=400, detail="Categoria inválida")
        
        
    db_competitor.name = name
    db_competitor.placa = placa
    db_competitor.category_id = category      
    db.commit()
    db.refresh(db_competitor)
        
   
    # Redireciona para a página de detalhes do enduro ou para a lista de competidores
    return RedirectResponse(url="/enduros/", status_code=303)

 #Rota para deletar competidores

@router.post("/enduros/{enduro_id}/competitors/{competitor_id}/delete/", response_class=RedirectResponse)
def delete_competitor(
    enduro_id: int,
    competitor_id: int, 
    db: Session = Depends(get_db),
):
        
    db_competitor = db.query(Competitor).filter(Competitor.id == competitor_id, Competitor.enduro_id == enduro_id).first()
    if not db_competitor:
        raise HTTPException(status_code=404, detail="Competidor não encontrado")
    
    
    
    db.delete(db_competitor)
    db.commit()
    
    
    return RedirectResponse(url=f"/enduros/{enduro_id}/competitors/", status_code=303)


"""
# Update dos Pcs 

#PC 1
@router.get("/enduros/{enduro_id}/competitors/{competitor_id}/pc/edit/", response_class=HTMLResponse)
def edit_competitor_form_pc1(enduro_id: int, competitor_id: int,    request: Request, db: Session = Depends(get_db)):
    
    # Busca o competidor pelo ID
    enduro = db.query(Enduro).filter(Enduro.id==enduro_id).first()
    if not enduro:
        raise HTTPException(status_code=404, detail="Enduro não encontrado")
    
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competidor não encontrado")

    categories = db.query(Category).all()
    
    checkpoint = db.query(Checkpoint).all()
    
    

    # Verifica se o competidor existe
    
    # Envia os dados para o template
    return templates.TemplateResponse("editpc1_competitor.html", {
        "request": request,
        "competitor": competitor,
        "categories": categories,
        "checkpoint": checkpoint, 
        "enduro": enduro  # Passando o ID do enduro para o formulário
    })




@router.post("/enduros/{enduro_id}/checkpoints/{checkpoint_id}/competitors/{competitor_id}/pc/update/")
def update_competitor_pcs(
    enduro_id: int,
    checkpoint_id: int,
    competitor_id: int,
    pc1: str = Form(None),
    pc2: str = Form(None),
    pc3: str = Form(None),
    pc4: str = Form(None),
    pc5: str = Form(None),
    pc6: str = Form(None),
    pc7: str = Form(None),
    pc8: str = Form(None),
    pc9: str = Form(None),
    pc10: str = Form(None),
    pc11: str = Form(None),
    pc12: str = Form(None),
    db: Session = Depends(get_db), 
):
    competitor = db.query(Competitor).filter(Competitor.id == competitor_id).first()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competidor não encontrado")
    
    enduro = db.query(Enduro).filter(Enduro.id==enduro_id).first()
    if not enduro:
        raise HTTPException(status_code=404, detail="Enduro não encontrado")
    
    checkpoints = db.query(Checkpoint).filter(Checkpoint.id == checkpoint_id).first()


    # Converter tempos para strings formatadas antes de salvar
    if pc1: competitor.pc1 = to_time_string(pc1)
    if pc2: competitor.pc2 = to_time_string(pc2)
    if pc3: competitor.pc3 = to_time_string(pc3)
    if pc4: competitor.pc4 = to_time_string(pc4)
    if pc5: competitor.pc5 = to_time_string(pc5)
    if pc6: competitor.pc6 = to_time_string(pc6)
    if pc7: competitor.pc7 = to_time_string(pc7)
    if pc8: competitor.pc8 = to_time_string(pc8)
    if pc9: competitor.pc9 = to_time_string(pc9)
    if pc10: competitor.pc10 = to_time_string(pc10)
    if pc11: competitor.pc11 = to_time_string(pc11)
    if pc12: competitor.pc12 = to_time_string(pc12)

    db.commit()
    db.refresh(competitor)

    return RedirectResponse(url=f"/enduros/{enduro_id}/checkpoints/1/competitors", status_code=303)


"""
    
   
# rota para ver lista de competidores 

@router.get("/enduros/{enduro_id}/competitors/", response_class=HTMLResponse) 
def list_competitors(enduro_id: int, request: Request, db: Session = Depends(get_db)):
    
    enduro = db.query(Enduro).filter(Enduro.id == enduro_id).first()
    if not enduro:
        raise HTTPException(status_code=404, detail="Enduro não encontrado")
    
    competitors = db.query(Competitor).options(joinedload(Competitor.category)).filter(Competitor.enduro_id == enduro_id).all()
    return templates.TemplateResponse("list_competitors.html", {"request": request, "enduro": enduro, "competitors": competitors})# Rotas para Checkpoints

#Criando Checkpoint 
@router.get("/enduros/{enduro_id}/checkpoints/create/", response_class=HTMLResponse)
def create_checkpoint_form(enduro_id: int, request: Request, db: Session = Depends(get_db)):
    enduro = db.query(Enduro).filter(Enduro.id == enduro_id).first()
    if not enduro:
        raise HTTPException(status_code=404, detail="Enduro não encontrado")
    return templates.TemplateResponse("create_checkpoint.html", {"request": request, "enduro": enduro})

@router.post("/enduros/{enduro_id}/checkpoints/", response_class=RedirectResponse)
def create_checkpoint(
    enduro_id: int,
    request: Request,
    name: str = Form(...),
    tempo: float = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    raio: float = Form(...),
    db: Session = Depends(get_db),
    response: Response = Response
):

    try:
        # Verifica se o enduro existe
        enduro = db.query(Enduro).filter(Enduro.id == enduro_id).first()
        if not enduro:
            raise HTTPException(status_code=404, detail="Enduro não encontrado")

        # Cria o checkpoint
        db_checkpoint = Checkpoint(name=name, time=tempo, enduro_id=enduro_id, latitude=latitude, longitude = longitude, raio=raio)
        db.add(db_checkpoint)
        db.commit()
        db.refresh(db_checkpoint)


        # Define uma mensagem de sucesso
        return RedirectResponse(url=f"/enduros/{enduro_id}/", status_code=303)
    except Exception as e:
        # Em caso de erro, faz rollback e levanta uma exceção
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar checkpoint: {str(e)}")
# Rota Lista checkpoints

#Rota para visualizar checkpoints 
@router.get("/enduros/{enduro_id}/checkpoints/", response_class=HTMLResponse)
def list_checkpoints(request: Request, enduro_id: int, db: Session = Depends(get_db)):
    enduro = db.query(Enduro).filter(Enduro.id == enduro_id).first()
    if not enduro:
        raise HTTPException(status_code=404, detail="Enduro não encontrado")
    
    
    
    checkpoints = db.query(Checkpoint).filter(Checkpoint.enduro_id == enduro_id).all()
    
     # Formatando o tempo de cada checkpoint
    for checkpoint in checkpoints:
        # Convertendo o tempo (float) para timedelta
        formatted_time = str(timedelta(seconds=checkpoint.time))
        
        # Ajustar o formato para garantir HH:MM:SS, mesmo para tempos abaixo de uma hora
        hours, remainder = divmod(checkpoint.time, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # Criar o formato desejado
        formatted_time = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
        
        checkpoint.formatted_time = formatted_time

    
    
    return templates.TemplateResponse("list_checkpoints.html", {"request": request, "checkpoints": checkpoints, "enduro": enduro})



@router.get("/enduros/{enduro_id}/checkpoints/{checkpoint_id}/edit/", response_class=HTMLResponse)
def edit_checkpoint_form(request: Request, enduro_id: int, checkpoint_id: int, db: Session = Depends(get_db)):
   # Verifica se o enduro existe
    enduro = db.query(Enduro).filter(Enduro.id == enduro_id).first()
    if not enduro:
        raise HTTPException(status_code=404, detail="Enduro não encontrado")
   
    checkpoint = db.query(Checkpoint).filter(Checkpoint.id == checkpoint_id).first()
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Competidor não encontrado")

    # Envia os dados para o template
    return templates.TemplateResponse("edit_checkpoint.html", {
        "request": request,
        "checkpoint": checkpoint,
        "enduro": enduro  # Passando o ID do enduro para o formulário
    })
    
#Rota para editar checkpoints 
@router.post("/enduros/{enduro_id}/checkpoints/{checkpoint_id}/update/", response_class=RedirectResponse)
def update_checkpoint(
    enduro_id: int,
    checkpoint_id: int, 
    request: Request,
    name: str = Form(...),
    time: float = Form(...), 
    db: Session = Depends(get_db),
):
    
    
    
        
    db_checkpoint = db.query(Checkpoint).filter(Checkpoint.id == checkpoint_id).first()
    if not db_checkpoint:
        raise HTTPException(status_code=404, detail="Competidor não encontrado")

    db_checkpoint.name = name
    db_checkpoint.time = time
    db.commit
    db.refresh(db_checkpoint)
        
   
    # Redireciona para a página de detalhes do enduro ou para a lista de competidores
    return RedirectResponse(url=f"/enduros/{enduro_id}/checkpoints/", status_code=303)

# rota para deletar os checkpoints

@router.post("/enduros/{enduro_id}/checkpoints/{checkpoint_id}/delete/", response_class=RedirectResponse)
def delete_checkpoint(
    enduro_id: int,
    checkpoint_id: int, 
    db: Session = Depends(get_db),
):
  
    
    db_checkpoint = db.query(Checkpoint).filter(Checkpoint.id == checkpoint_id).first()
    if not db_checkpoint:
        raise HTTPException(status_code=404, detail="Competidor não encontrado")
    
    
    
    db.delete(db_checkpoint)
    db.commit()
    
    
    return RedirectResponse(url=f"/enduros/{enduro_id}/checkpoints/", status_code=303)


#Rota para lançamento dos tempos

@router.get("/enduros/{enduro_id}/checkpoints/{checkpoint_id}/competitors/", response_class=HTMLResponse)
def register_tempo_checkpoint(enduro_id: int, checkpoint_id: int, request: Request, db: Session = Depends(get_db)):
    # Busca o enduro no banco de dados
    enduro = db.query(Enduro).filter(Enduro.id == enduro_id).first()
    if not enduro:
        raise HTTPException(status_code=404, detail="Enduro não encontrado")
    
    # Busca o checkpoint no banco de dados
    checkpoint = db.query(Checkpoint).filter(Checkpoint.id == checkpoint_id).first()
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint não encontrado")
    
    # Busca os competidores associados ao enduro do checkpoint
    competitor = db.query(Competitor).filter(Competitor.enduro_id == checkpoint.enduro_id).all()
    if not competitor:
        raise HTTPException(status_code=404, detail="Competidor não encontrado")
    
    # Renderiza o template (ajuste os nomes dos parâmetros conforme necessário)
    return templates.TemplateResponse("list_competitors_for_checkpoint.html", {
        "request": request,
        "enduro": enduro,
        "competitors": competitor,
        "checkpoint": checkpoint
    })




#Rota para inserir um categorias

@router.get("/enduros/{enduro_id}/category/create", response_class=HTMLResponse)
def create_category_form(enduro_id: int,  request: Request, db: Session = Depends(get_db)):
    
    enduro = db.query(Enduro).filter(Enduro.id == enduro_id).first()
    if not enduro:
        raise HTTPException(status_code=404, detail="Enduro não encontrado")
    
    return templates.TemplateResponse("create_category.html", {"request": request, "enduro": enduro})

@router.post("/enduro/{enduro_id}/category", response_class=RedirectResponse)
def create_category(
    request: Request,
    enduro_id: int,
    name: str = Form(...),
    db: Session = Depends(get_db),
    response: Response = Response
):
    db_category = Category( enduro_id=enduro_id, name=name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return RedirectResponse(url=f"/enduros/", status_code=303)

#Rota para visualizar categorias 
@router.get("/enduros/{enduro_id}/categories/", response_class=HTMLResponse)
def list_category(request: Request, enduro_id: int, db: Session = Depends(get_db)):
    categories = db.query(Category).all()  # Corrigido para pegar todas as categorias
    return templates.TemplateResponse("list_categories.html", {"request": request, "categories": categories, "enduro_id": enduro_id})

# Rota para editar os categorias

@router.get("/enduros/{enduro_id}/categories/{category_id}/edit/", response_class=HTMLResponse)
def edit_category_form(
    enduro_id: int,
    category_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    # Verifica se o enduro existe
    enduro = db.query(Enduro).filter(Enduro.id == enduro_id).first()
    if not enduro:
        raise HTTPException(status_code=404, detail="Enduro não encontrado")

    # Verifica se a categoria existe
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    return templates.TemplateResponse(
        "edit_category.html",
        {"request": request, "enduro": enduro, "category": category}
    )
    x
@router.post("/enduros/{enduro_id}/categories/{category_id}/update/", response_class=RedirectResponse)
def update_category(
    enduro_id: int,
    category_id: int,
    category_name: str = Form(...),
    db: Session = Depends(get_db)
):
    # Verifica se o enduro existe
    enduro = db.query(Enduro).filter(Enduro.id == enduro_id).first()
    if not enduro:
        raise HTTPException(status_code=404, detail="Enduro não encontrado")

    # Verifica se a categoria existe
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    # Atualiza o nome da categoria
    db_category.name = category_name  # Certifique-se de que o campo no modelo se chama `name`
    db.commit()
    db.refresh(db_category)

    # Redireciona para a página do enduro ou da categoria
    return RedirectResponse(url=f"/enduros/{enduro_id}/categories/", status_code=303)


# Rota para deletar os categorias

@router.post("/enduros/{enduro_id}/categories/{category_id}/delete/", response_class=RedirectResponse)
def delete_category(
    enduro_id: int,
    category_id: int, 
    db: Session = Depends(get_db),
    response: Response = Response
):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    
    db.delete(db_category)
    db.commit()    
    
    return RedirectResponse(url=f"/enduros/{enduro_id}/categories/", status_code=303)


# Rota para exibir a lista de largada

@router.get("/enduros/{enduro_id}/listalargada/", response_class=HTMLResponse)
def list_largada(enduro_id: int, request: Request, db: Session = Depends(get_db)):
    # Busca o enduro no banco de dados
    enduro = db.query(Enduro).filter(Enduro.id == enduro_id).first()
    if not enduro:
        raise HTTPException(status_code=404, detail="Enduro não encontrado")

    # Busca os competidores associados ao enduro
    competitors = db.query(Competitor).filter(Competitor.enduro_id == enduro_id).all()
    
    largada_list = []

    # Converte a hora de largada para datetime caso seja string
    try:
        hora_atual = datetime.strptime(enduro.hora_largada, "%H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=500, detail="Formato de hora de largada inválido")

    for competitor in competitors:
        # Obtém o nome do competidor
        competitor_name = competitor.name if competitor else "Sem nome"
        
        # Obtém a categoria do competidor
        category = db.query(Category).filter(Category.id == competitor.categories_id).first()
        category_name = category.name if category else "Sem categoria"
        
        # Adiciona o competidor à lista de largada com a hora ajustada
        largada_list.append({
            "name": competitor_name,
            "category": category_name,
            "hora_largada": hora_atual.strftime("%H:%M:%S")  # Agora funciona corretamente
        })
        
        # Incrementa a hora de largada para o próximo competidor
        hora_atual += timedelta(minutes=1)

    return templates.TemplateResponse(
        "list_largada.html",
        {"request": request, "enduro": enduro, "largada_list": largada_list}
    )


# Lista de tempos
    
@router.get("/enduros/{enduro_id}/tempos/", response_class=HTMLResponse)
def list_tempos(request: Request, enduro_id: int, db: Session = Depends(get_db)):
    # Busca o enduro no banco de dados
    enduro = db.query(Enduro).filter(Enduro.id == enduro_id).first()
    if not enduro:
        raise HTTPException(status_code=404, detail="Enduro não encontrado")

    # Busca os competidores associados ao enduro
    competitors = db.query(Competitor).filter(Competitor.enduro_id == enduro_id).all()

    # Passa a lista de competidores para o template
    return templates.TemplateResponse(
        "lista_tempos.html", 
        {"request": request, "enduro": enduro, "competitors": competitors}
    )

#lista de classificaçao 
@router.get("/enduros/tabela/", response_class=HTMLResponse)
def list_enduros(request: Request, enduro_id: int, db:  Session = Depends(get_db)):
    enduros = db.query(Enduro).all()
    
       
    return templates.TemplateResponse("Pagina1.html", {"request": request, "enduros": enduros})
    
    
# Adiciona a função ao ambiente do Jinja2
templates.env.globals.update(time_to_seconds=time_to_seconds)

@router.get("/resultados/{enduro_id}/")
def mostrar_resultados(enduro_id: int, request: Request, db: Session = Depends(get_db)):
    competitors = db.query(Competitor).filter(Competitor.enduro_id == enduro_id).all()
    checkpoints = db.query(Checkpoint).filter(Checkpoint.enduro_id == enduro_id).all()
    
    if not competitors or not checkpoints:
        return {"error": "Dados não encontrados"}

    # Busca a hora de largada (exemplo: supondo que está armazenada no banco de dados)
    enduro = db.query(Enduro).filter(Enduro.id == enduro_id).first()
    if not enduro:
        return {"error": "Enduro não encontrado"}

    hora_largada = 32400  # Supondo que `hora_largada` é um campo no modelo Enduro

    # Se a hora_largada for um objeto datetime, converta para segundos
    if isinstance(hora_largada, datetime):
        hora_largada = int(hora_largada.timestamp())  # Converte para segundos desde a época (Unix timestamp)

    return templates.TemplateResponse("resultados.html", {
        "request": request,
        "competitors": competitors,
        "checkpoints": checkpoints,
        "num_checkpoints": len(checkpoints),
        "hora_largada": hora_largada  # Passa a hora_largada para o template
    })
    

hora_str = ''  # Exemplo de hora vazia

try:
    hora = datetime.strptime(hora_str, '%H:%M:%S')
except ValueError:
    print(f"Erro: A hora '{hora_str}' não está no formato esperado '%H:%M:%S'.")


# Rota para exibir a interface upload 

@router.get("/enduros/{enduro_id}/competitors/{competitor_id}/upload/", response_class=HTMLResponse)
async def home(request: Request, enduro_id: int, competitor_id: int, db: Session = Depends(get_db)):
    # Recupera os resultados da comparação
    resultados = db.query(Resultados).all()
    enduro =  db.query(Enduro).filter(Enduro.id==enduro_id).first()
    competitor = db.query(Competitor).filter(Competitor.id==competitor_id).first()
    
    return templates.TemplateResponse("upload.html", {
        "request": request,
        "resultados": resultados,
        "enduro_id": enduro_id,  # Passa o enduro_id para o template
        "competitor_id": competitor_id  # Passa o competitor_id para o template
    })

# Rota para processar o arquivo TCX enviado
@router.post("/enduros/{enduro_id}/competitors/{competitor_id}/upload/upload_tcx/")
async def upload_tcx(file: UploadFile = File(...)):
    if not file.filename.endswith(".tcx"):
        raise HTTPException(status_code=400, detail="Apenas arquivos TCX são permitidos")

    temp_path = Path(f"temp/{file.filename}")
    temp_path.parent.mkdir(parents=True, exist_ok=True)

    with temp_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Garante que o banco está conectado antes de salvar os dados
    await get_db.connect()

    # Processa e salva os trackpoints
    await extrair_e_salvar_tcx(temp_path)

    # Compara os dados com checkpoints e armazena os resultados
    resultados = await comparar_com_checkpoints(temp_path)

    # Fecha conexão com o banco após o processamento
    await get_db.disconnect()

    temp_path.unlink(missing_ok=True)

    return {"resultados": resultados}

async def extrair_e_salvar_tcx(caminho_tcx: Path, competitor_id: int, db: Session):
    from tcxreader import TCXReader

    try:
        tcx_reader = TCXReader()
        dados_tcx = tcx_reader.read(str(caminho_tcx))

        for tp in dados_tcx.trackpoints:
            if tp.latitude and tp.longitude and tp.time:  # Verifica se o tempo não está vazio
                try:
                    # Converte o tempo para string no formato ISO
                    time_str = tp.time.isoformat()
                except AttributeError:
                    # Se tp.time não for um objeto datetime, ignora o trackpoint
                    continue

                trackpoint = Trackpoint(
                    competitor_id=competitor_id,
                    latitude=tp.latitude,
                    longitude=tp.longitude,
                    time=time_str,  # Usa o tempo formatado
                    altitude=tp.elevation,
                    distance=tp.distance,
                    heart_rate=tp.heart_rate
                )
                db.add(trackpoint)
        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao processar o arquivo TCX: {e}")

async def salvar_trackpoint(trackpoint: Trackpoint):
    query = """
    INSERT INTO trackpoints (latitude, longitude, time, altitude, distance, heart_rate)
    VALUES (:latitude, :longitude, :time, :altitude, :distance, :heart_rate)
    """
    await get_db.execute(query=query, values=trackpoint.dict())

async def comparar_com_checkpoints(caminho_tcx: Path):
    # Simulação da lógica de comparação com checkpoints
    resultados = [
        ResultadoComparacao(
            checkpoint_id=1,
            latitude=-19.9227,
            longitude=-43.9451,
            time="2024-03-05T14:00:00",
            distancia=100.5
        )
    ]

    # Salva os resultados no banco
    tarefas = [salvar_resultado(resultado) for resultado in resultados]
    await asyncio.gather(*tarefas)

    return resultados

async def salvar_resultado(resultado: ResultadoComparacao):
    query = """
    INSERT INTO resultados (checkpoint_id, latitude, longitude, time, distancia)
    VALUES (:checkpoint_id, :latitude, :longitude, :time, :distancia)
    """
    await get_db.execute(query=query, values=resultado.dict())