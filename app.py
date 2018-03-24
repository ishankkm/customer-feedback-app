'''
Created on Mar 21, 2018
@author: ishank
'''
import json, requests
from twilio.rest import Client  
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from twilio.twiml.messaging_response import MessagingResponse

from data_provider_service import DataProviderService

appJson = json.load(open('app.json'))
dataProvider = DataProviderService()

app = Flask(__name__)
CORS(app)
client = Client(appJson['msgConfig']['account_sid'], appJson['msgConfig']['auth_token'])
responseMessages = dataProvider.getMsgTemplates()

def analyzeSentiment(message):
    sentiment_api_url = appJson['textAnalyticsConfig']['sentiment_api_url']

    documents = {'documents' : [
      {'id': '1', 'language': 'en', 'text': message}
    ]}
    
    headers   = {"Ocp-Apim-Subscription-Key": appJson['textAnalyticsConfig']['subscription_key']}
    response  = requests.post(sentiment_api_url, headers=headers, json=documents)
    sentiments = response.json()
    return sentiments['documents'][0]['score']
 
def formatMsg(message, prodType = 'the product', custName = 'Customer'):
    return message.replace('<firstName>', custName) \
                  .replace('<productType>', prodType)
  

@app.route("/")
def hello():
#     return "hello world"
    return render_template('index.html', message="None")

@app.route("/sendMsg", methods = ['POST'])
def sendMsg():
    
    if not request.json or not 'phoneNumber' in request.json \
                        or not 'productType' in request.json \
                        or not 'custName' in request.json:
        return jsonify({"status":"FAIL", "error": "Incorrect Params"})
    
    phoneNumber, productType, custName = request.json['phoneNumber'], request.json['productType'], request.json['custName']
    
    msgBody = formatMsg(responseMessages['firstAutomatedMsg'], productType, custName)
    state = 0
    try:
        client.api.account.messages.create(
        to = phoneNumber,
        from_ = appJson['msgConfig']['appNumber'],
        body = msgBody )
        state = 1
    except Exception as e:
#         print(e.msg)
        return jsonify({"status":"FAIL", "message":e.msg})
    
    dataProvider.addCustomer(custName, phoneNumber, productType, msgBody, state)
      
    return jsonify({"status":"OK", 'msgBody': msgBody, "message": "Message was sent succesfully!" })


@app.route("/sms", methods=['GET', 'POST'])
def sms_ahoy_reply():
    
    resp = MessagingResponse()
    msgBody = request.values.get('Body', None)
    sentimentScore = analyzeSentiment(msgBody)
    
    phoneNum = request.values.get('From', None)
    cust = dataProvider.getCustomer(phoneNum)  
    dataProvider.addCustReceivedMsg(phoneNum, msgBody)
      
    message = ""
    
    if cust == None:
        resp.message(appJson['msgTemplates']['default'])
        return str(resp)
    
    if cust['state'] == 1:
        if sentimentScore > 0.5:
            message = formatMsg(responseMessages['positiveRes'], cust['prodType'], cust['custName'])
            resp.message(message)
        else:
            message = formatMsg(responseMessages['negativeRes'], cust['prodType'], cust['custName'])
            resp.message(message)
        dataProvider.addCustSentMsg(phoneNum, message, 2)
    elif cust['state'] == 2:
        message = appJson['msgTemplates']['endConvReply']
        resp.message(message)
        dataProvider.addCustSentMsg(phoneNum, message, 0)
    else:
        message = appJson['msgTemplates']['default']
        resp.message(message)            
        dataProvider.addCustSentMsg(phoneNum, message, 0)    

    return str(resp)

@app.route("/updateMsg", methods = ['POST'])
def updateMsg():
#     print(request.json)
    if not request.json or not 'msgName' in request.json \
                        or not 'message' in request.json:
        response = jsonify({"status":"FAIL", "error": "Incorrect Params"})
    else:
        if dataProvider.addMsgTemplate(request.json['message'], request.json['msgName']):     
            response = jsonify({"status":"OK"})
        else:
            response =  jsonify({"status":"Fail"})
        
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/getAllMsg", methods = ['GET'])
def getAllMsg():
#     print("request    ")
    response = jsonify(dataProvider.getMsgTemplates())
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
