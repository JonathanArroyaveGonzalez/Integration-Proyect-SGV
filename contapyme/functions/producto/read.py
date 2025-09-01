from json import loads
import requests

from contapyme.functions.login.login import login
from settings.models.config import Config


def read_items(db_name, irecurso):
    try:
        keyagent = login(db_name)

        # Check the token
        if not keyagent:
            raise ValueError('User authentication failed')
        
        c = Config()
        config_data = c.get_config(db_name, 'contapyme')['contapyme']

        iapp = config_data["iapp"]
        url = config_data["url"]
        
        endpoint = '/TCatElemInv/"GetListaElemInv"/'
        
        # URL for the POST request
        url = url + endpoint
        
        # Constructs the parameters
        params = {
            "datospagina": {
                "cantidadregistros": "1",
                "pagina": "1"
            },
            "datosfiltro": {
                "sql":f"irecurso='{irecurso}'"
            },
        }

        # Constructs the payload
        payload ={ 
            "_parameters" : [ params, keyagent, iapp, '0' ] 
        }

        try:
            # Sends a POST request to fetch item data in ContaPyme
            response = requests.post(url, json=payload)

            # Extracts data from the response
            data = loads(response.content).get('result', [])[0]
            
            # Extracts the item data
            reply = data.get('respuesta', {}).get('datos', {})  
            
            if len(reply) >= 1:
                item = reply[0]
                return item
            else:
                return {}   
            
        # If there is a query error             
        except Exception as e:
            raise ValueError(e)

    # If there is a authentication error
    except Exception as e:
        raise ValueError(e)
    
