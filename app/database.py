from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

SQLALCHEMY_DATABASE_URL = f'postgresql+psycopg://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}' # +psycopg -> add to use psycopg3 instead of psycopg2

engine = create_engine(SQLALCHEMY_DATABASE_URL) # Устанавливает соединение с базой данных по указанному URL-адресу

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Создает фабрику сессий (класс-генератор объектов сессии)

Base = declarative_base() 
# Создает базовый класс для определения моделей (таблиц) в декларативном стиле
# Все классы-модели наследуются от Base (например, class User(Base): ...).
# SQLAlchemy использует этот класс для автоматического создания схемы таблиц (Base.metadata.create_all(engine)).

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()