from .schemas import *
from .models import Ocupacion, Tarifa, Conductor, Vehiculo, Espacio, Calle
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import timedelta
from decimal import Decimal
from datetime import datetime
from typing import List, Dict, Optional

# CRUD para Calle
def create_calle(db: Session, calle: CalleCreate):
    db_calle = Calle(nombre_calle=calle.nombre_calle)
    db.add(db_calle)
    db.commit()
    db.refresh(db_calle)
    return db_calle

def get_calles(db: Session, skip: int = 0, limit: int = 100)->list[Calle]:
    return db.query(Calle).offset(skip).limit(limit).all()

# CRUD para Espacio
def create_espacio(db: Session, espacio: EspacioCreate)->Espacio:
    nro_espacio_anterior = db.query(Espacio).filter(Espacio.id_calle == espacio.id_calle).order_by(Espacio.nro_espacio.desc()).first()
    if nro_espacio_anterior:
        nuevo_nro_espacio = nro_espacio_anterior.nro_espacio + 1
    else:
        nuevo_nro_espacio = 1
    db_espacio = Espacio(id_calle=espacio.id_calle, nro_espacio=nuevo_nro_espacio)
    db.add(db_espacio)
    db.commit()
    db.refresh(db_espacio)
    return db_espacio
    
def get_espacios(db: Session, skip: int = 0, limit: int = 100)->list[Espacio]:
    return db.query(Espacio).offset(skip).limit(limit).all()

def get_espacios_por_calle(db: Session, id_calle: int, skip: int = 0, limit: int = 100)->list[Espacio]:
    return db.query(Espacio).filter(Espacio.id_calle == id_calle).offset(skip).limit(limit).all()


# CRUD para Vehiculo
def create_vehiculo(db: Session, vehiculo: VehiculoCreate) -> Vehiculo:
    chapa_normalizada = vehiculo.chapa.strip().upper()

    db_vehiculo = db.query(Vehiculo).filter(
        Vehiculo.chapa == chapa_normalizada
    ).first()

    if db_vehiculo:
        return db_vehiculo

    db_vehiculo = Vehiculo(
        chapa=chapa_normalizada,
        tipo=vehiculo.tipo
    )

    db.add(db_vehiculo)
    db.flush()

    return db_vehiculo
def get_espacios_libres_por_calle(db: Session, id_calle: int, fecha_hora_ingreso: datetime, tiempo_estimado: int)->list[Espacio]:
    espacios = db.query(Espacio).filter(Espacio.id_calle == id_calle).all()
    espacios_libres: list[Espacio]= []
    for espacio in espacios:
        if not espacio_esta_ocupado(db, espacio.id_espacio, fecha_hora_ingreso, tiempo_estimado):
            espacios_libres.append(espacio)
    return espacios_libres


def espacio_esta_ocupado(db: Session, id_espacio: int, fecha_hora_ingreso: datetime, tiempo_estimado: int)->bool:
    if fecha_hora_ingreso < datetime.now():
        return True
    fecha_hora_fin_estimada = fecha_hora_ingreso + timedelta(minutes=tiempo_estimado)
    tolerancia_minutos = timedelta(minutes=5)  # Tolerancia de 5 minutos
    ocupaciones = db.query(Ocupacion).filter(
        Ocupacion.id_espacio == id_espacio,
        Ocupacion.estado == "confirmado",
        Ocupacion.fecha_hora_fin_real == None,
        or_(
            and_(Ocupacion.fecha_hora_inicio <= fecha_hora_ingreso, Ocupacion.fecha_hora_fin + tolerancia_minutos > fecha_hora_ingreso),
            and_(Ocupacion.fecha_hora_inicio < fecha_hora_fin_estimada, Ocupacion.fecha_hora_fin + tolerancia_minutos >= fecha_hora_fin_estimada),
            and_(Ocupacion.fecha_hora_inicio >= fecha_hora_ingreso, Ocupacion.fecha_hora_fin + tolerancia_minutos <= fecha_hora_fin_estimada)
        )
    ).all()
    return len(ocupaciones) > 0


