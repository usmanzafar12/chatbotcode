#libraries to be imported 
import sys
import logging
import json, requests
from flask import Flask, request, Response
import logging
from googletrans import Translator
import string
from nltk import compat
from nltk import word_tokenize
from nltk.corpus import stopwords
import psycopg2
import time 
from datetime import timedelta,datetime
import datetime

#global variables
translated_message_text=' '
userTest=' '
message_text=' '
comment_id=''
msg_time=''
msg_time1=''
app = Flask(__name__)

#flags
#HERE flag_google_translate 0 (response),1 (donot respond),2 (input and response is the same), 3 (service is down)
flag_google_translate=0

#HERE flag_api_ai 0(reponse),1(Donot respond), 2(service is down)
flag_api_ai=0

# HERE flag_input=0 (Donot Forwards the input), flag_input=1 (forward the input), flag_input=5 (append the previous message to new one)
flag_input=0

flag_bypass=0



try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

PAT = 'EAACh9MQ3zy8BAJuw2AdCaSezuGIio39aVlFENWK1ZA0LHVEcU3BnhqFRrUJrZAKEfCdp9DZBJa8UAZB0ZCFb7FWtJ6mZAzUVenZCzEcJX8vg7HxEAwgcL93YOfXxZCb9CJygQpMo8J49JR6AGYh67CeoMGZAAs9OZCsUPrhhA19wFmlAZDZD'

VERIFY_TOKEN = 'test'

CLIENT_ACCESS_TOKEN = '3a67ab4afb49424587183ae8b04bf88b'

ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)


#Creating a new db Table
#conn = psycopg2.connect(database="postgres", user="postgres", password="9090", host="127.0.0.1", port="5432")
#cur = conn.cursor()
#cur.execute("CREATE TABLE response8(id serial PRIMARY KEY,inputFlag integer ,apiFlag integer,googleTranslateFlag integer,timeStampMessage timestamp, facebookId varchar(300),message_id varchar(300), inputMessage varchar(200000), translatedMessage varchar(200000), apiResponse varchar(200000), userOption text);")
#logging.info("Table Created....")
#conn.commit()
#conn.close()


@app.route('/', methods=['GET'])

def handle_verification():
    '''
    Verifies facebook webhook subscription
    Successful when verify_token is same as token sent by facebook app
    '''
    if (request.args.get('hub.verify_token', '') == VERIFY_TOKEN):
        logger.info("\\n successfully verified")
        return Response(request.args.get('hub.challenge', ''))
    else:
        logger.info("Wrong verification token!")
        return Response('Error, invalid token')

conn = psycopg2.connect(database="postgres", user="postgres", password="9090", host="127.0.0.1", port="5432")
cur = conn.cursor()

sender_messages=''

def checks_responses(translated_message_text,message_text):

    #if the api.ai return an empty string
    global flag_api_ai,flag_google_translate

    if (not userTest):
        logging.info('API.ai havent respond')
        flag_api_ai=1
    else:
        flag_api_ai=0

    #if google translate return an empty string or  
    if( not translated_message_text):
        flag_google_translate=1
    #if response is the same as input string
    elif(translated_message_text==message_text):
        flag_google_translate=2
        translated_message_text=message_text


    else:   
        flag_google_translate=0


def checks_input(query_number,temp_time,sender_messages,message_text):
    global flag_input,flag_bypass
   #if the time interval is less than 4 and message length is less than the 3 and previous message length is greater than 3
    if(temp_time.total_seconds()>4.0 and len(message_text.split())<2):
    	logging.info("GREETINGS............")

    	translator = Translator()
    	detected_lang = translator.detect(message_text).lang
    	logging.info(message_text)
    	logging.info(detected_lang)

    	logging.info(len(detected_lang))
    	logging.info(detected_lang.find('en'))

    	if (detected_lang.find('en')!=-1):
	    	flag_input=1
#	    	flag_bypass=1


