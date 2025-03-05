from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from datetime import datetime




# Dependência para obter a sessão do banco de dados

DATABASE_URL = "sqlite:///./enduro.db"
       
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

from fastapi import HTTPException

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

        
        

    
  
