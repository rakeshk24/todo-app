import logging
import os

LOG_FILE = '/var/log/todo-app/app.log'
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
MAX_LOG_BYTES = 10 * 1024 * 1024
LOG_BACKUP_COUNT = 3


def setup_logging():
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(level=level, format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    logger = logging.getLogger('todo_app')
    logger.setLevel(level)

    if not os.environ.get('VERCEL') and not os.environ.get('TESTING'):
        try:
            log_dir = os.path.dirname(LOG_FILE)
            os.makedirs(log_dir, exist_ok=True)
            from logging.handlers import RotatingFileHandler
            fh = RotatingFileHandler(LOG_FILE, maxBytes=MAX_LOG_BYTES, backupCount=LOG_BACKUP_COUNT)
            fh.setLevel(level)
            fh.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT))
            logger.addHandler(fh)
        except:
            pass

    return logger
