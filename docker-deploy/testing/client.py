import socket
import sys
from xml_request_generator import *

def sendCreate(new_account, position_list):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = 'vcm-32401.vm.duke.edu'
    port = 1234
    sock.connect((host, port))
    create_requets = createRequestGenerator(new_account, position_list)
    print(tostring(create_requets))
    sock.send(tostring(create_requets))
    data = sock.recv(65535)
    print(data)

def sendTransaction(account_id, order_list, query_list, cancel_list):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = 'vcm-32401.vm.duke.edu'
    port = 1234
    sock.connect((host, port))
    create_requets = TransRequestGenerator(account_id, order_list, query_list, cancel_list)
    print(tostring(create_requets))
    sock.send(tostring(create_requets))
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









if __name__ == "__main__":
    test1()
    test2()
    print("##############################")
    test3()
    
    


