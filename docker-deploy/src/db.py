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

def getSession(engine):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    engine.dispose()
    return session

def dbInit():
    engine = connectDB()
    return getSession(engine)

def initDB():
    engine = connectDB()
    dropAllTable(engine)
    insp = inspect(engine)
    if not (insp.has_table("account") and insp.has_table("executed") and insp.has_table("order") and insp.has_table("position")):
        dropAllTable(engine)
        createAllTable(engine)
    return engine

if __name__ == "__main__":
    engine = connectDB()
    dropAllTable(engine)
    initDB()