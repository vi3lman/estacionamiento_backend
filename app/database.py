from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. URL de conexión a tu base de datos PostgreSQL
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/estacionamiento_db"

# 2. Creación del motor (Engine)
# El engine es el responsable de establecer la conexión real con Postgres
engine = create_engine(DATABASE_URL)

# 3. Fábrica de sesiones (SessionLocal)
# Crea un entorno de trabajo para hablar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Clase Base
# De esta clase heredarán todos nuestros modelos en el archivo models.py
Base = declarative_base()

# 5. Dependencia para FastAPI (Generador de base de datos)
def get_db():
    db = SessionLocal()
    try:
        yield db  # Entrega la sesión al endpoint que la pida
    finally:
        db.close()  # Se asegura de cerrar la conexión cuando el endpoint termina