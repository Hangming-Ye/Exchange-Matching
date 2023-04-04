from xml_request_generator import *
import socket, time, struct, threading

HOST = '127.0.0.1'
PORT = 12345

def clientInit(id):
    sock = conn()
    res = hybridTestEven(id, sock) if id%2==0 else hybridTestOdd(id, sock)

def conn():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((socket.gethostname(), PORT))
    return sock

def sendXML(sock, xml):
    size = struct.pack("i", len(xml))

    sock.send(size)
    sock.send(xml)

def hybridTestOdd(id, sock):
    xml = createRequestGenerator({"id": id, "balance": 10000}, [])
    sendXML(sock, tostring(xml))
    resp = sock.recv(65535)
    sock.close()
    print(resp)

def hybridTestEven(id, sock):
    xml = createRequestGenerator({"id": id, "balance": 0}, [
        {"id": id, "symbol": "BTC", "num": 100}
    ])
    sendXML(sock, tostring(xml))
    resp = sock.recv(65535)
    sock.close()
    print(resp)

def test(num):
    for i in range(1, num+1):
        t = threading.Thread(target=clientInit, args=(i,))
        t.start()

if __name__ == "__main__":
    test(10)