#we have Two option
#Either we only focus on the time interval or convsider the length
#if we only focus on Time interval we can concatinate till a particular length is attained.
#We can see that if previous message and current message are less than 4 than concatinate else they remain separate entitty in this case 
#we can only concatinate two sentences in this case
#If we consider the sentence length then we can divide a sentence into many chunks
    #if(temp_time.total_seconds()<4.0 and len(message_text.split())<4 and len(sender_messages[query_number][7].split())<4):
    if(temp_time.total_seconds()<4.0 and len(sender_messages[query_number][7].split())<4):

        logging.info("ONE")
        #user_id is the sender's latest id
        message_id_updated=sender_messages[query_number][6]

        #previous_message_temp contains previous message
        previous_message_temp=sender_messages[query_number][7]

        #new_message is concatinate message
        message_text=previous_message_temp+' '+message_text
        logging.info("COMBINED MESSAGE")
        logging.info(message_text)

        if(len(message_text.split())>3):
            flag_input=1
        else:
            #flag_input=5 means more than two joining sentences
            flag_input=5

        logging.info("CURRENT DB")
        logging.info(sender_messages)
        logging.info("MESSAGE TO BE DELETED")
        logging.info(message_id_updated)

        logging.info("Commbined MESSAGE")
        logging.info(sender_messages[query_number])

        logging.info("NEW MESSAGE")
        logging.info(message_text)



        #delete the incomplete message chunk
        cur.execute("DELETE FROM response8 WHERE response8.message_id=%s",(message_id_updated,))
        conn.commit()
        
    #IF THE TIME interval is is greathan than four and text length is greater than 3 that is normal text
    elif(temp_time.total_seconds()>=4.0 and len(message_text.split())>=4):
        flag_input=1
        logging.info("TWO")

            
    elif(temp_time.total_seconds()<4.0 and len(message_text.split())<4 and len(sender_messages[query_number][7].split())>=4):

        logging.info("THREE MESSAGES")
        logging.info(message_text)

        flag_input=1
        logging.info("Three")

    elif(temp_time.total_seconds()<4.0 and len(message_text.split())>=4 and len(sender_messages[query_number][7].split())>=4):

        logging.info("FOUR MESSAGES")
        logging.info(message_text)

        flag_input=1
        logging.info("FOUR")

	
 #   elif(temp_time.total_seconds()>=4.0 and len(message_text.split())<5):
 #       flag_input=1
 #       logging.info("TWO")

    return message_text



@app.route('/', methods=['POST'])
def handle_message():
    '''
    Handle messages sent by facebook messenger to the applicaiton
    '''

    #global global_translated_message_text, globalUserTest, global_message_text, global_comment_id, global_entry, msg_time, sender_messages,flag_input
    global translated_message_text, userTest, message_text, comment_id, msg_time, sender_messages,flag_input,sender_id,flag_google_translate,flag_api_ai
    global msg_time1
    data = request.get_json()
    logger.info("\\n")
    flag_input=0

    if data["object"] == "page":
        for entry in data["entry"]:
            global_entry=entry
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):

                    # handle the input other than text
                    try:
                        sender_id = messaging_event["sender"]["id"]
                        recipient_id = messaging_event["recipient"]["id"]
                        message_text = messaging_event["message"]["text"]
                        comment_id=messaging_event["message"]["mid"]
                    except Exception as e:
                        sender_id = messaging_event["sender"]["id"]
                        recipient_id = messaging_event["recipient"]["id"]
                        message_text = 'NEW'
                        comment_id=messaging_event["message"]["mid"]
                    

                    #standardized_text = standardize_message_text(message_text)
                    if message_text.split('@')[0]!='Yes' and message_text.split('@')[0]!='No':
                        # time stamp of the input message
                        msg_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(messaging_event['timestamp']/1000))
                        msg_time=datetime.datetime.strptime(msg_time, "%Y-%m-%d %H:%M:%S")

                        #fetching user specific re
                        sql="SELECT * FROM response8 WHERE response8.facebookId = %s ORDER BY response8.id DESC LIMIT 2"
                        cur.execute(sql,(sender_id,))
                        conn.commit()
                        sender_messages1=cur.fetchall()

                        #if there is a new user entering a dummy 
                        query =  "INSERT INTO response8 (inputFlag,apiFlag,googleTranslateFlag,timeStampMessage,facebookId,message_id, inputMessage, translatedMessage, apiResponse,userOption) VALUES ( %s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"

                        if(len(sender_messages1)==0):
                             msg_time1=msg_time- timedelta(hours=9)
                             data = (9,9,9,msg_time1,sender_id, "DUMMY MESSAGE ID","DUMMY MESSAGE", " ", " "," ")
                             cur.execute(query, data)
                             conn.commit()   

                        #inserting the input into db immidiately after the input
                        data = (9,9,9,msg_time,sender_id, comment_id.split('$')[1],message_text, " ", " "," ")
                        cur.execute(query, data)
                        conn.commit()                       

                        #fetching the current DB
                        cur.execute(sql,(sender_id,))
                        conn.commit()
                        sender_messages=cur.fetchall()

                        #extrating time stamp from the record time_stamp_recent contains the last message time
                        time_stamp_recent=sender_messages[1][4]
                        query_number=1
                
                        #extracting the difference of the last message stored in the db and the input message latest msg_time contains the recents message
                        temp_time=sender_messages[0][4]-time_stamp_recent

                        flag_input=0

                        message_text=checks_input(query_number,temp_time,sender_messages,message_text)
                        logging.info("NEW CONDITION")
                        logging.info(flag_input)
                        logging.info("TIME DIFFERNCE")
                        logging.info(temp_time)

                        if(flag_input>0):

                            try:
                                if(flag_input==1):
                                    translated_message_text = google_translate(message_text)
                                    userTest=parse_user_message(translated_message_text)
                                    flag_google_translate=0
                                    flag_api_ai=0
                                    flag_bypass=0
                                else:
                                    translated_message_text = " "
                                    userTest=" "
                                    flag_google_translate=0
                                    flag_api_ai=0
                                    
                            except Exception as e:
                            	print("ERROR:")
                            	print(e)
                                translated_message_text=" "
                                userTest=" "
                                flag_google_translate=3
                                flag_api_ai=2
                                send_message_response(sender_id,comment_id.split('$')[1], 'Service is currently unavailable please try again later.')

                            checks_responses(translated_message_text,message_text)

                            if(flag_input==1):
                                send_message_response(sender_id,comment_id.split('$')[1] , userTest)
                                send_message_response(sender_id,comment_id.split('$')[1], 'Is the Reponse Ok?')

                            cur.execute("""UPDATE response8 SET inputFlag=(%s),apiFlag=(%s),googleTranslateFlag=(%s),inputMessage=(%s),translatedMessage=(%s),apiResponse=(%s),message_id=(%s) WHERE message_id=(%s)""", (flag_input,flag_api_ai,flag_google_translate,message_text,translated_message_text,userTest,comment_id.split('$')[1],comment_id.split('$')[1]))
                            conn.commit()
                            flag_input=0

                    #if the user enters the user response (Yes or No)
                    elif message_text.split('@')[0] == 'Yes'or message_text.split('@')[0]=='No':
                        conn1 = psycopg2.connect(database="postgres", user="postgres", password="9090", host="127.0.0.1", port="5432")
                        cur1 = conn1.cursor()
                        #retrieving the message id from payload from json
                        try:
                            message_id_payload=global_entry['messaging'][0]['message']['quick_reply']['payload']

                        except Exception as e:
                            message_id_payload='1'

                        a=message_text.split('@')[0]
                        cur1.execute("""UPDATE response8 SET userOption= (%s) WHERE message_id=(%s)""", (a,message_id_payload))
                        conn1.commit()
                        conn1.close()
    

                    logging.info("INPUT MESSAGE")
                    logging.info(message_text)

                    logging.info("Sender ID")
                    logging.info(sender_id)

                    logging.info("Translated Message")
                    logging.info(translated_message_text)

                    logging.info("API RESPONSE")
                    logging.info(userTest)
    return "ok"

