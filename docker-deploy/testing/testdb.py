from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker, declarative_base
import psycopg2
from testorm import *

def connectDB():
    return create_engine("postgresql+psycopg2://postgres:passw0rd@0.0.0.0:5432/EM_SYSTEM")

def createAllTable(engine):
    Base.metadata.create_all(engine)

def dropAllTable(engine):
    Base.metadata.drop_all(engine)

def initDB():
    engine = connectDB()
    dropAllTable(engine)
    createAllTable(engine)

if __name__ == "__main__":
    engine = connectDB()
    dropAllTable(engine)
    initDB()