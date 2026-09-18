from device_systems.database.connection import SessionLocal


def get_db():
    # Abrir una sesion para la peticion y cerrarla al terminar.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