# CRUD para Vehiculo

def get_vehiculos(db: Session, skip: int = 0, limit: int = 100)->list[Vehiculo]:
    return db.query(Vehiculo).offset(skip).limit(limit).all()

# CRUD para Conductor
def create_conductor(db: Session, conductor: ConductorCreate)->Conductor:
    nro_documento_normalizado = conductor.nro_documento.strip()

    db_conductor = db.query(Conductor).filter(
        Conductor.nro_documento == nro_documento_normalizado
    ).first()

    if db_conductor:
        return db_conductor

    db_conductor = Conductor(
        nombre=conductor.nombre.strip(),
        nro_documento=nro_documento_normalizado
    )

    db.add(db_conductor)
    db.flush()

    return db_conductor

def get_conductores(db: Session, skip: int = 0, limit: int = 100)->list[Conductor]:
    return db.query(Conductor).offset(skip).limit(limit).all()

# CRUD para Ocupacion
#aqui se crea la ocupacion y la tarifa correspondiente
def create_ocupacion(db: Session, ocupacion: OcupacionCreate) -> Ocupacion:
    try:
        # 1. Crear vehículo
        db_vehiculo = create_vehiculo(db, ocupacion.vehiculo)

        # 2. Crear conductor
        db_conductor = create_conductor(db, ocupacion.conductor)

        db.add(db_conductor)
        db.flush()

        # 3. Calcular fecha de fin
        fecha_hora_fin = ocupacion.fecha_hora_inicio + timedelta(
            minutes=ocupacion.tiempo_estimado
        )

        # 4. Crear ocupación
        db_ocupacion = Ocupacion(
            id_calle=ocupacion.id_calle,
            id_espacio=ocupacion.id_espacio,
            id_vehiculo=db_vehiculo.id_vehiculo,
            id_conductor=db_conductor.id_conductor,
            tiempo_estimado=ocupacion.tiempo_estimado,
            fecha_hora_inicio=ocupacion.fecha_hora_inicio,
            fecha_hora_fin=fecha_hora_fin,
            estado="confirmado"
        )

        db.add(db_ocupacion)
        db.flush()
        

        # 5. Crear tarifa automáticamente
        monto_base = calcular_tarifa_precio(db, db_ocupacion.tiempo_estimado)

        db_tarifa = Tarifa(
            id_ocupacion=db_ocupacion.id_ocupacion,
            monto_tarifa_base=monto_base,
            estado_multa="NO APLICA",
            monto_multa=Decimal("0.00")
        )

        db.add(db_tarifa)
        db.flush()

        # 6. Confirmar todo junto
        db.commit()
        db.refresh(db_ocupacion)

        return db_ocupacion

    except Exception as e:
        db.rollback()
        raise e

def get_ocupaciones(db: Session, skip: int = 0, limit: int = 100)->list[Ocupacion]:
    return db.query(Ocupacion).offset(skip).limit(limit).all()



def get_ocupaciones_por_conductor(db: Session, id_conductor: int) -> List[Dict]:

    resultados = (
        db.query(Ocupacion, Espacio, Calle, Vehiculo, Tarifa)
        .join(Espacio, Ocupacion.id_espacio == Espacio.id_espacio)
        .join(Calle, Espacio.id_calle == Calle.id_calle)
        .join(Vehiculo, Ocupacion.id_vehiculo == Vehiculo.id_vehiculo)
        .join(Tarifa, Ocupacion.id_ocupacion == Tarifa.id_ocupacion)
        .filter(Ocupacion.id_conductor == id_conductor)
        .all()
    )


    lista_ocupaciones = []


    for ocupacion, espacio, calle, vehiculo, tarifa in resultados:
        lista_ocupaciones.append({
            "id_ocupacion": ocupacion.id_ocupacion,
            "nombre_calle": calle.nombre_calle,
            "numero_espacio": espacio.nro_espacio,
            "chapa_vehiculo": vehiculo.chapa,
            "tiempo_estimado": ocupacion.tiempo_estimado,
            "fecha_hora_inicio": ocupacion.fecha_hora_inicio,
            "fecha_hora_fin": ocupacion.fecha_hora_fin,
            "fecha_hora_fin_real": ocupacion.fecha_hora_fin_real,
            "estado": ocupacion.estado,
            "monto_tarifa_base": tarifa.monto_tarifa_base,
            "estado_multa": tarifa.estado_multa,
            "monto_multa": tarifa.monto_multa,
            "monto_total": tarifa.monto_tarifa_base + tarifa.monto_multa
        })
    return lista_ocupaciones

