from xml_request_generator import *
import socket, time, struct, threading

HOST = '0.0.0.0'
PORT = 12345
WORKLOAD = 200

def clientInit(id):
    hybridTestEven(id) if id%2==0 else hybridTestOdd(id)

def conn():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((socket.gethostname(), PORT))
    return sock

def sendXML(sock, xml, flag):
    size = struct.pack("i", len(xml))
    sock.send(size)
    sock.send(xml)
    if flag:
        print("%%%%%%%%", len(xml), xml)

def request(id, xml):
    flag = True
    flag2 = False
    while flag:
        sock = conn()
        sendXML(sock, tostring(xml), flag2)
        resp = sock.recv(65535)
        if len(resp) != 0:
            flag = False
            print(id, resp)
        else:
            print(id,"!!!!!!!!!!!!!!!!!")
            flag2 = True
    sock.close()


def hybridTestOdd(id):
    request(id, createRequestGenerator({"id": id, "balance": 10000}, []))
    request(id, TransRequestGenerator(id, [{"symbol":"BTC", "amount":30, "limit":100}], [], []))
    request(id, TransRequestGenerator(id, [{"symbol":"BTC", "amount":70, "limit":100}], [], []))

def hybridTestEven(id):
    request(id, createRequestGenerator({"id": id, "balance": 0}, [{"id": id, "symbol": "BTC", "num": 100}]))
    request(id, TransRequestGenerator(id, [{"symbol":"BTC", "amount":-100, "limit":100}], [], []))

def test(num):
    threadList = list()
    for i in range(1, num+1):
        t = threading.Thread(target=clientInit, args=(i,))
        t.start()
        threadList.append(t)
    
    for t in threadList:
        t.join()
    
if __name__ == "__main__":
    test(WORKLOAD)