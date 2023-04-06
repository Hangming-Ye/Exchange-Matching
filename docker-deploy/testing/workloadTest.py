from xml_request_generator import *
import socket, time, struct, threading
from testdb import *
import matplotlib.pyplot as plt

HOST = '0.0.0.0'
PORT = 12345

def hybridTest(id):
    hybridTestEven(id) if id%2==0 else hybridTestOdd(id)


def conn():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((socket.gethostname(), PORT))
    return sock


def sendXML(sock, xml):
    size = struct.pack("i", len(xml))
    sock.send(size)
    sock.send(xml)


def request(id, xml):
    try:
        sock = conn()
        sendXML(sock, tostring(xml))
        print(sock.recv(65535))
        sock.close()
    except socket.timeout:
        print("packet loss")
        sock.close()


def createTest(id):
    request(id, createRequestGenerator({"id": id, "balance": id*id}, [{"id": id, "symbol": "BTC", "num": id*id}]))


def cancelTestGen(id):
    request(id, createRequestGenerator({"id": id, "balance": 100}, [{"id": id, "symbol": "BTC", "num": 50}]))
    request(id, TransRequestGenerator(id, [{"symbol":"BTC", "amount":-50, "limit":100}], [], []))

def cancelTest(id):
    request(id, TransRequestGenerator(id, [], [], [id]))

def hybridTestOdd(id):
    request(id, createRequestGenerator({"id": id, "balance": 10000}, []))
    request(id, TransRequestGenerator(id, [{"symbol":"BTC", "amount":50, "limit":100}], [], []))
    request(id, TransRequestGenerator(id, [{"symbol":"BTC", "amount":50, "limit":100}], [], []))
    

def hybridTestEven(id):
    request(id, createRequestGenerator({"id": id, "balance": 0}, [{"id": id, "symbol": "BTC", "num": 100}]))
    request(id, TransRequestGenerator(id, [{"symbol":"BTC", "amount":-100, "limit":100}], [], []))
    request(id, TransRequestGenerator(id, [], [id], []))

def cancelPre(num):
    threadList = list()
    for i in range(1, num+1):
        t = threading.Thread(target=cancelTestGen, args=(i,))
        t.start()
        threadList.append(t)
        
    for t in threadList:
        t.join()

def conTest(num, func, ins):
    start = time.time()
    threadList = list()
    for i in range(1, num+1):
        t = threading.Thread(target=func, args=(i,))
        t.start()
        threadList.append(t)
    
    for t in threadList:
        t.join()
    end = time.time()
    return (end - start)/(num*ins)


def seqTest(num, func, ins):
    start = time.time()
    for i in range(1, num+1):
        func(i)
    end = time.time()
    return (end - start)/(num*ins)


def graph(func, ins, wlList, title):
    initDB()
    if func==cancelTest:
        cancelPre(50)
    seq = seqTest(50, func, ins)
    seqTime = list()
    for i in range(len(wlList)):
        seqTime.append(seq)

    conTime = list()
    for wl in wlList:
        initDB()
        if func==cancelTest:
            cancelPre(wl)
        conTime.append(conTest(wl, func, ins))
    
    plt.plot(wlList,conTime, label = "Concurrency")
    plt.plot(wlList,seqTime, label = "Sequence")
    plt.xlabel("Workload")
    plt.ylabel("Average Response Time (s)")
    plt.title(title)
    plt.legend(loc = 'upper right')
    path = "./"+ title + ".png"
    plt.savefig(path)
    plt.show()
    plt.close()

def manDraw1():
    xlist = [1, 2, 4, 8, 12, 16]
    ylist = [0.14480661630630492, 0.07760035832722982, 0.039463148911794026, 0.019212086995442707, 0.015615406036376954, 0.014644641876220704]
    title = "Concurrency Performance with Different Process Num"
    plt.plot(xlist,ylist)
    plt.xlabel("Process Number")
    plt.ylabel("Average Response Time (s)")
    plt.title(title)
    path = "./"+ title + ".png"
    plt.savefig(path)
    plt.show()
    plt.close()

def manDraw2():
    xlist = [1, 2, 4]
    ylist = [0.04141168594360352, 0.03765674432118734, 0.03458372513453166]
    title = "Concurrency Performance with Different Core Num"
    plt.plot(xlist,ylist)
    plt.xlabel("Core Number")
    plt.ylabel("Average Response Time (s)")
    plt.title(title)
    x_major_locator= plt.MultipleLocator(1)
    ax=plt.gca()
    ax.xaxis.set_major_locator(x_major_locator)
    path = "./"+ title + ".png"
    plt.savefig(path)
    plt.show()
    plt.close()

if __name__ == "__main__":
    graph(createTest, 1, [40, 80, 160, 320, 480, 540],"Create Test Performance with Different Workload")
    graph(cancelTest, 1, [20, 40, 80, 160, 240, 320],"Cancel Test Performance with Different Workload")
    graph(hybridTest, 3, [20, 40, 80, 160, 240, 320],"Hybrid Test Performance with Different Workload")
    manDraw1()
    manDraw2()