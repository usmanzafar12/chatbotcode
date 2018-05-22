import sys
import logging
import json, requests
from flask import Flask, session, Response, request, jsonify, make_response
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
#from word_normalization import *
import redis
#from urdu_flow import *
from english_flow import *
#from google.cloud import vision
#from google.cloud.vision import types


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
PAT = 'EAACh9MQ3zy8BAMLZBBvZCoOFwLU3E8nwNsQ6mnXud9dlZB6a8izcvZChkaVbB7sP9lJXnZCooXtwALKk7bwRAWqgb5Kowl13BdppFDgEZA3NLaZCOCZBTQ3RCUWsGueZCw4lAkO3mvzKD7CnOCZCV3PWucUO7XPZCFdn82SpyDTJkoH6QZDZD'
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
	try:
		# Primary function in which whole code is run
		logging.info("Facebook push notification received")
		data = request.get_json()
		sender_id, recipient_id, comment_id, message_text = fb_msg_parse(data)
		session['session_id'] = hl.md5(sender_id.encode('utf-8')).hexdigest()
		message_type = message_attachment_check(data)
		if message_type == 'audio':
			send_message_response(sender_id, comment_id, 'The bot doesnt support \
			 						audio')
			return Response(status=200)

		if message_type == 'image':
			uri = get_uri(data)
			landmark = detect_landmarks_uri(uri)
			response = "You are near " + landmark
			send_message_response(sender_id, comment_id, response)
			return Response(status=200)

		#
		if lang_detect(message_text) == 'urdu':
			response = urdu_response(message_text, sender_id, \
										recipient_id, comment_id)
		else:
			response = eng_response(message_text, sender_id, \
										recipient_id, comment_id)

		# import pdb; pdb.set_trace();
		if type(response) is str:
			print("-----------Response is Here-----------")
			print(sender_id)
			print(comment_id)
			print(response)
			print("-----------Response is Here-----------")
			send_message_response(sender_id, comment_id, response)
		return Response(status=200)
	except Exception as e:
		print(e)
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


@app.route('/response/<int:id>', methods=['POST'])
def chatbot_response(id):
	message = "this is the id " + str(id) + " you sent. enjoy"
	resp = make_response(message, 200)
	return resp


@app.route('/response/<int:id>/<value>', methods=['POST'])
def verification_check(id, value):
	msg = "this is the id " + str(id) + " and string value " + str(value)
	resp = make_response(message, 200)
	return resp

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
	# import pdb; pdb.set_trace()
	if detected_lang.find('en') == -1:
		return 'urdu'
	else:
		return 'english'


def detect_landmarks_uri(uri):
	"""Detects landmarks in the file located in Google Cloud Storage or on the
	Web."""
	image_from_uri = requests.get(uri).content
	client = vision.ImageAnnotatorClient()
	image = types.Image(content=image_from_uri)
	response = client.landmark_detection(image=image)
	#logging.info("the response should be next")
	logging.info(response)
	landmarks = response.landmark_annotations
	return landmarks[0].description


def get_uri(data):
	uri = data['entry'][0]['messaging'][0]['message']\
				['attachments'][0]['payload']['url']
	return uri


def message_attachment_check(data):
	for entry in data["entry"]:
		for messaging_event in entry["messaging"]:
			if "attachments" in messaging_event["message"].keys():
				uri = messaging_event["message"]["attachments"][0]['payload']['url']
				if messaging_event["message"]["attachments"][0]['type'] == 'audio':
					return 'audio'
				if messaging_event["message"]["attachments"][0]['type'] == 'image':
					return 'image'
	return None

if __name__ == '__main__':
	app.run(port=4000)
