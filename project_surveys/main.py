"""app = FastAPI()

Recibe solicitudes HTTP en las rutas y archivos .//items/{item_id}
Ambas rutas toman operaciones (también conocidas como métodos HTTP).GET
La ruta tiene un parámetro path que debe ser un archivo ./items/{item_id}item_idint
La ruta de acceso tiene un parámetro de consulta opcional ./items/{item_id}strq

@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}"""
from typing import Union
from fastapi import FastAPI
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import os
from config import *

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()
        
@app.post("/docentes/")
def create_docente(apellido: str, nombre: str, dni: str, email: str, db: Session = Depends(get_db)):
    try:
        query = text("INSERT INTO docente (apellido, nombre, dni, email) VALUES (:apellido, :nombre, :dni, :email)")
        db.execute(query, {"apellido": apellido, "nombre": nombre, "dni": dni, "email": email})
        db.commit()
        return {"message": "Docente creado exitosamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear docente: {e}")

@app.get("/docentes/")
def read_docentes(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM docente"))
    docentes = result.fetchall()
    return docentes