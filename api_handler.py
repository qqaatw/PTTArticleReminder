import json

from api import *

def load_config():
    enabled_apis = []
    with open('config.json', 'r', encoding='utf8') as f:
        config = json.load(f)
    for service in config['services']:
        if service['enable'] == 'true':
            assert service['name'] in SUPPORTED_SERVICES, \
                'Specified service is not supported: {}'.format(service['name'])
            if service['name'] == 'line':
                enabled_apis.append(LineAPI(service['client_list'], service['channel_access_token']))
            elif service['name'] == 'telegram':
                enabled_apis.append(TelegramAPI(service['client_list'], service['bot_token']))
    return enabled_apis

enabled_apis = load_config()

def send_message(text, receiver):
    for enabled_api in enabled_apis:
        if enabled_api.send_message(text, receiver):
            return
    raise RuntimeError('All APIs are unavailable.')

def broadcast_message(text):
    for enabled_api in enabled_apis:
        if enabled_api.broadcast_message(text):
            return
    raise RuntimeError('All APIs are unavailable.')