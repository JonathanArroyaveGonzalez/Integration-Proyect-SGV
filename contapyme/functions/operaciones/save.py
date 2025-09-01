from json import loads
import requests

from contapyme.functions.login.login import login
from settings.models.config import Config


def save_operation(db_name, inumoper, itdoper, order):
    try:
        # Authenticate to obtain a token
        keyagent = login(db_name)

        # Check the token
        if not keyagent:
            raise ValueError("User authentication failed")

        c = Config()
        config_data = c.get_config(db_name, "contapyme")["contapyme"]

        iapp = config_data["iapp"]
        url = config_data["url"]

        endpoint = '/TCatOperaciones/"DoExecuteOprAction"/'

        # URL for the POST request
        url = url + endpoint

        # Constructs the parameters
        datajson = {
            "accion": "SAVE",
            "operaciones": [{"inumoper": inumoper, "itdoper": itdoper}],
            "oprdata": order,
        }

        # Constructs the payload
        payload = {"_parameters": [datajson, keyagent, iapp, "0"]}
        #return payload
        try:
            # Sends a POST request to fetch operation data in ContaPyme
            response = requests.post(url, json=payload, timeout=180)

            print(response.json())
            # return response
            # Extracts data from the response
            data = loads(response.content).get("result", [])[0]
            reply = data.get("respuesta", {}).get("datos", {})

            if reply:
                return reply
            else:
                raise ValueError(data['encabezado']['mensaje'])

        except requests.Timeout:
            raise TimeoutError("The request timed out after 180 seconds.")
        # If there is a query error
        except Exception as e:
            raise ValueError(e)

    # If there is a authentication error
    except Exception as e:
        raise ValueError(e)
