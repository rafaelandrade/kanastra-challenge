from os import environ

from dotenv import load_dotenv

load_dotenv()

config = {}

if environ.get('API_ENV') == 'local':
    config['MONGO_URL'] = environ.get('LOCAL_MONGO_URL')
    config['MONGO_DB'] = environ.get('LOCAL_MONGO_DB')

if environ.get('API_ENV') == 'production':
    config['MONGO_URL'] = environ.get('PRODUCTION_MONGO_URL')
    config['MONGO_DB'] = environ.get('PRODUCTION_MONGO_DB')