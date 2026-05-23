# app/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship
# Importamos la Base declarativa desde tu archivo de configuración de base de datos
from .database import Base

class Calle(Base):
    __tablename__ = "calle"

    id_calle = Column(Integer, primary_key=True, index=True)
    nombre_calle = Column(String, nullable=False, unique=True)

    # Una relación para poder acceder a los espacios de esta calle desde Python de forma fácil
    # ej: mi_calle.espacios -> te devolverá una lista de objetos Espacio
    espacios = relationship("Espacio", back_populates="calle")


class Espacio(Base):
    __tablename__ = "espacio"

    id_espacio = Column(Integer, primary_key=True, index=True)
    id_calle = Column(Integer, ForeignKey("calle.id_calle", ondelete="CASCADE"), nullable=False)
    nro_espacio = Column(Integer, nullable=False)

    # Relaciones bidireccionales de SQLAlchemy para navegar entre objetos en Python
    calle = relationship("Calle", back_populates="espacios")

    # Configuración de los argumentos de la tabla: Aquí añadimos el Índice Único Compuesto
    # Esto equivale a tu: CREATE UNIQUE INDEX uq_espacio_calle ON public.espacio (id_calle, nro_espacio);
    __table_args__ = (
        UniqueConstraint("id_calle", "nro_espacio", name="uq_espacio_calle"),
    )

class Vehiculo(Base):
    __tablename__ = "vehiculo"

    id_vehiculo = Column(Integer, primary_key=True, index=True)
    chapa = Column(String, nullable=False, unique=True)
    tipo = Column(String, nullable=False)

class Conductor(Base):
    __tablename__ = "conductor"

    id_conductor = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    nro_documento = Column(String, nullable=False, unique=True)

class Ocupacion(Base):
    __tablename__ = "ocupacion"

    id_ocupacion = Column(Integer, primary_key=True, index=True)
    id_calle = Column(Integer, ForeignKey("calle.id_calle", ondelete="CASCADE"), nullable=False)
    id_espacio = Column(Integer, ForeignKey("espacio.id_espacio", ondelete="CASCADE"), nullable=False)
    id_vehiculo = Column(Integer, ForeignKey("vehiculo.id_vehiculo", ondelete="CASCADE"), nullable=False)
    id_conductor = Column(Integer, ForeignKey("conductor.id_conductor", ondelete="CASCADE"), nullable=False)
    tiempo_estimado = Column(Integer, nullable=False)  # Tiempo estimado en minutos
    fecha_hora_inicio = Column(DateTime, nullable=False)
    fecha_hora_fin = Column(DateTime, nullable=False) # se calcula a partir de fecha_hora_inicio + tiempo_estimado
    fecha_hora_fin_real = Column(DateTime) # cuando el conductor marca su salida
    estado = Column(String, nullable=False) # "confirmado", "cancelado", "finalizado"

    # Relaciones para navegar entre objetos en Python
    espacio = relationship("Espacio")
    vehiculo = relationship("Vehiculo")
    conductor = relationship("Conductor")
    tarifa = relationship("Tarifa", uselist=False, back_populates="ocupacion")
    calle= relationship("Calle") 

    __table_args__ = (
        UniqueConstraint("id_espacio", "fecha_hora_inicio", name="uq_ocupacion_espacio_tiempo"),
    )

class Tarifa(Base):
    __tablename__ = "tarifa"

    id_tarifa = Column(Integer, primary_key=True, index=True)
    id_ocupacion = Column(Integer, ForeignKey("ocupacion.id_ocupacion", ondelete="CASCADE"), nullable=False, unique=True)
    monto_tarifa_base = Column(Numeric(10, 2), nullable=False)  # Monto base de la tarifa
    monto_multa = Column(Numeric(10, 2), nullable=False, default=0.00)  # Monto de la multa por exceder el tiempo estimado
    estado_multa = Column(String, nullable=False, default="NO APLICA")  # "APLICA" o "PENDIENTE" o "PAGADA"

    # Relación para navegar entre objetos en Python
    ocupacion = relationship("Ocupacion", back_populates="tarifa", uselist=False)
    factura = relationship("Factura", uselist=False, back_populates="tarifa")

class Factura(Base):
    __tablename__ = "factura"

    id_factura = Column(Integer, primary_key=True, index=True)
    id_tarifa = Column(Integer, ForeignKey("tarifa.id_tarifa", ondelete="CASCADE"), nullable=False, unique=True)
    id_conductor = Column(Integer, ForeignKey("conductor.id_conductor", ondelete="CASCADE"), nullable=False)
    nro_factura = Column(String, nullable=False, unique=True)  # Número de factura único
    ruc = Column(String, nullable=False)  # RUC del conductor
    monto_total = Column(Numeric(10, 2), nullable=False)  # Monto total a pagar
    fecha_hora_emision = Column(DateTime, nullable=False)  # Fecha y hora de emisión de la factura

    # Relación para navegar entre objetos en Python
    conductor = relationship("Conductor")  
    tarifa = relationship("Tarifa", back_populates="factura", uselist=False)  