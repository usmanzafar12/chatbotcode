import sys
import logging
logging.basicConfig(strem=sys.stderr,level=logging.INFO)

sys.path.insert(0, "/var/www/Phonetica")
sys.path.insert(0, "/var/www/Phonetica/site-packages")

#sys.path.insert(0, "/home/ubuntu/.local/lib/python2.7/site-packages")
logging.info(sys.path)
from fonetica-usman import app as application
