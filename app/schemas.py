from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import Optional


#schemas para las entidades principales: Calle, Espacio, Vehiculo, Conductor
class CalleBase(BaseModel):
    nombre_calle: str

class CalleCreate(CalleBase):
    pass # No se necesitan campos adicionales para crear una calle

class CalleRead(CalleBase):
    id_calle: int
    class Config:
        from_attributes = True

class EspacioBase(BaseModel):
    id_calle: int
    #nro_espacio: int ya se encarga el crud

class EspacioCreate(EspacioBase):
    pass

class EspacioRead(EspacioBase):
    id_espacio: int
    nro_espacio: int
    class Config:
        from_attributes = True

class VehiculoBase(BaseModel):
    chapa: str
    tipo: str

class VehiculoCreate(VehiculoBase):
    pass

class VehiculoRead(VehiculoBase):
    id_vehiculo: int
    class Config:
        from_attributes = True

class ConductorBase(BaseModel):
    nombre: str
    nro_documento: str

class ConductorCreate(ConductorBase):
    pass

class ConductorRead(ConductorBase):
    id_conductor: int
    class Config:
        from_attributes = True


#schemas para la ocupacion
class OcupacionBase(BaseModel):
    id_espacio: int
    id_vehiculo: int
    id_conductor: int
    tiempo_estimado: int
    fecha_hora_inicio: datetime
    #fecha_hora_fin_real: Optional[datetime] = None
    #estado: str = "confirmado" # por defecto, al crear una ocupacion, el estado es "confirmado"

class OcupacionCreate(OcupacionBase):
    pass

class OcupacionRead(OcupacionBase):
    id_ocupacion: int
    fecha_hora_fin: datetime # se calcula a partir de fecha_hora_inicio + tiempo_estimado
    estado: str
    fecha_hora_fin_real: Optional[datetime] = None
    class Config:
        from_attributes = True



#schemas para la tarifa y factura, que se generan a partir de la ocupacion
class TarifaBase(BaseModel):
    id_ocupacion: int
    monto_tarifa_base: Decimal
    monto_multa: Decimal = Decimal("0.00")
    estado_multa: str = "NO APLICA"

class TarifaCreate(TarifaBase):
    pass

class TarifaRead(TarifaBase):
    id_tarifa: int
    class Config:
        from_attributes = True

class FacturaBase(BaseModel):
    id_tarifa: int
    id_conductor: int
    nro_factura: str
    ruc: str
    monto_total: Decimal
    fecha_emision: datetime

class FacturaCreate(FacturaBase):
    pass

class FacturaRead(FacturaBase):
    id_factura: int
    class Config:
        from_attributes = True
