import sys
import logging
logging.basicConfig(strem=sys.stderr,level=logging.INFO)

sys.path.insert(0, "/var/www/chatbot")
sys.path.insert(0, "/var/www/chatbot/site-packages")

sys.path.insert(0, "/usr/local/lib/python2.7/dist-packages")
logging.info(sys.path)
from main import app as application
