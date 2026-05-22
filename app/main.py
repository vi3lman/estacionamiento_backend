from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from .database import get_db, engine
from .models import *
from .crud import create_calle, create_espacio, get_calles, get_espacios_por_calle
from .schemas import *
from app import models


def create_tables():
    #models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)  # Base viene de models


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    print("--------------------------------------------------------------------")
    print("Servidor iniciado. Tablas creadas (si no existían).")
    print("--------------------------------------------------------------------")
    yield
    print("---------------------------------------------------------------------")
    print("Servidor detenido.")
    print("---------------------------------------------------------------------")          


app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de Estacionamiento"}


@app.get("/calles/", response_model=list[CalleRead])
def read_calles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    calles = get_calles(db, skip=skip, limit=limit)
    return calles

@app.get("/espacios/{id_calle}", response_model=list[EspacioRead])
def read_espacios_por_calle(id_calle: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    espacios = get_espacios_por_calle(db, id_calle=id_calle, skip=skip, limit=limit)
    return espacios





@app.post("/calles/", response_model=CalleRead)
def create_calle_endpoint(calle: CalleCreate, db: Session = Depends(get_db)):
    return create_calle(db=db, calle=calle)

@app.post("/espacios/", response_model=EspacioRead)
def create_espacio_endpoint(espacio: EspacioCreate, db: Session = Depends(get_db)):
    return create_espacio(db=db, espacio=espacio)