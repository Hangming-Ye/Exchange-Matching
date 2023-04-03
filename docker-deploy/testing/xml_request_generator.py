import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring

# account dic is a dictionary eg. [{id:'id', balance:'balance'}]
# position list is a list of dictionary eg [{id:'id',symbol:"symbol",num:"num"}]
# a fast generate method, but limit to the order
def createRequestGenerator(new_account, position_list):
    #first generate root tag
    request = ET.Element('create')
    id = new_account['id']
    balance = new_account['balance']
    ET.SubElement(request, 'account', {
                'id': str(id), 'balance': str(balance)})
       
    for new_position in position_list:
        id = new_position['id']
        sym = new_position['symbol']
        num = new_position['num']
        pos=ET.SubElement(request, 'symbol', {
                'sym': sym})
        under_pos=ET.SubElement(pos, 'account', {
                'id': str(id)})
        under_pos.text = str(num)
    return request

# Or you can use any combination of these two functions to create an xml request with create as the root directory
# but do not forget to add  request = ET.Element('create') in main function
def account_generator(request,id,balance):
    ET.SubElement(request, 'account', {
                'id': str(id), 'balance': str(balance)})
def position_generator(request, id, symbol, num):
    pos=ET.SubElement(request, 'symbol', {
                'id': str(id)})
    under_pos=ET.SubElement(pos, 'account', {
                'id': str(id)})
    under_pos.text = num


def order_generator(request, symbol, amount, limit):
    ET.SubElement(request, 'order', {
                'sym': symbol,'amount':str(amount),'limit':str(limit)})
def query_generator(request, trans_id):
    ET.SubElement(request, 'query', {
                'id': str(trans_id)})
def cancel_generator(request, trans_id):
    ET.SubElement(request, 'cancel', {
                'id': str(trans_id)})
    


# order list is a list of dictionary [{symbol:"symbol", amount:"amount", limit:"limit"}]
# query list is a list contain a list of trans_id
# this function is to quick generate a transaction request
# if you want to random order just use _generator function to generate a random combination
def TransRequestGenerator(account_id, order_list, query_list, cancel_list):
    request = ET.Element('transactions',{'id':str(account_id)})
    for order in order_list:
        symbol = order['symbol']
        amount = order['amount']
        limit = order['limit']
        order_generator(request, symbol, amount, limit)
    for toBequery in query_list:
        query_generator(request, toBequery)
    for toBecancel in cancel_list:
        cancel_generator(request, toBecancel)
    return request




# now we begin our test
if __name__ == "__main__":
    #test create
    
    new_account ={"id":1,"balance":100}
    #[{id:'id',symbol:"symbol",num:"num"}]
    position_list = [
        {"id":1,"symbol":"ETC","num":100},
        {"id":1,"symbol":"APPLE","num":300},
        {"id":1,"symbol":"HTC","num":400},
        {"id":1,"symbol":"META","num":800}
    ]
    create_requets = createRequestGenerator(new_account, position_list)
    tree = ET.ElementTree(create_requets)
    # write the tree to a file
    tree.write("/home/ht175/ECE568/Exchange-Matching/docker-deploy/src/create.xml",xml_declaration=True,encoding='UTF-8')
    #test transaction
    account_id = 2
    order_list = [
        {"symbol":"FACEBOOK", "amount":900, "limit":-1000},
        {"symbol":"TESLA", "amount":1000, "limit":967.3},
        {"symbol":"GOOGLE", "amount":200, "limit":1290}
    ]
    query_list = [101,90,8,7]
    cancel_list = [10, 20, 30]
    trans_request=TransRequestGenerator(account_id, order_list, query_list, cancel_list)
    tree = ET.ElementTree(trans_request)
    # write the tree to a file
    tree.write("/home/ht175/ECE568/Exchange-Matching/docker-deploy/src/transaction.xml",xml_declaration=True,encoding='UTF-8')



        






        
        


