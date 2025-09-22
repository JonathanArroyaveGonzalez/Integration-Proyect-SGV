from mercadolibre.utils import make_authenticated_request, get_meli_api_base_url
from dotenv import load_dotenv
import os 

load_dotenv()

base_url = get_meli_api_base_url()
user_account_id = os.getenv("USER_ACCOUNT_ID")
url = f"{base_url}/users/{user_account_id}/items/search"

"""
Metodo que extrae los IDs de los productos de la cuenta de MercadoLibre
"""
def extract_product_ids():
    response = make_authenticated_request("GET", url)
    if response.status_code == 200:
        meli_item = response.json()["results"]
        return meli_item
    else:
        print(f"Error {response.status_code}: {response.text}")
        return []