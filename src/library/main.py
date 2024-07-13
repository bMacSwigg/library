import logging

from library.config import APP_CONFIG
from library.ui.ui import AppWindow

FMT = '%(asctime)s %(levelname)s:%(name)s %(message)s'
logging.basicConfig(filename=APP_CONFIG.log_file(), level=logging.INFO, format=FMT)
logger = logging.getLogger(__name__)

logger.info('Start')
try:
    aw = AppWindow()
    logger.info('Initialized AppWindow')
    aw.main()
except Exception as e:
    logger.error('Execution hit an error', exc_info=e)
logger.info('End')
