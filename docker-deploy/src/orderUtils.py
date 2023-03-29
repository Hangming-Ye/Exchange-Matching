from orm import *
from db import *
from sqlalchemy.orm import query, Session, sessionmaker

def matchOrder(session, od):
    allOrder = session.query(Order.tran_id).filter(Order.symbol==od.symbol, Order.status=="open")
    # buy order
    if od.remain_amount > 0:
        ans = allOrder.filter(Order.limit_price < od.limit_price, Order.remain_amount < 0).order_by(Order.limit_price, Order.time).first()
    elif od.remain_amount < 0:
        ans = allOrder.filter(Order.limit_price > od.limit_price, Order.remain_amount > 0).order_by(Order.limit_price.desc(), Order.time).first()
    return ans

def test():
    
    engine = initDB()
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    tmp  = Order(symbol = "BTC", remain_amount = 10, limit_price = 100.0, status = "open", time = 111, account_id = 0)
    ans = matchOrder(session, tmp)
    print(ans)
test()