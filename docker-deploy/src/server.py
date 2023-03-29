import socket
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring
from datetime import datetime
PORT = 12345  # Port to listen on (non-privileged ports are > 1023)
def process_request(fd):
    while (True):
        request = fd.recv()
        if (request):
           res = parseXML(request)
           # xml to string
           fd.send(tostring(res))
        else:
            break
    # receive request from client


def server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', PORT))
    sock.listen()
    # act as a server to continue to accept request from client
    while (True):
        fd, addr = sock.accept()

        process_request(fd)


# parse xml and call relevant function to deal with <create accout> <create postion> <open order> <cancel order> <query oder>
# return response xml
def parseXML(request):
    root = ET.fromstring(request)
    res = ET.Element('results')
    # first divide to two workflow: create/transaction
    if root.tag == "create":
        for child in root:
            if (child.tag == "account"):
                accout_id = child.get('id')
                balance = child.get('balance')
                # now need to connect to database and insert this record into Account
                # name function InsertAccount return a string with a format of xml
                res = InsertAccount(accout_id, balance, res)

            elif (child.tag == "symbol"):
                sym = child.get('sym')
                # deep to child's child to get accout id and num of stock
                childOfSym = child[0]
                accout_id = childOfSym.get('id')
                amount = childOfSym.text
                # now need to connect database and insert this record into Position
                # name function InsertPosition return a string with a format of xml
                res = InsertPosition(sym, accout_id, amount, res)
            else:
                # please deal with error
                print("error here please deal with")

    elif root.tag == "transactions":
        accout_id = root.get(id)
        for child in root:
            if (child.tag == "order"):
                sym = child.get('sym')
                amount = child.get('amount')
                limit = child.get('limit')
                # get current time and pass to time varibale
                time = datetime.now()
                # edit Account/Position to deduct money/stock
                # name function DeductAmount/DeductPosition return true or false indicate if could execute the relevant operation
                if (DeductAmount(accout_id, sym, limit)):
                    # now need to connect database and insert this record into Order
                    # with status 'open'
                    # name function InsertOrder return a string with a format of xml
                    res = InsertOrder(sym, amount, limit, time, res)
                else:
                    # deal with error
                    # let rese include error information
                    # do something here
                    res = res

            elif (child.tag == "cancel"):
                tran_id = child.get('id')
                # now need to change database table Order to change its' status from open to cancel
                # name function CancelOrder return a string with a format of xml
                res = CancelOrder(tran_id, res)

            elif (child.tag == "query"):
                tran_id = child.get('id')
                # now need to query table Order and Executed to get all records
                # name function QueryOrder return a string with a format of xml
                res = QueryOrder(tran_id, res)

            else:
                print("please deal with error here")
    else:
        print("please deal with error here")
    return res


def InsertAccount(accout_id, balance, res):
    return res


def InsertPosition(sym, accout_id, amount, res):
    return res


def InsertOrder(sym, amount, limit, time, res):
    return res


def DeductAmount(accout_id, sym, limit):
    return False


def CancelOrder(tran_id, res):
    return res


def QueryOrder(tran_id, res):
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
                print("create account id = " + accout_id + " balance = " +balance)

            elif (child.tag == "symbol"):
                sym = child.get('sym')
                # deep to child's child to get accout id and num of stock
                childOfSym = child[0]
                accout_id = childOfSym.get('id')
                amount = childOfSym.text
                # now need to connect database and insert this record into Position
                # name function InsertPosition return a string with a format of xml
                print("create symbol id = " + accout_id + " amount = " +amount)

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
                print("transaction order account_id = " + accout_id + " sym = " + sym + " amount = " +amount + " limit " + limit)

            elif (child.tag == "cancel"):
                tran_id = child.get('id')
                print("transaction cancel account_id = " + accout_id + " transaction id " + tran_id )
            

            elif (child.tag == "query"):
                tran_id = child.get('id')
                print("transaction query account_id = " + accout_id + " transaction id " + tran_id )
                
if __name__ == "__main__":
    filename = 'text.xml'
    f = open(filename, 'rb')
    xml = f.read(1024)
    print(xml)
    test(xml)

