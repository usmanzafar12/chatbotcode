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
from query import *
from helper import *
from facebook_send import *
import pandas as pd
from nltk import word_tokenize
import re

try:
	import apiai
except ImportError:
	sys.path.append(
		os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
	)
	import apiai

app = Flask(__name__)
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
	logging.info("Facebook message parsed")
	#message_text = normalize(message_text, dictionary)
	message_text = ner(message_text)
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
			query(insert_query,(0,0,0,timestamp,sender_id,comment_id,\
								message_text,'','',''))
			logging.info("facebook message inserted in db")
			return sender_id, recipient_id, comment_id, message_text


def google_translate(user_text, comment_id):
	'''
	this function will translate the received text using google translate
	'''
	translator = Translator(service_urls = ['translate.google.com.pk'])
	detected_lang = translator.detect(user_text).lang
	if(detected_lang.find('en')!=-1):
		#passthrough for english
		trans_input = user_text
		query(update_query_translation, (trans_input, comment_id))
		return trans_input
	else:
		mid_trans = translator.translate(user_text, src="hi", dest = "ur").text
		trans_input = translator.translate(mid_trans, src = "ur", dest = "en").text
		query(update_query_translation, (trans_input, comment_id))
		logging.info("TEXT Translated")
		return trans_input


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





if __name__ == '__main__':
	app.run(port=4000)
