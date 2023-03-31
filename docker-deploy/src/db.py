from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker, declarative_base
import psycopg2
from orm import *

def connectDB():
    return create_engine("postgresql+psycopg2://postgres:passw0rd@0.0.0.0:5432/EM_SYSTEM",future=True)

def createAllTable(engine):
    Base.metadata.create_all(engine)

def dropAllTable(engine):
    Base.metadata.drop_all(engine)

def initDB():
    engine = connectDB()
    insp = inspect(engine)
    if not (insp.has_table("account") and insp.has_table("executed") and insp.has_table("order") and insp.has_table("position")):
        dropAllTable(engine)
        createAllTable(engine)
    return engine

if __name__ == "__main__":
    engine = connectDB()
    dropAllTable(engine)
    initDB()