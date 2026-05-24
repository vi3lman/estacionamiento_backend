from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .database import get_db, engine
from .models import *
from .crud import *
from .schemas import *
from app import models
from typing import Dict, List, Optional


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


# Endpoints para Calles y Espacios

@app.get("/calles", response_model=list[CalleRead])
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

@app.post("/espacios", response_model=EspacioRead)
def create_espacio_endpoint(espacio: EspacioCreate, db: Session = Depends(get_db)):
    return create_espacio(db=db, espacio=espacio)

@app.get("/espacios/libres/{id_calle}", response_model=list[EspacioRead])
def get_espacios_libres_por_calle_endpoint(id_calle: int, fecha_hora_ingreso: datetime, tiempo_estimado: int, db: Session = Depends(get_db)):
    if fecha_hora_ingreso < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="La fecha y hora de ingreso no puede ser en el pasado."
        )
    espacios_libres = get_espacios_libres_por_calle(db=db, id_calle=id_calle, fecha_hora_ingreso=fecha_hora_ingreso, tiempo_estimado=tiempo_estimado)
    return espacios_libres


#Todo lo relacionado con ocupaciones
@app.post("/ocupaciones")
def crear_ocupacion(ocupacion: OcupacionCreate,db: Session = Depends(get_db)):
    return create_ocupacion(db, ocupacion)

@app.get("/ocupaciones", response_model=list[OcupacionRead])
def get_ocupaciones_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_ocupaciones(db, skip=skip, limit=limit)

@app.get("/ocupaciones/{id_conductor}", response_model=list[Dict])
def get_ocupaciones_por_conductor_endpoint(id_conductor: int, db: Session = Depends(get_db)):
    ocupaciones = get_ocupaciones_por_conductor(db, id_conductor=id_conductor)
    if not ocupaciones:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontraron ocupaciones para el conductor con ID {id_conductor}."
        )
    return ocupaciones


@app.post("/espacios/{id_espacio}/infraccion", response_model=OcupacionRead)
def reportar_infraccion_endpoint(id_espacio: int, db: Session = Depends(get_db)):
    
    ocupacion_infractora = reportar_infraccion(db=db, id_espacio=id_espacio)
    
    if not ocupacion_infractora:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"No hay ocupación para el espacio {id_espacio} o el tiempo aún no ha expirado."
        )
    
    return ocupacion_infractora

@app.post("/ocupaciones/{id_ocupacion}/finalizar", response_model=OcupacionRead)
def marcar_salida_endpoint(id_ocupacion: int, db: Session = Depends(get_db)):
    ocupacion_finalizada = marcar_salida_ocupacion(db=db, id_ocupacion=id_ocupacion)
    
    if not ocupacion_finalizada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"No se encontró la ocupación con id {id_ocupacion} o ya fue finalizada."
        )
    
    return ocupacion_finalizada


@app.get("/conductores", response_model=list[ConductorRead])
def get_conductores_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_conductores(db, skip=skip, limit=limit)