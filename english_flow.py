from query import *
from helper import *
from word_normalization import *

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


def eng_response(message_text, sender_id, recipient_id, comment_id):
	message_text = normalization_redis.eng_word_correction(message_text)
	query(update_query_normalization, (message_text, comment_id))
	try:
		api_response = api_ai_query(translated_message, comment_id)
	except:
		send_message(sender_id, comment_id, "There was an error with fetching \
										 the response from the AI")
		return Response(status=200)
	return api_response
