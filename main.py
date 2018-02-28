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
from word_normalization import *
import redis
from urdu_flow import *
from english_flow import *


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
	data = request.get_json()
	sender_id, recipient_id, comment_id, message_text = fb_msg_parse(data)
	session['session_id'] = hl.md5(str(sender_id)).hexdigest()
	logging.info("Facebook message parsed")
	if lang_detect(message_text) == 'urdu':
		response = urdu_response(message_text, sender_id, \
									recipient_id, comment_id)
	else:
		response = eng_response(message_text, sender_id, \
									recipient_id, comment_id)
	logging.info("This is the type of the response")
	logging.info(type(response))
	if type(response) is unicode:
		send_message_response(sender_id, comment_id, response)
	return Response(status=200)


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
	return test


def fb_msg_parse(data):
	logging.info(json.dumps(data))
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


def lang_detect(message_text):
	translator = Translator(service_urls = ['translate.google.com.pk'])
	detected_lang = translator.detect(message_text).lang
	logging.info(" This is the value the language detected")
	logging.info(detected_lang)
	if detected_lang.find('en') == -1:
		return 'urdu'
	else:
		return 'english'


if __name__ == '__main__':
	app.run(port=4000)
