from orm import *
from db import *
from sqlalchemy.orm import query, Session, sessionmaker
from myException import *
import time
# 预扣款问题
# 自己创建的order自己应该不能搜索到吧？
# amount 为啥允许小数？
# 部分交易的时候， 如果buyer成交价格低于预付的价格，应当直接退款还是等到整个订单完成之后统一退款

def makeTransaction(session, amount, price, sym, uid):
    od_id = createOrder(session, amount, price, sym, uid)
    match_id = matchOrder(session, od_id)
    while match_id != -1:
        executeOrder(session, od_id, match_id)
        match_id = matchOrder(session, od_id)


def createOrder(session, amount, price, sym, uid):
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

def matchOrder(session, od_id):
    od = session.query(Order).get(od_id)
    if od.status != "open":
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
        return ans[0]
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
        modifyBalance(session, buy.uid, refund)
    modifyBalance(session, sell.uid, price * exe_amount)
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
        raise ArgumentError("User not exist")
    
    user.balance += change
    if user.balance < 0:
        raise ArgumentError("Insufficient Balance")
    
    session.commit()


def modifyPosition(session, sym, uid, change):
    stock = session.query(Position).filter(Position.account_id == uid, Position.symbol == sym).first()
    # position not find
    if stock == None:
        raise ArgumentError("Position not exist")
    
    stock = stock[0]
    stock.amount += change
    # position amount insufficient
    if stock.amount < 0:
        raise ArgumentError("Insufficient Share Amount")
    
    session.commit()

def addExecuted(session, amount, price, order_id, time):
    newExe = Executed(order_id = order_id, price = price, amount = amount, time = time)
    session.add(newExe)
    session.commit()
    
    


def test():
    engine = initDB()
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    # user = session.query(Account).get(2)
    # print(user.dto())
    testaccount = Account(balance = 114514)
    # test = Order(symbol = "BTC", remain_amount = -10, limit_price = 90.0, status = "open", time = 200, account_id = 1)
    session.add(testaccount)
    session.commit()
    # acc = session.query(Account.account_id).all()
    # for a in acc:
    #     print(a[0])
    # session.add(test)
    # session.commit()
    # tmp  = Order(symbol = "BTC", remain_amount = 10, limit_price = 100.0, status = "open", time = 111, account_id = 2)
    # ans = matchOrder(session, tmp)
    # print(ans)
    test = Order(symbol = "BTC", remain_amount = -10, limit_price = 90.0, status = "open", time = 200, account_id = 1)
    session.add(test)
    session.commit()
    print(test.dto())
test()