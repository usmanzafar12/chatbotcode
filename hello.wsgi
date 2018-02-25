import sys
import logging
logging.basicConfig(strem=sys.stderr,level=logging.INFO)

sys.path.insert(0, "/var/www/fonetica-code-live")
sys.path.insert(0, "/var/www/fonetica-code-live/site-packages")

#sys.path.insert(0, "/home/ubuntu/.local/lib/python2.7/site-packages")
logging.info(sys.path)
from main import app as application
