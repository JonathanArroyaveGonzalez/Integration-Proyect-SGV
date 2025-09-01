from json import loads
import requests

from contapyme.functions.login.login import login
from settings.models.config import Config

def read_thirdparty(db_name, init):
    try:
        # Authenticate to obtain a token
        keyagent = login(db_name)

        # Check the token
        if not keyagent:
            raise ValueError('User authentication failed')
        
        c = Config()
        config_data = c.get_config(db_name, 'contapyme')['contapyme']

        iapp = config_data["iapp"]
        url = config_data["url"]
        
        endpoint = '/TCatTerceros/"GetInfoTercero"/'
        
        # URL for the POST request
        url = url + endpoint
        
        # Constructs the parameters
        params = {
            "init": init
        }
        
        # Constructs the payload
        payload ={ 
            "_parameters" : [ params, keyagent, iapp , '0' ] 
        }

        try:
            # Sends a POST request to fetch client data in ContaPyme
            response = requests.post(url, json=payload)
            
            # Extracts data from the response
            data = loads(response.content).get('result', [])[0]
            
            header = data.get('encabezado', {})
            result = header.get('resultado', '')
            
            # Checks the result
            if result == 'true':
                # Extracts the client data
                reply = data.get('respuesta', {}).get('datos', {})
                basicinfo = reply.get('infobasica', {})
                return basicinfo
            else:
                return {}

        # If there is a query error             
        except Exception as e:
            raise ValueError(e)

    # If there is a authentication error
    except Exception as e:
        raise ValueError(e)
    
