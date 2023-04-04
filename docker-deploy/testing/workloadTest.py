from xml_request_generator import *
import socket, time, struct

HOST = 'vcm-32401.vm.duke.edu'
PORT = 12345

def clientInit(id):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    res = hybridTestEven(id, sock) if id%2==0 else hybridTestOdd(id, sock)

def sendXML(sock, xml):
    msg = xml.encode('utf-8')
    size = struct.pack("i", len(msg))

    sock.send(size)
    sock.send(msg)

def hybridTestOdd(id, sock):
    xml = createRequestGenerator({"id": id, "balance": 10000}, [])
    sendXML(sock, xml)

def hybridTestEven(id, sock):
    xml = createRequestGenerator({"id": id, "balance": 0}, [
        {"id": id, "symbol": "BTC", "num": 100}
    ])
    sendXML(sock, xml)