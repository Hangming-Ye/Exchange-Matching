from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base
import psycopg2
from orm import *

def initDB():
    engine = create_engine("postgresql+psycopg2://postgres:passw0rd@0.0.0.0:5432/EM_SYSTEM",future=True)
    return engine

def createTable(engine):
    Base.metadata.create_all(engine)
    return

engine = initDB()
createTable(engine)