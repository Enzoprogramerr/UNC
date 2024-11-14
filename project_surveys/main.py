from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import os
from config import *
from sqlalchemy.sql import text
from typing import List
from pydantic import BaseModel

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

"""Base = declarative_base() 
class Respuesta(Base): 
    __tablename__ = "respuestas" 
    id = Column(Integer, primary_key=True, index=True) 
    respuesta = Column(Text, nullable=False) 
    fecha = Column(Integer, nullable=False) 
    encuestado = Column(String(255), nullable=False)
    pregunta = Column(Integer, nullable=False, comment='clave foranea - id pregunta') 
    encuesta = Column(Integer, nullable=False, comment='clave foranea - id encuesta') # Crear la tabla en la base de datos Base.metadata.create_all(bind=engine)
"""
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()

class Docente(BaseModel):
    id: int
    apellido: str
    nombre: str
    dni: str
    email: str

    class Config:
        orm_mode = True
      
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
    finally:
        db.close()

@app.get("/docentes/",
response_model=List[Docente])
def read_docentes(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM docente"))
    docentes = result.fetchall()
    db.close()
    return docentes

class DocenteSimple(BaseModel):
     apellido: str 
     nombre: str

@app.get("/docente/{docente_id}", response_model=DocenteSimple)
def get_docente(docente_id: int, db: Session = Depends(get_db)):
    result = db.execute(text("SELECT apellido, nombre FROM docente WHERE id = :id"), {"id": docente_id})
    docente = result.fetchone()
    if not docente:
        raise HTTPException(status_code=404, detail="Docente no encontrado")
    db.close()
    return {"apellido": docente[0], "nombre": docente[1]}
    


class Respuesta(BaseModel):
    respuesta: str
    fecha: int
    encuestado: str  # Nuevo campo

    class Config:
        from_attributes = True 

@app.post("/respuestas/")
def create_respuesta(respuesta: Respuesta, db: Session = Depends(get_db)):
    try:
        id_pregunta = 1  
        id_encuesta = 2  
        
        query = text(
            "INSERT INTO respuestas (respuesta, fecha, encuestado, pregunta, encuesta) "
            "VALUES (:respuesta, :fecha, :encuestado, :pregunta, :encuesta)"
        )
        db.execute(query, {
            "respuesta": respuesta.respuesta,
            "fecha": respuesta.fecha,  
            "pregunta": id_pregunta,
            "encuesta": id_encuesta,
            "encuestado": respuesta.encuestado # Nuevo campo añadido
        })
        db.commit()
        return {"message": "Respuesta guardada exitosamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar respuesta: {e}")
    finally:
        db.close()


class EspacioCurricular(BaseModel):
    nombre: str

    class Config:
        orm_mode = True

@app.post("/espacio_curricular/")
def create_espacio_curricular(db: Session = Depends(get_db)):
    try:
        nombre = "Ramiro"
        plan_estudio = "semestral"
        anio = 2024
        carrera = "Desarrollo de Software"
        
        query = text(
            "INSERT INTO espacio_curricular (nombre, plan_estudio, anio, carrera) "
            "VALUES (:nombre, :plan_estudio, :anio, :carrera)"
        )
        db.execute(query, {
            "nombre": nombre,
            "plan_estudio": plan_estudio,
            "anio": anio,
            "carrera": carrera
        })
        db.commit()
        return {"message": "Respuesta guardada exitosamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar respuesta: {e}")
    finally:
        db.close()

@app.get("/espacio_curricular/{espacio_id}", response_model=EspacioCurricular)
def get_espacio_curricular(espacio_id: int, db: Session = Depends(get_db)):
    result = db.execute(text("SELECT nombre FROM espacio_curricular WHERE id = :id"), {"id": espacio_id})
    espacio = result.fetchone()
    if not espacio:
        raise HTTPException(status_code=404, detail="Espacio curricular no encontrado")
    db.close()
    return {"nombre":espacio[0]}

class EncuestaOut(BaseModel):
    docente_id: int
    espacio_id: int

    class Config:
        orm_mode = True

#FALTA AGREGAR EL ENDPOINT PARA HACER UN REGISTRO DE LA TABLA ENCUESTA Y PROBAR EL GET DE ABAJO.

@app.get("/encuesta/{encuesta_id}", response_model=EncuestaOut)
def get_encuesta(encuesta_id: int, db: Session = Depends(get_db)):
    result = db.execute(text("SELECT docente_id, espacio_id FROM encuesta WHERE id = :id"), {"id": encuesta_id})
    encuesta = result.fetchone()
    if not encuesta:
        raise HTTPException(status_code=404, detail="Encuesta no encontrada")
    db.close()
    return {"docente_id": encuesta.docente_id, "espacio_id": encuesta.espacio_id}




