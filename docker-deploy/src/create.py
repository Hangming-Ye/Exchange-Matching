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


def CancelOrder(session, id, res):
    Order_exists = session.query(Order).filter_by(
        tran_id=id).scalar() is not None
    if Order_exists:
        order = session.query(Order).filter_by(
            tran_id=id).first()
        if order.status == "open":
            # change the status to cancel and refund immediately
            order.status = "canceled"
            # refund money to account
            if order.limit_price >= 0:
                # calculate the money that need to refund
                refund_money = order.limit_price * order.remain_amount
                refundMoney(session, refund_money, order.account_id)

            # refund stock to position
            else:
                refund_amount = order.remain_amount
                refundStock(session, refund_amount,
                            order.account_id, order.symbol)

            # once done refund and status change, update response
            under_cancel = ET.SubElement(res, 'canceled', {'id': str(id)})
            # get all new status of this order
            # first load cancel status
            ET.SubElement(under_cancel, 'canceled', {
                          'shares': str(order.remain_amount), 'time': order.time})
            all_excuted = session.query(Executed).filter_by(
                order_id=id).all
            for execute in all_excuted:
                #  ET.SubElement(under_cancel, 'executed', {
                #           'shares': str(execute.), 'price': ,time': order.time})
                print

            session.commit()

        elif order.status == "executed":
            print

        else:
            print


def queryExcuted(session, tran_id):
    all_excuted = session.query(Executed).filter_by(
        order_id=tran_id).all


def refundMoney(session, refund_money, account_id):
    print


def refundStock(session, refund_amount, account_id, symbol):
    print


if __name__ == "__main__":
    engine = connectDB()
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    # now begin our test
    res = ET.Element('results')
    InsertAccount(session, 101, 2000, res)
    InsertPosition(session, "APPLE", 102, 1000, res)
    print(tostring(res))
