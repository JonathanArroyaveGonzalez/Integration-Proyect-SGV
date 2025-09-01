from json import loads
import requests

from settings.models.config import Config

def login(db_name):

    c = Config()
    config_data = c.get_config(db_name, 'contapyme')['contapyme']

    email = config_data["email"]
    password = config_data["password"]
    iapp = config_data["iapp"]
    url = config_data["url"]
    
    endpoint = '/TBasicoGeneral/"GetAuth"/'
    # URL for the POST request
    url = url + endpoint
    
    credentials = {
        'email': email,
        'password': password,
        'idmaquina': '',
    }

    # Loading parameters for the request
    payload = {
        '_parameters': [credentials, '', iapp, '0'],
    }

    try:
        # Sends a POST request to ContaPyme
        response = requests.post(url, json=payload, timeout=15)

        # Extracts data from the response
        data = loads(response.content).get('result', [])[0]

        header = data.get('encabezado', {})
        result = header.get('resultado', '')
        
        # Checks the result
        if result == 'true':
            # Extracts the key agent
            reply = data.get('respuesta', {}).get('datos', {})
            keyagent = reply.get('keyagente', '')
            return keyagent
        else:
            return None

    except requests.Timeout:
        raise TimeoutError("The login request timed out after 60 seconds.")     
    except Exception as e:
        raise ValueError(e)