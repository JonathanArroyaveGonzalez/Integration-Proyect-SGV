from json import loads
import requests

from contapyme.functions.login.login import login
from settings.models.config import Config

def read_purchase_orders(db_name, snumsop):
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
        
        endpoint = '/TCatOperaciones/"DoExecuteOprAction"/'
        
        # URL for the POST request
        url = url + endpoint
                
        # Constructs the parameters
        params = {
            'accion': "LOAD",
            'operaciones': [
                {
                'itdoper': 'ORD5',
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
                cellar = reply.get('datosprincipales', {}).get('iinventario', None)
                approved = reply.get('encabezado', {}).get('bconfirmaenviofe', None)

                if doctoerp:
                    if not approved:
                        raise ValueError(f'The order {doctoerp} is not approved')
                    
                    if cellar != '10':
                        raise ValueError(f'The order {doctoerp} belongs to another store')

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
    
