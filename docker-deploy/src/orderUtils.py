from orm import *
from db import *
from sqlalchemy.orm import query, Session, sessionmaker
import time
# 自己创建的order自己应该不能搜索到吧？

def createOrder(session, amount, price, sym, uid):
    user = session.query().get(uid)
    if user == None:
        return -1
    user_dict = user.dto()

    # buy order
    if amount > 0:
        user_dict['balance'] -= amount * price
        # insufficient balance
        if user_dict['balance'] < 0:
            return -2
        user.update(user_dict, synchronize_session = False)
    #sell order
    elif amount < 0:
        stock = session.query(Position).filter(Position.account_id == uid, Position.symbol == sym).first()

        # position not find
        if stock == None:
            return -3
        
        stock = stock[0]
        stock_dict = stock.dto()
        stock_dict['amount'] -= amount

        # position amount insufficient
        if stock_dict['amount'] < 0:
            return -4
        stock.update(stock_dict, synchronize_session = False)

    # create order successfully
    order = Order(remain_amount = amount, limit_price = price, symbol = sym, time = int(time.time()), account_id = uid)
    session.add(order)
    session.commit()
    return order.tran_id

def matchOrder(session, od_id):
    od = session.query(Order).get(od_id)
    allOrder = session.query(Order.tran_id).filter(Order.symbol==od.symbol, Order.status=="open")

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

def executeOrder(session, od1_id, od2_id):
    od1 = session.query(Order).get(od1_id)
    od2 = session.query(Order).get(od2_id)

    price  = od1.limit_price
    
    if od1.remain_amount > 0:
        buy = od1
        sell = od2
    else:
        buy = od2
        sell = od1
    
    
    


def test():
    engine = initDB()
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    testaccount = Account(balance = 114514)
    test = Order(symbol = "BTC", remain_amount = -10, limit_price = 90.0, status = "open", time = 200, account_id = 1)
    session.add(testaccount)
    session.commit()
    acc = session.query(Account.account_id).all()
    for a in acc:
        print(a[0])
    session.add(test)
    session.commit()
    tmp  = Order(symbol = "BTC", remain_amount = 10, limit_price = 100.0, status = "open", time = 111, account_id = 2)
    ans = matchOrder(session, tmp)
    print(ans)
test()