def google_translate(user_text):
    '''
    this function will translate the received text using google translate
    '''
    global flag_bypass
    logging.info('FLAG BY PASS')
    logging.info(flag_bypass)
    translator = Translator(service_urls = ['translate.google.com.pk'])
    detected_lang = translator.detect(user_text).lang

    logging.info("LANGUAGE")
    logging.info(detected_lang)

    if(detected_lang.find('en')!=-1):

        trans_input = user_text
        print(trans_input)
        return trans_input
    else:
    	logging.info("TEXT Translated")
        mid_trans = translator.translate(user_text, src="hi", dest = "ur").text
        trans_input = translator.translate(mid_trans, src = "ur", dest = "en").text
        print(trans_input)
        return trans_input

def send_message_response(sender_id,comment_id, message_text):

    sentenceDelimiter = ". "
    messages = message_text.split(sentenceDelimiter)
    for message in messages:
        send_message(sender_id,comment_id, message)

def send_message(sender_id,comment_id, message_text):
    '''
    Sending response back to the user using facebook graph API
    '''
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
        params={"access_token": PAT},
        headers={"Content-Type": "application/json"},
        data=json.dumps({
        "recipient": {"id": sender_id},
        #db_comment_id of the bata base
        "message":{
    "text": message_text,
    "quick_replies":[
      {
        "content_type":"text",
        "title":"Yes",
        "payload":str(comment_id)
      },
      {
        "content_type":"text",
        "title":"No",
        "payload":str(comment_id)
      }
    ]

  }
    }))

def parse_user_message(user_text):
    '''
    Send the message to API AI which invokes an intent
    and sends the response accordingly
    The bot response is appened with weaher data fetched from
    open weather map client
    '''
    print("PARSE USER MESSAG " + str(time.time()) )

    request = ai.text_request()
    request.query = user_text

    response = json.loads(request.getresponse().read().decode('utf-8'))
    responseStatus = response['status']['code']

    if (responseStatus == 200):
        print("API AI response", response['result']['fulfillment']['speech'])
        return (response['result']['fulfillment']['speech'])
    else:
        return ("Sorry, I couldn't understand that question")

#def standardize_message_text(text):

    #sms='kia aadatein aaaaaaaaaaaa aachi'
#    tokenizedWords = nltk.word_tokenize(text)

#    for word in tokenizedWords:
#        for key, value in dictionaryRomanUrdu.items():
#            if(word in value):
#                indexInList=tokenizedWords.index(word)
#                tokenizedWords[indexInList]=key

#    sentence="".join([" "+i if not i.startswith("'") and i not in string.punctuation else i for i in tokenizedWords]).strip()
#    return sentence

if __name__ == '__main__':
    app.run()
