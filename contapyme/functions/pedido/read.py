from json import loads
import requests

from contapyme.functions.login.login import login
from settings.models.config import Config

def read_orders(db_name, type_order, snumsop):
    try:
        keyagent = login(db_name)

        # Check the token
        if not keyagent:
            raise ValueError('User authentication failed')
        
        c = Config()
        config_data = c.get_config(db_name, 'contapyme')['contapyme']

        iapp = config_data["iapp"]
        url = config_data["url"]
        
        endpoint = '/TCatOperaciones/"DoExecuteOprAction"/'
        
        # URL for the POST request
        url = url + endpoint
        
        # Constructs the parameters
        params = {
            'accion': "LOAD",
            'operaciones': [
                {
                'itdoper': type_order,
                'snumsop': snumsop
                },
            ],
        }

        # Constructs the payload
        payload ={ 
            "_parameters" : [ params, keyagent, iapp , '0' ] 
        }
        
        try:
            # Sends a POST request to fetch order data in ContaPyme
            response = requests.post(url, json=payload)
            
            # Extracts data from the response
            data = loads(response.content).get('result', [])[0]
            
            # Extracts the order data
            reply = data.get('respuesta', {}).get('datos', {})
            if reply:
                doctoerp = reply.get('encabezado', {}).get('snumsop', '')
                if doctoerp:
                    return reply
                else:
                    return {}
            else:
                raise ValueError(data['encabezado']['mensaje'])

        # If there is a query error             
        except Exception as e:
            raise ValueError(e)

    # If there is a authentication error
    except Exception as e:
        raise ValueError(e)
    
