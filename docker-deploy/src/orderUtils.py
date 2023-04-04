from orm import *
from db import *
from sqlalchemy.orm import query, Session, sessionmaker
from myException import *
import time
from xml.etree.ElementTree import tostring
import xml.etree.ElementTree as ET

# 自己创建的order自己应该不能搜索到吧？


'''
@Desc   : unit test function for transaction
@Arg    : session: session of database conn, amount: transaction amount, 
          limit: limit price, account_id: account_id of owner
@Return : void
'''
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


'''
@Desc   : create the transaction and block transaction resources
@Arg    : session: session of database conn, amount: transaction amount, 
          limit: limit price, account_id: account_id of owner
@Return : if success, return the id of created transaction
@Excep  : Account doesn't exist, balance insufficient, position insufficient
'''
def createOrder(session, amount, price, sym, uid):
    # check user existence
    
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


'''
@Desc   : make transaction of specific order until no suitbale order or transaction is executed
@Arg    : session: session of database conn, od_id: id of the transaction
@Return : void
'''
def makeTransaction(session, od_id):
    match_id = matchOrder(session, od_id)
    while match_id != -1:
        executeOrder(session, od_id, match_id)
        match_id = matchOrder(session, od_id)


'''
@Desc   : find the match order which 
            1. status is open
            2. match the price best and time second 
            3. have same symbol
            4. not create by same account
@Arg    : session: session of database conn, od_id: id of the transaction
@Return : best matching transaction id if success, 
          -1 when the transaction is not open or no matching transaction
'''
def matchOrder(session, od_id):
    od = session.query(Order).get(od_id)

    # if order is not open
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


'''
@Desc   : excute the 2 transactions by   
            1. determine executed price
            2. modify the position of two account
            3. modify order amount and status if needed
            4. create executed for two orders
            5. modify the balance of both buy and sell account
@Arg    : session: session of database conn, new_id: trans_id of the newer created transaction
          old_id: trans_id of the matched transaction
@Return : void
'''
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

    if refund > 0:
        modifyBalance(session, buy.account_id, refund)
    modifyBalance(session, sell.account_id, price * exe_amount)


'''
@Desc   : modify the balance of account by specifioc change
@Arg    : session: database session conn, uid: account_id want to modify, change: modify amount(+ for add, - for minus)
@Return : void
@Excep  : User not exist, Insufficient Balance
'''
def modifyBalance(session, uid, change):
    user = session.query(Account).get(uid)
    if user == None:
        raise ArgumentError('User not exist')
    
    user.balance += change
    if user.balance < 0:
        raise ArgumentError('Insufficient Balance')
    
    session.commit()


'''
@Desc   : modify the sym position of account by specifioc change
@Arg    : session: database session conn, sym: symbol want to change, 
          uid: account_id want to modify, change: modify amount(+ for add, - for minus)
@Return : void
@Excep  : Position not exist, Insufficient Share Amount
'''
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


'''
@Desc   : add executed for the order
@Arg    : session: session of database conn, amount: executed amount, 
          price: executed price, order_id: trans_id, time: executed time
@Return : void
'''
def addExecuted(session, amount, price, order_id, time):
    newExe = Executed(order_id = order_id, price = price, amount = amount, time = time)
    session.add(newExe)
    session.commit()


def CancelOrder(session, id, res):
    Order_exists = session.query(Order).filter_by(
        tran_id=id).scalar() is not None
    if Order_exists:
        order = session.query(Order).filter_by(
            tran_id=id).first()
        if order.status == StatusEnum.open:
            # change the status to cancel and refund immediately
            order.status = "canceled"
            # refund money to account
            if order.remain_amount >= 0:
                # calculate the money that need to refund
                refund_money = order.limit_price * order.remain_amount
                modifyBalance(session, order.account_id, refund_money)

            # refund stock to position
            else:
                refund_amount = order.remain_amount
                modifyPosition(session, order.symbol,
                               order.account_id, refund_amount)

            # once done refund and status change, update response
            under_cancel = ET.SubElement(res, 'canceled', {'id': str(id)})
            # get all new status of this order
            # first load cancel status
            ET.SubElement(under_cancel, 'canceled', {
                          'shares': str(order.remain_amount), 'time': str(order.time)})
            all_excuted = session.query(Executed).filter_by(
                order_id=id).all()
            for execute in all_excuted:
                ET.SubElement(under_cancel, 'executed', {
                    'shares': str(execute.amount), 'price': str(execute.price), 'time': str(execute.time)})

            session.commit()

        elif order.status == StatusEnum.executed:
            # deal with error cannot cancel a executed order
            error = ET.SubElement(res, 'error', {'id': str(id)})
            error.text = "order has been all executed, cannot be canceled"

        else:
           # print(order.status)
            error = ET.SubElement(res, 'error', {'id': str(id)})
            error.text = "order has been canceled already, cannot be canceled again"
    else:
        error = ET.SubElement(res, 'error', {'id': str(id)})
        error.text = "order doesnot exists, please type in correct transaction id"


def QueryOrder(session, id, res):
    Order_exists = session.query(Order).filter_by(
        tran_id=id).scalar() is not None
    under_status = ET.SubElement(res, 'status', {'id': str(id)})
    all_excuted = session.query(Executed).filter_by(
        order_id=id)
    order = session.query(Order).filter_by(tran_id=id).first()
    if Order_exists:
        if order.status == StatusEnum.open:
            ET.SubElement(under_status, 'open', {
                'shares': str(order.remain_amount)})

        if order.status == StatusEnum.canceled:
            ET.SubElement(under_status, 'canceled', {
                'shares': str(order.remain_amount), 'time': str(order.time)})
        for execute in all_excuted:
            ET.SubElement(under_status, 'executed', {
                'shares': str(execute.amount), 'price': str(execute.price), 'time': str(execute.time)})
    else:
        error = ET.SubElement(res, 'error', {'id': str(id)})
        error.text = "order doesnot exists, please type in correct transaction id"


'''
@Desc   : combination test of the orderUtils class
@Arg    : void
@Return : void
'''
if __name__ == "__main__":
    engine = initDB()
    dropAllTable(engine)
    createAllTable(engine)
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    user1 = Account(account_id = 1, balance = 100000)
    user2 = Account(account_id = 2, balance = 300000)
    user3 = Account(account_id = 3, balance = 0)
    user4 = Account(account_id = 4, balance = 0)
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