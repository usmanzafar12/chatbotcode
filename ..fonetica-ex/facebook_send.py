
import logging
import sys
import json, requests


PAT = 'EAACh9MQ3zy8BAJuw2AdCaSezuGIio39aVlFENWK1ZA0LHVEcU3BnhqFRrUJrZAKEfCdp9DZBJa8UAZB0ZCFb7FWtJ6mZAzUVenZCzEcJX8vg7HxEAwgcL93YOfXxZCb9CJygQpMo8J49JR6AGYh67CeoMGZAAs9OZCsUPrhhA19wFmlAZDZD'

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)

def send_message_response(sender_id, comment_id, message_text):
	sentenceDelimiter = ". "
	messages = message_text.split(sentenceDelimiter)
	logging.info(messages)
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
		"message":{
	"text": message_text,
	}}))