def create_tarifa(db: Session, id_ocupacion: int)-> Optional[Tarifa]:
    db_ocupacion = db.query(Ocupacion).filter(Ocupacion.id_ocupacion == id_ocupacion).first()
    if db_ocupacion:
        precio = calcular_tarifa_precio(db, db_ocupacion.tiempo_estimado)
        db_tarifa = Tarifa(id_ocupacion=id_ocupacion, precio=precio, estado_multa="NO APLICA", monto_multa=0.00)
        db.add(db_tarifa)
        db.commit()
        db.refresh(db_tarifa)
        return db_tarifa
    return None

def calcular_tarifa_precio(db: Session, tiempo_estimado: int)->Decimal:
    tarifa_base = 5.00  # Tarifa base por estacionamiento
    tarifa_por_minuto = 0.50  # Tarifa adicional por minuto
    return Decimal(str(tarifa_base + (tarifa_por_minuto * tiempo_estimado)))


def marcar_salida_ocupacion(db: Session, id_ocupacion: int)->Optional[Ocupacion]:
    db_ocupacion = db.query(Ocupacion).filter(Ocupacion.id_ocupacion == id_ocupacion).first()
    fecha_hora_fin_real = datetime.now()
    if db_ocupacion:
        db_ocupacion.fecha_hora_fin_real = fecha_hora_fin_real
        db_ocupacion.estado = "finalizado"



        if  fecha_hora_fin_real > db_ocupacion.fecha_hora_fin:
            db_ocupacion.tarifa.estado_multa = "aplica"
            db_ocupacion.tarifa.monto_multa = calcular_multa(db_ocupacion.fecha_hora_fin_real, db_ocupacion.fecha_hora_fin)

        db.commit()
        db.refresh(db_ocupacion)    
    return db_ocupacion

def calcular_multa(fecha_hora_fin_real: datetime, fecha_hora_fin: datetime)->Decimal:
    minutos_excedidos = (fecha_hora_fin_real - fecha_hora_fin).total_seconds() / 60   
    multa_por_minuto = 1.00  # Monto de la multa por minuto excedido
    return Decimal(str(minutos_excedidos * multa_por_minuto))



def reportar_infraccion(db: Session, id_espacio: int)->Optional[Ocupacion]:
    db_ocupacion = db.query(Ocupacion).filter(
        Ocupacion.id_espacio == id_espacio,
        Ocupacion.estado == "confirmado",
        Ocupacion.fecha_hora_fin_real == None,
        Ocupacion.fecha_hora_fin < datetime.now()
    ).first()
    if db_ocupacion:
        db_ocupacion.estado = "cancelado"
        db_ocupacion.tarifa.estado_multa = "aplica"
        db_ocupacion.tarifa.monto_multa = calcular_multa(datetime.now(), db_ocupacion.fecha_hora_fin)
        db.commit()
        db.refresh(db_ocupacion)
        return db_ocupacion
    return None



def get_conductores(db: Session, skip: int = 0, limit: int = 100)->list[Conductor]:
    return db.query(Conductor).offset(skip).limit(limit).all()