import logging

logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('./data/log.txt', mode='w')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)