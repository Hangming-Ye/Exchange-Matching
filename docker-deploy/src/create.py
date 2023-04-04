from sqlalchemy.orm import Session, query
from sqlalchemy import insert
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring
from orm import StatusEnum, Account, Order, Executed, Position, StatusEnum
from db import *
from orderUtils import *


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
                # position = session.query(Position).filter_by(
                #     account_id=id, symbol=sym).first()
                # position.amount += amount
                # concurency deal
                session.query(Position).filter_by(account_id=id, symbol=sym).first().update(
                    {"amount": Account.amount + 100})

                session.commit()
            else:
                new_position = Position(
                    account_id=id, amount=amount, symbol=sym)
                session.add(new_position)
                session.commit()
        ET.SubElement(res, 'created', {'sym': sym, 'id': str(id)})


def Naive_InsertAcc(session, id, in_balance):
    exists = session.query(Account).filter_by(
        account_id=id).scalar() is not None
    if not exists:
        new_account = Account(account_id=id, balance=in_balance)
        session.add(new_account)
        session.commit()


def Naive_InsertPos(session, sym, id, amount):
    Position_exists = session.query(Position).filter_by(
        account_id=id, symbol=sym).scalar() is not None
    Account_exists = session.query(Account).filter_by(
        account_id=id).scalar() is not None
    if not Account_exists:
        print('account id is not exists, please create account first')

    else:
        if amount < 0:
            print('amount is lower than 0, but short position is forbidden')
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


def Naive_InsertOrder(session, amount, price, sym, uid):
    order = Order(remain_amount=amount, limit_price=price, symbol=sym,
                  time=int(time.time()), account_id=uid, status='open')
    session.add(order)
    session.commit()
    return order.tran_id


def Naive_InsertExe(session, amount, price, order_id):
    print(order_id)
    newExe = Executed(order_id=order_id, price=price,
                      amount=amount, time=int(time.time()))
    session.add(newExe)
    session.commit()


if __name__ == "__main__":

    # create the ElementTree object
    engine = connectDB()
    dropAllTable(engine)
    initDB()
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    # now begin our test with create accout and create position
    res = ET.Element('results')
    # InsertAccount(session, 101, 2000, res)
    # InsertPosition(session, "APPLE", 102, 1000, res)
    # print(tostring(res))
    # now begin our test with cancel order and query order
    # before we start, first we need to insert some fake data in table
    Naive_InsertAcc(session, 1, 2000)
    Naive_InsertAcc(session, 2, 1000)
    Naive_InsertAcc(session, 3, 50)
    Naive_InsertPos(session, "APPLE", 1, 1000)
    Naive_InsertPos(session, "TESLA", 2, 50)
    Naive_InsertPos(session, "FACEBOOK", 3, 200)
    Naive_InsertPos(session, "LINKIN", 2, 0)
    u1_trsid = Naive_InsertOrder(session, 110, 330, "Meta", 1)
    u2_trsid = Naive_InsertOrder(session, 220, -50, "LINKIN", 2)
    u3_trsid = Naive_InsertOrder(session, 330, 69, "NISSAN", 3)
    print(type(u1_trsid))
    Naive_InsertExe(session, 100, 90, u1_trsid)
    Naive_InsertExe(session, 100, 99, u1_trsid)
    Naive_InsertExe(session, 100, 103, u1_trsid)
    Naive_InsertExe(session, 300, 230, u2_trsid)
    Naive_InsertExe(session, 300, 229, u2_trsid)
    Naive_InsertExe(session, 40, 79, u3_trsid)
    # now begin test query order
    QueryOrder(session, u1_trsid, res)
    QueryOrder(session, u2_trsid, res)
    QueryOrder(session, u3_trsid, res)
    # print(tostring(res))
    # now begin test cancel order
    CancelOrder(session, u1_trsid, res)
    CancelOrder(session, u2_trsid, res)
    # print(tostring(res))
    # now we need to see if the database is correctly edited
    # first we need to get relevant record
    account1 = session.query(Account).filter_by(
        account_id=1).first()
    print("account 1 's balance should be 2000+110*330=38300 ")
    print("database show " + str(account1.balance))
    account2 = session.query(Position).filter_by(
        account_id=2).all()
    for pos in account2:
        print(pos.symbol, " ", pos.amount)
    # create the ElementTree object
    tree = ET.ElementTree(res)

    # write the tree to a file
    print(tostring(res))
    tree.write("/home/ht175/ECE568/Exchange-Matching/docker-deploy/src/output.xml",
               xml_declaration=True, encoding='UTF-8')
