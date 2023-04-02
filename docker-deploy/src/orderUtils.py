from orm import *
from db import *
from sqlalchemy.orm import query, Session, sessionmaker
from myException import *
import time
from xml.etree.ElementTree import tostring
import xml.etree.ElementTree as ET
# 预扣款问题
# 自己创建的order自己应该不能搜索到吧？
# amount 为啥允许小数？
# 部分交易的时候， 如果buyer成交价格低于预付的价格，应当直接退款还是等到整个订单完成之后统一退款

def testMtd(session, amount, limit, sym, accout_id):
    res = ET.Element('results')
    try:
        od_id = createOrder(session, amount, limit, sym, accout_id)
    except ArgumentError as e:
        createError = ET.SubElement(res, 'error', {'sym': sym, 'amount':str(amount), 'limit':str(limit)})
        createError.text = e.msg
    else:
        ET.SubElement(res, 'opened', {'sym': sym, 'amount':str(amount), 'limit':str(limit), 'id':str(od_id)})
        makeTransaction(session, od_id)
    print(tostring(res))
    tree = ET.ElementTree(res)
    tree.write(str(accout_id)+".xml",xml_declaration=True,encoding='UTF-8')


def createOrder(session, amount, price, sym, uid):
    if session.query(Account).get(uid) is None:
        raise ArgumentError("Account does not exist")
    # buy order
    if amount > 0:
        modifyBalance(session, uid, -amount*price)
    #sell order
    elif amount < 0:
        modifyPosition(session, sym, uid, amount)
    # create order successfully
    order = Order(remain_amount = amount, limit_price = price, symbol = sym, time = int(time.time()), account_id = uid, status = StatusEnum.open)
    session.add(order)
    session.commit()
    return order.tran_id


def makeTransaction(session, od_id):
    match_id = matchOrder(session, od_id)
    while match_id != -1:
        executeOrder(session, od_id, match_id)
        match_id = matchOrder(session, od_id)


def matchOrder(session, od_id):
    od = session.query(Order).get(od_id)
    if od.status != StatusEnum.open:
        return -1

    allOrder = session.query(Order.tran_id).filter(Order.symbol==od.symbol, Order.status==StatusEnum.open)

    # buy order
    if od.remain_amount > 0:
        ans = allOrder.filter(Order.limit_price <= od.limit_price, Order.remain_amount < 0).order_by(Order.limit_price, Order.time).first()
    # sell order
    elif od.remain_amount < 0:
        ans = allOrder.filter(Order.limit_price >= od.limit_price, Order.remain_amount > 0).order_by(Order.limit_price.desc(), Order.time).first()

    # matched order find
    if ans != None:
        return ans
    # no matched order find
    else:
        return -1


def executeOrder(session, new_id, old_id):
    new = session.query(Order).get(new_id)
    old = session.query(Order).get(old_id)

    #determine sell and buy
    if new.remain_amount > 0:
        buy = new
        sell = old
    else:
        buy = old
        sell = new
    
    # determine execute price, amount and refund for buyer (if have)
    price  = old.limit_price
    exe_amount = min(buy.remain_amount, -sell.remain_amount)
    refund = (buy.limit_price - price) * exe_amount

    if refund > 0:
        modifyBalance(session, buy.account_id, refund)
    modifyBalance(session, sell.account_id, price * exe_amount)
    modifyPosition(session, buy.symbol, buy.account_id, exe_amount)

    exeTime = int(time.time())

    buy.remain_amount -= exe_amount
    if buy.remain_amount == 0:
        buy.status = StatusEnum.executed
    session.commit()

    sell.remain_amount += exe_amount
    if sell.remain_amount == 0:
        sell.status = StatusEnum.executed
    session.commit()

    addExecuted(session, exe_amount, price, buy.tran_id, exeTime)
    addExecuted(session, exe_amount, price, sell.tran_id, exeTime)


def modifyBalance(session, uid, change):
    user = session.query(Account).get(uid)
    if user == None:
        raise ArgumentError('User not exist')
    
    user.balance += change
    if user.balance < 0:
        raise ArgumentError('Insufficient Balance')
    
    session.commit()


def modifyPosition(session, sym, uid, change):
    stock = session.query(Position).filter(Position.account_id == uid, Position.symbol == sym).first()
    # position not find
    if stock == None:
        if change < 0:
            raise ArgumentError('Position not exist')
        elif change >= 0:
            newPos = Position(account_id = uid, amount = change, symbol = sym)
            session.add(newPos)
            session.commit()
            return
        
    stock.amount += change
    # position amount insufficient
    if stock.amount < 0:
        raise ArgumentError('Insufficient Share Amount')
    
    session.commit()


def addExecuted(session, amount, price, order_id, time):
    newExe = Executed(order_id = order_id, price = price, amount = amount, time = time)
    session.add(newExe)
    session.commit()
    
    
if __name__ == "__main__":
    engine = initDB()
    dropAllTable(engine)
    createAllTable(engine)
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    user1 = Account(balance = 100000)
    user2 = Account(balance = 300000)
    user3 = Account(balance = 0)
    user4 = Account(balance = 0)
    session.add(user1)
    session.add(user2)
    session.add(user3)
    session.add(user4)
    session.commit()

    pos3 = Position(account_id = 3, amount = 600, symbol = "BTC")
    pos4 = Position(account_id = 4, amount = 200, symbol = "BTC")
    session.add(pos3)
    session.add(pos4)
    session.commit()

    testMtd(session, -100, 130, "BTC", 4)
    testMtd(session, 200, 127, "BTC", 1)
    testMtd(session, 300, 125, "BTC", 2)
    testMtd(session, -400, 124, "BTC", 3)

    print("----USER  1-------")
    print(user1.dto())
    u1E = session.query(Position).filter(Position.account_id == 1).first()
    print(u1E.dto())

    print("----USER  2-------")
    print(user2.dto())
    u2E = session.query(Position).filter(Position.account_id == 2).first()
    print(u2E.dto())
    

    print("----USER  3-------")
    print(user3.dto())
    u3E = session.query(Position).filter(Position.account_id == 3).first()
    print(u3E.dto())

    print("----USER  4-------")
    print(user4.dto())
    u4E = session.query(Position).filter(Position.account_id == 4).first()
    print(u4E.dto())