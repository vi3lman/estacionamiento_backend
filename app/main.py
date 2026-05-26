from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .database import get_db, engine
from .models import *
from .crud import *
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


@app.get("/calles", response_model=list[CalleRead])
def read_calles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    calles = get_calles(db, skip=skip, limit=limit)
    return calles


@app.get("/conductores", response_model=list[ConductorRead])
def get_conductores_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_conductores(db, skip=skip, limit=limit)

@app.get("/espacios/{id_calle}", response_model=list[EspacioRead])
def read_espacios_por_calle(id_calle: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    espacios = get_espacios_por_calle(db, id_calle=id_calle, skip=skip, limit=limit)
    return espacios

@app.get("/espacios/libres/{id_calle}", response_model=list[EspacioRead])
def get_espacios_libres_por_calle_endpoint(id_calle: int, fecha_hora_ingreso: datetime, tiempo_estimado: int, db: Session = Depends(get_db)):
    if fecha_hora_ingreso < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="La fecha y hora de ingreso no puede ser en el pasado."
        )
    espacios_libres = get_espacios_libres_por_calle(db=db, id_calle=id_calle, fecha_hora_ingreso=fecha_hora_ingreso, tiempo_estimado=tiempo_estimado)
    return espacios_libres

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

@app.post("/calles", response_model=CalleRead)
def create_calle_endpoint(calle: CalleCreate, db: Session = Depends(get_db)):
    return create_calle(db=db, calle=calle)

@app.post("/espacios", response_model=EspacioRead)
def create_espacio_endpoint(espacio: EspacioCreate, db: Session = Depends(get_db)):
    return create_espacio(db=db, espacio=espacio)

@app.post("/ocupaciones")
def crear_ocupacion(ocupacion: OcupacionCreate,db: Session = Depends(get_db)):
     # 1. Validar que el espacio pertenezca a la calle seleccionada
    if not espacio_pertenece_a_calle(
        db=db,
        id_espacio=ocupacion.id_espacio,
        id_calle=ocupacion.id_calle
    ):
        raise HTTPException(
            status_code=400,
            detail="El espacio seleccionado no pertenece a la calle indicada."
        )
     # 2. Validar que el espacio no esté ocupado en el horario solicitado
    ocupado = espacio_esta_ocupado(
        db=db,
        id_espacio=ocupacion.id_espacio,
        fecha_hora_ingreso=ocupacion.fecha_hora_inicio,
        tiempo_estimado=ocupacion.tiempo_estimado
    )
    if ocupado:
        raise HTTPException(
            status_code=409,
            detail="El espacio ya está ocupado en ese horario o la fecha ingresada no es válida."
        )
    return create_ocupacion(db, ocupacion)


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

@app.post("/ocupaciones/{id_ocupacion}/cancelar", response_model=OcupacionRead)
def cancelar_ocupacion_endpoint(id_ocupacion: int, db: Session = Depends(get_db)):
    ocupacion_cancelada = cancelar_ocupacion(db=db, id_ocupacion=id_ocupacion)
    
    if not ocupacion_cancelada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"No se encontró la ocupación con id {id_ocupacion} o ya fue finalizada/cancelada."
        )
        
    return ocupacion_cancelada

@app.post("/ocupaciones/{id_ocupacion}/modificar", response_model=OcupacionRead)
def modificar_ocupacion_endpoint(id_ocupacion: int, nueva_fecha_hora_inicio: datetime, nuevo_tiempo_estimado: int, db: Session = Depends(get_db)):
    ocupacion_modificada = modificar_ocupacion(db=db, id_ocupacion=id_ocupacion, nueva_fecha_hora_inicio=nueva_fecha_hora_inicio, nuevo_tiempo_estimado=nuevo_tiempo_estimado)

    if not ocupacion_modificada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró la ocupación con id {id_ocupacion}."
        )
    
    if datetime.now() > nueva_fecha_hora_inicio - timedelta(hours=8):
        raise HTTPException(
            status_code=400,
            detail="La ocupación solo puede ser modificada con al menos 8 horas de anticipación."
        ) 

    return ocupacion_modificada
