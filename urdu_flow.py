from query import *
from helper import *
from googletrans import Translator
from flask import Response, session
from facebook_send import *
from word_normalization import *


def urdu_response(message_text, sender_id, recipient_id, comment_id):
	#message_text = urdu_normalization.eng_word_correction(message_text)
	query(update_query_normalization, (message_text, comment_id))
	extracted_entities, message_text = ner(message_text)
	try:
		translated_message = google_translate(message_text, comment_id)

		if not translated_message:
			translated_message = "There was an error with the \
													 communication service"
			translated_message = restore_entities(extracted_entities, \
												translated_message)
	except:
		send_message(sender_id, comment_id, "There was an error with the \
										 translation service")
		logging.info("This is the translated message")
		logging.info(translated_message)
		return Response(status=200)
	try:
		api_response = api_ai_query_urdu(translated_message, comment_id)
	except:
		send_message(sender_id, comment_id, "There was an error with fetching \
										 the response from the AI")
		return Response(status=200)
	return api_response


def api_ai_query_urdu(text, comment_id):
	logging.info("Api AI entered")
	api_endpoint = "https://api.dialogflow.com/v1/query/?v=20150910"
	#logging.info("API AI QUERY CALLED")
	headers = {'Authorization' : 'Bearer de5f147f221d4154b5a590f8ccb9e2a7',
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


def google_translate(user_text, comment_id):
	'''
	this function will translate the received text using google translate
	'''
	logging.info("This is from the GOOGLE TRANSLATE FUNCTION")
	logging.info(user_text)
	translator = Translator(service_urls = ['translate.google.com.pk'])
	mid_trans = translator.translate(user_text, src="hi", dest = "ur").text
	logging.info(mid_trans)
	trans_input = translator.translate(mid_trans, src = "ur", dest = "en").text
	query(update_query_translation, (trans_input, comment_id))
	logging.info("TEXT Translated")
	return trans_input
