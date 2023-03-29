from sqlalchemy.orm import Session, query
from sqlalchemy import insert
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring
from orm import StatusEnum, Account, Order, Executed, Position
from db import *


def InsertAccount(session, id, in_balance, res):
    # check account if exist
    exists = session.query(Account).filter_by(
        account_id=id).scalar() is not None
    if not exists:
        new_account = Account(account_id=id, balance=in_balance)
        session.add(new_account)
        session.commit()
    # now need to generate relevant response
        ET.SubElement(res, 'created', {'id': str(id)})
    else:
        err = ET.SubElement(res, 'error', {'id': str(id)})
        err.text = 'account id has already exist'
  


def InsertPosition(session, sym, id, amount, res):
    Position_exists = session.query(Position).filter_by(
        account_id=id, symbol=sym).scalar() is not None
    Account_exists = session.query(Account).filter_by(
        account_id=id).scalar() is not None
    if not Account_exists:
        err = ET.SubElement(res, 'error', {'sym': sym, 'id': str(id)})
        err.text = 'account id is not exists, please create account first'

    else:
        if amount < 0:
            err = ET.SubElement(res, 'error', {'sym': sym, 'id': str(id)})
            err.text = 'amount is lower than 0, but short position is forbidden'
        else:
            if Position_exists:
                # just update relevant amount
                position = session.query(Position).filter_by(
                    account_id=id, symbol=sym).first()
                position.amount += amount
                session.commit()
            else:
                new_position = Position(
                    account_id=id, amount=amount, symbol=sym)
                session.add(new_position)
                session.commit()
        ET.SubElement(res, 'created', {'sym': sym, 'id': str(id)})
 


if __name__ == "__main__":
    engine = connectDB()
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    # now begin our test
    res = ET.Element('results')
    InsertAccount(session, 101, 2000, res)
    InsertPosition(session, "APPLE", 102, 1000, res)
    print(tostring(res))

