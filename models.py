from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime, time
from database import Base, engine

class Enduro(Base):
    __tablename__ = "enduros"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String)
    date = Column(String)
    hora_largada = Column(String, nullable=False)

    competitors = relationship("Competitor", back_populates="enduro")
    checkpoints = relationship("Checkpoint", back_populates="enduro")
    categories = relationship("Category", back_populates="enduro")
    resultados = relationship("Resultados", back_populates="enduro")

class Competitor(Base):
    __tablename__ = "competitors"
    id = Column(Integer, primary_key=True, index=True)
    enduro_id = Column(Integer, ForeignKey("enduros.id"))
    name = Column(String, index=True)
    placa = Column(String)
    categories_id = Column(Integer, ForeignKey("categories.id"))

    enduro = relationship("Enduro", back_populates="competitors")
    checkpoints = relationship("Checkpoint", back_populates="competitor")
    category = relationship("Category", back_populates="competitors")
    resultados = relationship("Resultados", back_populates="competitor")
    trackpoints = relationship("Trackpoint", back_populates="competitor")

class Checkpoint(Base):
    __tablename__ = "checkpoints"
    id = Column(Integer, primary_key=True, index=True)
    enduro_id = Column(Integer, ForeignKey("enduros.id"))
    competitor_id = Column(Integer, ForeignKey("competitors.id"))
    name = Column(String, nullable=False)
    time = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    raio = Column(Integer)

    enduro = relationship("Enduro", back_populates="checkpoints")
    competitor = relationship("Competitor", back_populates="checkpoints")
    resultados = relationship("Resultados", back_populates="checkpoint")  # Updated relationship name

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    enduro_id = Column(Integer, ForeignKey("enduros.id"))
    name = Column(String)

    enduro = relationship("Enduro", back_populates="categories")
    competitors = relationship("Competitor", back_populates="category")

class Resultados(Base):
    __tablename__ = "resultados"
    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id"))
    enduro_id = Column(Integer, ForeignKey("enduros.id"))
    checkpoint_id = Column(Integer, ForeignKey("checkpoints.id"))  # Added foreign key to Checkpoint
    latitude = Column(Float)
    longitude = Column(Float)
    raio = Column(Integer)
    time = Column(Float)
    starttime = Column(String)

    enduro = relationship("Enduro", back_populates="resultados")
    competitor = relationship("Competitor", back_populates="resultados")
    checkpoint = relationship("Checkpoint", back_populates="resultados")  # Updated relationship

class Trackpoint(Base):
    __tablename__ = "trackpoints"
    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id"))
    latitude = Column(Float)
    longitude = Column(Float)
    time = Column(String)
    starttime = Column(String)

    competitor = relationship("Competitor", back_populates="trackpoints")

# Classes Pydantic para validação
class EnduroCreate(BaseModel):
    name: str
    location: str
    date: str
    hora_largada: str

    @validator('hora_largada')
    def validate_hora_largada(cls, value):
        if value == '':
            raise ValueError("A hora não pode estar vazia.")
        try:
            datetime.strptime(value, '%H:%M:%S')
        except ValueError:
            raise ValueError("A hora deve estar no formato HH:MM:SS.")
        return value

class CompetitorCreate(BaseModel):
    enduro_id: int
    name: str
    placa: str
    categories_id: int

class CompetitorResponse(BaseModel):
    id: int
    enduro_id: int
    name: str
    placa: str
    categories_id: int

class CheckpointCreate(BaseModel):
    enduro_id: int
    competitor_id: int
    name: str
    time: float
    latitude: float
    longitude: float
    raio: int

class CategoryCreate(BaseModel):
    enduro_id: int
    name: str

class ResultadosCreate(BaseModel):
    competitor_id: int
    enduro_id: int
    checkpoint_id: int  # Added checkpoint_id
    latitude: float
    longitude: float
    raio: int
    time: float
    starttime: str

    @validator('starttime')
    def validate_starttime(cls, value):
        if value == '':
            raise ValueError("O horário de início não pode estar vazio.")
        try:
            datetime.strptime(value, '%H:%M:%S')
        except ValueError:
            raise ValueError("O horário de início deve estar no formato HH:MM:SS.")
        return value

class TrackpointCreate(BaseModel):
    competitor_id: int
    latitude: float
    longitude: float
    time: str
    starttime: str

    @validator('time')
    def validate_time(cls, value):
        if value == '':
            raise ValueError("O horário não pode estar vazio.")
        try:
            datetime.strptime(value, '%H:%M:%S')
        except ValueError:
            raise ValueError("O horário deve estar no formato HH:MM:SS.")
        return value

class UpdatePC(BaseModel):
    pc: int
    placa: str
    hora: str

    @validator('hora')
    def validate_hora(cls, value):
        if value == '':
            raise ValueError("A hora não pode estar vazia.")
        try:
            datetime.strptime(value, '%H:%M:%S')
        except ValueError:
            raise ValueError("A hora deve estar no formato HH:MM:SS.")
        return value

class UpdatePCList(BaseModel):
    updates: List[UpdatePC]

class ResultadoComparacao(BaseModel):
    checkpoint_id: int
    latitude: float
    longitude: float
    time: str  # Formato ISO 8601 (ex: "2024-03-05T14:00:00")
    distancia: float

# Criar tabelas no banco de dados
Base.metadata.create_all(bind=engine)