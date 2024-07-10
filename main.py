import logging

from library.constants import *
from library.ui.ui import AppWindow

FMT = '%(asctime)s %(levelname)s:%(name)s %(message)s'
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format=FMT)
logger = logging.getLogger(__name__)

logger.info('Start')
try:
    aw = AppWindow()
    logger.info('Initialized AppWindow')
    aw.main()
except:
    # execution context will be logged automatically
    logger.error('Execution hit an error')
logger.info('End')
