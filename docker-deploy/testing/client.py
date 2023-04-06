import socket
import sys
from xml_request_generator import *
from workloadTest import *

def sendCreate(new_account, position_list):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '0.0.0.0'
    port = 12345
    sock.connect((host, port))
    create_requets = createRequestGenerator(new_account, position_list)
    print(tostring(create_requets))
    # sock.send(tostring(create_requets))
    sendXML(sock,tostring(create_requets))
    data = sock.recv(65535)
    print(data)

def sendTransaction(account_id, order_list, query_list, cancel_list):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = 'vcm-32401.vm.duke.edu'
    port = 1234
    sock.connect((host, port))
    create_requets = TransRequestGenerator(account_id, order_list, query_list, cancel_list)
    print(tostring(create_requets))
    # sock.send(tostring(create_requets))
    sendXML(sock,tostring(create_requets))
    data = sock.recv(65535)
    print(data)

# test complete execute
def test1():
    sendCreate({"id": 1, "balance": 1000000}, [
        {"id": 1, "symbol": "ETC", "num": 100},
        {"id": 1, "symbol": "APPLE", "num": 300},
    ])
    sendCreate({"id": 2, "balance": 2000000}, [
        {"id": 2, "symbol": "ETC", "num": 300},
        {"id": 2, "symbol": "APPLE", "num": 100},
    ])
    sendTransaction(1,[
        {"symbol":"ETC", "amount":-100, "limit":100}, #transid=1
        {"symbol":"GOOGLE", "amount":100, "limit":100} #transid=2
    ],[1],[2])
    sendTransaction(2,[
        {"symbol":"ETC", "amount":100, "limit":100}, #transid=3
        
    ],[3],[])
    

# test partial execute
def test2():
    sendCreate({"id": 3, "balance": 1000000}, [
        {"id": 3, "symbol": "ETC", "num": 100},
        {"id": 3, "symbol": "APPLE", "num": 300},
    ])
    sendCreate({"id": 4, "balance": 2000000}, [
        {"id": 4, "symbol": "ETC", "num": 300},
        {"id": 4, "symbol": "APPLE", "num": 100},
    ])
    sendTransaction(3,[
        {"symbol":"ETC", "amount":-50, "limit":100}, #transid=4
       
    ],[4],[])
    sendTransaction(4,[
        {"symbol":"ETC", "amount":100, "limit":120}, #transid=5
        
    ],[5],[5]) #executed 50 shares and cancel

#test match strategy
def test3():
    sendCreate({"id": 5, "balance": 10000}, [
        {"id": 5, "symbol": "APPLE", "num": 500},
    ])
    sendCreate({"id": 6, "balance": 20000}, [
        {"id": 6, "symbol": "APPLE", "num": 300},
    ])
    sendTransaction(5,[
        {"symbol":"APPLE", "amount":-200, "limit":128}, #transid=6
    ],[6],[])
    sendTransaction(4,[
        {"symbol":"APPLE", "amount":-100, "limit":129}, #transid=7
    ],[7],[])
    sendTransaction(1,[
        {"symbol":"APPLE", "amount":100, "limit":129}, #transid=8
    ],[8],[])
    sendTransaction(2,[
        {"symbol":"APPLE", "amount":100, "limit":130}, #transid=9
    ],[9],[])
    sendTransaction(3,[
        {"symbol":"APPLE", "amount":100, "limit":131}, #transid=10
    ],[10],[])
    sendTransaction(5,[
    ],[6],[]) 
    sendTransaction(6,[
    ],[7],[]) 

"""
buy             sell
                 129@100 2
129@100 3          128@200 1
first execute
sell
128 100
"""
"""
buy             sell
                 129@100 2
130@100 4               
first execute
sell
128 100
128 100
"""
"""
buy             sell
                 129@100 2
131@100                
first execute
sell
128 100
128 100
129 100
"""
#test error: account id already exists
def test4():
    sendCreate({"id": 7, "balance": 1000000}, [
        {"id": 7, "symbol": "ETC", "num": 100},
        {"id": 7, "symbol": "APPLE", "num": 300},
    ])
    sendCreate({"id": 7, "balance": 1000000}, [
        {"id": 7, "symbol": "ETC", "num": 100},
        {"id": 7, "symbol": "APPLE", "num": 300},
    ])
#test in transaction if account	ID	is	invalid,	then	an	<error>	will	be	reported	for	each	transaction
def test5():
    sendTransaction(8,[{"symbol":"AAA", "amount":-50, "limit":100}
    ],[8],[8]) 
#test in create position error if amount <0
def test6():
    sendCreate({"id": 8, "balance": 10000}, [
        {"id": 8, "symbol": "BBB", "num": -100},
    ])
#test in cancel, try to cancel a executed order
def test7():
    sendCreate({"id": 9, "balance": 10000}, [
        {"id": 9, "symbol": "BBB", "num": 100},
    ])
    sendTransaction(9,[
        {"symbol":"BBB", "amount":100, "limit":10}, #transid=11
    ],[11],[11])
    sendTransaction(9,[
    ],[11],[11])

#test in cancel, try to cancel a not existed order
def test8():
     sendTransaction(9,[
     ], 
    [],[12])

#test try to create a transaction which will deduct money more than the balance
#or deduct stock more than position
def test9():
    sendCreate({"id": 10, "balance": 10}, [
        {"id": 10, "symbol": "BBB", "num": 100},
    ])
    sendTransaction(10,[
        {"symbol":"CCC", "amount":100, "limit":10}, 
    ],[],[])
    sendTransaction(10,[
        {"symbol":"BBB", "amount":-110, "limit":10}, 
    ],[],[])

















if __name__ == "__main__":
    print("test1: ##############################")
    test1()
    print("test2: ##############################")
    test2()
    print("test3: ##############################")
    test3()
    print("test4: ##############################")
    test4()
    print("test5: ##############################")
    test5()
    print("test6: ##############################")
    test6()
    print("test7: ##############################")
    test7()
    print("test8: ##############################")
    test8()
    print("test9: ##############################")
    test9()

    
    


