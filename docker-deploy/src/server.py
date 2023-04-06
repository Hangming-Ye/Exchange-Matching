import socket, struct
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring
from datetime import datetime
from create import *
from orderUtils import *
from orm import *
import multiprocessing as MP

PORT = 12345  # Port to listen on (non-privileged ports are > 1023)
PROCESSNUM = 4


def init(l):
    global lock
    lock = l

def process_request(fd):
    session  = dbInit()
    request = recvXML(fd)
    if request != None:
        res = parseXML(request, session)
        # xml to string
        fd.send(tostring(res))
    fd.close()
    session.close()
    # receive request from client


def recvXML(fd):
    struSize = fd.recv(4)
    if len(struSize) == 0:
        return None
    size = struct.unpack("i", struSize)[0]
    request = fd.recv(size)
    if len(request) == 0:
        return None
    return request


# parse xml and call relevant function to deal with <create accout> <create postion> <open order> <cancel order> <query oder>
# return response xml
def parseXML(request, session):
    root = ET.fromstring(request)
    res = ET.Element('results')
    # first divide to two workflow: create/transaction
    if root.tag == "create":
        for child in root:
            if (child.tag == "account"):
                accout_id = child.get('id')
                balance = child.get('balance')
                # now need to connect to database and insert this record into Account
                # name function InsertAccount
                InsertAccount(session, accout_id, balance, res)

            elif (child.tag == "symbol"):
                sym = child.get('sym')
                # deep to child's child to get accout id and num of stock
                childOfSym = child[0]
                accout_id = childOfSym.get('id')
                amount = int(childOfSym.text)
                # now need to connect database and insert this record into Position
                # name function InsertPosition
                InsertPosition(session, sym, accout_id, amount, res)

            else:
                # please deal with error
                print("error here please deal with")
    elif root.tag == "transactions":
        accout_id = root.attrib.get('id')
        account_exists = checkAccount(session, accout_id)
        for child in root:
            if (child.tag == "order"):
                sym = child.get('sym')
                amount = float(child.get('amount'))
                limit = float(child.get('limit'))
                if account_exists:
                # get current time and pass to time varibale
                    try:
                        od_id = createOrder(
                            session, amount, limit, sym, accout_id)
                    except ArgumentError as e:
                        createError = ET.SubElement(
                            res, 'error', {'sym': sym, 'amount': str(amount), 'limit': str(limit)})
                        createError.text = e.msg
                    else:
                        ET.SubElement(res, 'opened', {'sym': sym, 'amount': str(
                            amount), 'limit': str(limit), 'id': str(od_id)})
                        lock.acquire()
                        makeTransaction(session, od_id)
                        lock.release()
                else:
                    createError = ET.SubElement(
                            res, 'error', {'sym': sym, 'amount': str(amount), 'limit': str(limit)})
                    createError.text = "invaild account: account does not exists"
            elif (child.tag == "cancel"):
                tran_id = child.get('id')
                if account_exists:
                    # now need to change database table Order to change its' status from open to cancel
                    # name function CancelOrder
                    lock.acquire()
                    CancelOrder(session, tran_id, res)
                    lock.release()
                else:
                    error = ET.SubElement(res, 'error', {'id': str(tran_id)})
                    error.text = "invaild account: account does not exists"
            elif (child.tag == "query"):
                tran_id = child.get('id')
                if account_exists:
                    
                    # now need to query table Order and Executed to get all record
                    # name function QueryOrder
                    QueryOrder(session, tran_id, res)
                else:
                    error = ET.SubElement(res, 'error', {'id': str(tran_id)})
                    error.text = "invaild account: account does not exists"

            else:
                error = ET.SubElement(res, 'error', {'id': str(id)})
                error.text = "invaild tag in transaction"
    else:
        error = ET.SubElement(res, 'error', {'id': str(id)})
        error.text = "invaild tag in transaction/create"
    return res


def test(xml):
    root = ET.fromstring(xml)
    # first divide to two workflow: create/transaction
    if root.tag == "create":
        for child in root:
            if (child.tag == "account"):
                accout_id = child.get('id')
                balance = child.get('balance')
                # now need to connect to database and insert this record into Account
                # name function InsertAccount return a string with a format of xml
                print("create account id = " +
                      accout_id + " balance = " + balance)

            elif (child.tag == "symbol"):
                sym = child.get('sym')
                # deep to child's child to get accout id and num of stock
                childOfSym = child[0]
                accout_id = childOfSym.get('id')
                amount = childOfSym.text
                # now need to connect database and insert this record into Position
                # name function InsertPosition return a string with a format of xml
                print("create symbol id = " + accout_id + " amount = " + amount)

    elif root.tag == "transactions":
        accout_id = root.attrib.get('id')
        print(accout_id)
        for child in root:
            if (child.tag == "order"):
                sym = child.get('sym')
                print(sym)
                amount = child.get('amount')
                print(amount)
                limit = child.get('limit')
                print(limit)
                # get current time and pass to time varibale
                time = datetime.now()
                # edit Account/Position to deduct money/stock
                # name function DeductAmount/DeductPosition return true or false indicate if could execute the relevant operation
                print("transaction order account_id = " + accout_id +
                      " sym = " + sym + " amount = " + amount + " limit " + limit)

            elif (child.tag == "cancel"):
                tran_id = child.get('id')
                print("transaction cancel account_id = " +
                      accout_id + " transaction id " + tran_id)

            elif (child.tag == "query"):
                tran_id = child.get('id')
                print("transaction query account_id = " +
                      accout_id + " transaction id " + tran_id)


if __name__ == "__main__":
    initDB()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((socket.gethostname(), PORT))
    sock.listen(100)
    print("----Start Listen at port",PORT,"----")
    l = MP.Lock()
    pool = MP.Pool(processes=PROCESSNUM, initializer=init, initargs=(l,))
    fdList = list()
    # act as a server to continue to accept request from client
    while (True):
        fd, addr = sock.accept()
        fdList.append(fd)
        if len(fdList) > 0:
            tarFD = fdList.pop(0)
            pool.apply_async(func=process_request, args=(tarFD,))