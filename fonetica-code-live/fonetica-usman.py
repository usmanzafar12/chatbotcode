import sys
import logging
import json, requests
from flask import Flask, session, Response, request, jsonify
import logging
from googletrans import Translator
import string
from nltk import compat
from nltk import word_tokenize
from nltk.corpus import stopwords
import psycopg2
from query import *
from helper import *
from facebook_send import *
import pandas as pd
from nltk import word_tokenize
import re
import hashlib as hl
import uuid
from word_normalization
import redis

try:
	import apiai
except ImportError:
	sys.path.append(
		os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
	)
	import apiai


app = Flask(__name__)
app.secret_key = str(uuid.uuid4())
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)
PAT = 'EAACh9MQ3zy8BAJuw2AdCaSezuGIio39aVlFENWK1ZA0LHVEcU3BnhqFRrUJrZAKEfCdp9DZBJa8UAZB0ZCFb7FWtJ6mZAzUVenZCzEcJX8vg7HxEAwgcL93YOfXxZCb9CJygQpMo8J49JR6AGYh67CeoMGZAAs9OZCsUPrhhA19wFmlAZDZD'
VERIFY_TOKEN = 'test'
CLIENT_ACCESS_TOKEN = '3a67ab4afb49424587183ae8b04bf88b'
ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)


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


@app.route('/', methods=['POST'])
def handle_message_dummy():
	# Primary function in which whole code is run
	logging.info("Facebook push notification received")
	dictionary = load_dictionary()
	data = request.get_json()
	sender_id, recipient_id, comment_id, message_text = fb_msg_parse(data)
	session['session_id'] = hl.md5(str(sender_id)).hexdigest()
	logging.info("Facebook message parsed")
	message_text = normalization_redis.eng_word_correction(message_text)
	query(update_query_normalization, (message_text, comment_id))

	#message_text = ner(message_text)
	try:
		translated_message = google_translate(message_text, comment_id)
	except:
		send_message(sender_id, comment_id, "There was an error with the \
											 translation service")
		return Response(status=200)
	try:
		api_response = api_ai_query(translated_message, comment_id)
	except:
		send_message(sender_id, comment_id, "There was an error with fetching \
										 the response from the AI")
		return Response(status=200)
	send_message_response(sender_id, comment_id, api_response)
	return Response(status=200)


def fb_msg_parse(data):
	for entry in data["entry"]:
		for messaging_event in entry["messaging"]:
			try:
				message_text = messaging_event["message"]["text"]
			except Exception as e:
				message_text = 'NEW'
			sender_id = messaging_event["sender"]["id"]
			recipient_id = messaging_event["recipient"]["id"]
			comment_id = messaging_event["message"]["mid"]
			timestamp = get_timestamp(messaging_event['timestamp'])
			#updated
			query(insert_query,(0,0,0,timestamp,sender_id,comment_id,\
								message_text,'','','',''))
			logging.info("facebook message inserted in db")
			return sender_id, recipient_id, comment_id, message_text


def google_translate(user_text, comment_id):
	'''
	this function will translate the received text using google translate
	'''
	#translator = Translator(service_urls = ['translate.google.com.pk'])
	#detected_lang = translator.detect(user_text).lang
	#if(detected_lang.find('en')!=-1):
		#passthrough for english
	trans_input = user_text
	query(update_query_translation, (trans_input, comment_id))
	return trans_input
	#else:
	#	mid_trans = translator.translate(user_text, src="hi", dest = "ur").text
	#	trans_input = translator.translate(mid_trans, src = "ur", dest = "en").text
	#	query(update_query_translation, (trans_input, comment_id))
	#	logging.info("TEXT Translated")
	#	return trans_input


"""
def api_ai_query(text, comment_id):
	logging.info("Api AI entered")
	request = ai.text_request()
	request.query = text
	response = json.loads(request.getresponse().read().decode('utf-8'))
	responseStatus = response['status']['code']
	if (responseStatus == 200):
		response = response['result']['fulfillment']['speech']
		query(update_query_apiai,(response, comment_id))
		logging.info("api ai returning")
		return response
	else:
		response = "Sorry, I couldn't understand that question"
		query(update_query_apiai,(response, comment_id))
		logging.info("api ai returning")
		return response
"""


def api_ai_query(text, comment_id):
	logging.info("Api AI entered")
	api_endpoint = "https://api.dialogflow.com/v1/query/?v=20150910"
	#logging.info("API AI QUERY CALLED")
	headers = {'Authorization' : 'Bearer 3a67ab4afb49424587183ae8b04bf88b',
			   'Content-Type' : 'application/json'}
	body = {'query' : text,
			'lang' : 'en',
			'sessionId' :  session['session_id'] }
	body_json = json.dumps(body)
	apiai_result = requests.post(api_endpoint, \
								 headers=headers, data=body_json).json()
	logging.info(apiai_result)
	logging.info("Dict, %s", apiai_result['result']['fulfillment']['speech'])
	api_response = apiai_result['result']['fulfillment']['speech']
	query(update_query_apiai, (api_response, comment_id))
	return api_response


@app.route('/dialogflow', methods=['POST'])
def dialogflow():
	# Primary function in which whole code is run
	data = request.get_json()
	response_message = data['result']['fulfillment']['speech']

	if data['result']['metadata']['intentName'] == 'transfer-start':
		#logging.info(data)
		webhook_data = {"followupEvent": {
				      "name": "test-transfer-event"
				   }}

	elif data['result']['metadata']['intentName'] == \
			'transfer-test-follow_dialog_context':
		#logging.info(data)
		#logging.info(data['result']['contexts'][1]['name'])
		logging.info("Is this working?")
		contexts = remove_contexts('transfer-ongoing', data)
		webhook_data = {"speech" : response_message,
				"displayText" : "",
				"contextOut" : contexts,
				"source" : "webhook" }

	else:
		webhook_data = {"speech" : response_message,
				"displayText" : "",
				"contextOut" : [{
				"name": "transfer-ongoing",
				"lifespan": 1,
				  }],
				  "source" : "webhook" }
		logging.info("DATA AFTER REMOVE CONTEXTS")
		logging.info(data)
		#logging.info("DATA AFTER REMOVE CONTEXTS")
		#logging.info(data)
	test = jsonify(webhook_data)
	logging.info(json.dumps(webhook_data))
	#resp = Response(test, status=200, mimetype='application/json')s
	return test


if __name__ == '__main__':
	app.run(port=4000)
