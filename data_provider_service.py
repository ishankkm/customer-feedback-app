'''
Created on Mar 22, 2018
@author: ishank
'''

from pymongo import MongoClient
import json, time

class DataProviderService(object):
    def __init__(self):
        self._appJson = json.load(open('app.json'))
        try:
            self._client = MongoClient(self._appJson['mongoConfig']['mongoClient'])
            self._db = self._client.business
        except:
            return Exception("DB connection error")
    
    # Add customer details to DB
    def addCustomer(self, custName, phoneNum, prodType, message=None, state=0):
        
        if len(phoneNum) < 10:
            return Exception("Invalid phone number")
        
        countryCode = phoneNum[:-10] if len(phoneNum) > 10 else "+1"
        cust = self.getCustomer(phoneNum, prodType, custName)        
        
        document = {
            "custName": custName,
            "phoneNum": phoneNum[-10:],
            "countryCode": countryCode,
            "prodType": prodType,
            "state": 1
        }
        
        if message != None:
            document['sentMsg'] = [{'message': message, 'timestamp': time.time()}]
        
        try:            
            if cust != None:
                if message != None:
                    self.addCustSentMsg(phoneNum, message, state)
            else:
                self._db.customers.update_one({"phoneNum": phoneNum[-10:]}, {'$set': document}, upsert=True)
        except Exception as e:
            print(e)
            return Exception("DB operation failed")
        
        return True
    
    # Get customer data if customer exist in DB
    def getCustomer(self, phoneNum, prodType=None, custName=None):
        
        cust = {'phoneNum': phoneNum[-10:]}
        if prodType != None: cust['prodType'] = prodType
        if prodType != None: cust['custName'] = custName
            
        
        if len(phoneNum) < 10:
            return Exception("Invalid phone number")
        try:
            return  self._db.customers.find_one(cust)
        except:
            return Exception("DB operation failed")
    
    # Add a message that was sent to customer
    def addCustSentMsg(self, phoneNum, message, state=None):
        
        cust = self.getCustomer(phoneNum)
        
        if cust == None: 
            return Exception("Customer does not Exist")
        
        msgDoc = {
            'message': message,
            'timestamp': time.time()
        }
        
        try:        
            self._db.customers.update_one({'phoneNum': cust['phoneNum']}, {'$push': { 'sentMsg': msgDoc }})
            if state != None:
                self._db.customers.update_one({'phoneNum': cust['phoneNum']}, {'$set': { 'state': state }})
        except Exception as e:
            print(str(e))
            return Exception("DB operation failed")
        
        return True
    
    # Add a message received from customer
    def addCustReceivedMsg(self, phoneNum, message, state=None):
        
        cust = self.getCustomer(phoneNum)
        
        if cust == None: 
            return Exception("Customer does not Exist")
        
        msgDoc = {
            'message': message,
            'receivedFrom': phoneNum[-10:],
            'timestamp': time.time()
        }
        
        try:        
            self._db.customers.update_one({'phoneNum': cust['phoneNum']}, {'$push': { 'recvMsg': msgDoc }})
            if state != None:
                self._db.customers.update_one({'phoneNum': cust['phoneNum']}, {'$set': { 'state': state }})
        except:
            return Exception("DB operation failed")
        
        return True
    
    # return a list of messages corresponding to a customer. Type can be all, sent, or received
    def getAllCustMsg(self, phoneNum, msgtype='all'):
        
        cust = self.getCustomer(phoneNum[-10:])
        
        sentMsg = cust['sentMsg']
        recvMsg = cust['recvMsg']
        
        if msgtype == 'sent':
            return {'sentMsg': sentMsg }
        elif msgtype == 'received':
            return {'receivedMsg': recvMsg}
        else:    
            return {'sentMsg': sentMsg, 'receivedMsg': recvMsg }
    
    def getMsgTemplates(self):
        result = self._db.msgTemplates.find({'type': 'messages'})
        messages = result.next()['msg'] 
        
        return messages
    
    def addMsgTemplate(self, message, msgType):        
        document = {
            '$set': {"msg."+msgType: message}
        }
        
        try:
            self._db.msgTemplates.update_one({"type": "messages"}, document) 
        except:
            return Exception('DB Update Error')
        
        return True
        
    

# dp = DataProviderService()
# print(dp.getMsgTemplates())
# if dp.getCustomer("+13233270568")['custName']:
#     print("DB Connected")