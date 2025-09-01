from json import loads
import requests

from contapyme.functions.login.login import login
from settings.models.config import Config

def read_operations(db_name, itdoper, quantity=None):
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
        
        endpoint = '/TCatOperaciones/"GetListaOperaciones"/'
        
        # URL for the POST request
        url = url + endpoint

        if quantity is None:
            quantity = 100

        # Constructs the parameters
        params = {
            "datospagina": {
                "cantidadregistros": quantity,
                "pagina": "1"
            },
            "camposderetorno": [
                "snumsop"
            ],
            "ordenarpor": {
                "fultima": "desc"
            },
            "datosfiltro": {
                "banulada": "F"
            },
            "itdoper": [
                itdoper
            ]
        }

        # Constructs the payload
        payload ={ 
            "_parameters" : [ params, keyagent, iapp , '0' ] 
        }
        
        try:
            # Sends a POST request to fetch operation data in ContaPyme
            response = requests.post(url, json=payload)
            
            # Extracts data from the response
            data = loads(response.content).get('result', [])[0]
            reply = data.get('respuesta', {}).get('datos', {})
            if reply:
                return reply
            else:
                return {}
            
        # If there is a query error             
        except Exception as e:
            raise ValueError(e)

    # If there is a authentication error
    except Exception as e:
        raise ValueError(e)
    
