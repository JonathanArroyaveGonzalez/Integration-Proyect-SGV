# import requests
# import time

# # --- Configuración de tu App ---
# CLIENT_ID = "4013894436730927"
# CLIENT_SECRET = "qAw4JL6gGzmFFMote6C9WlzhIWFXhTpO"
# REDIRECT_URI = "https://web.copernicowms.com"

# # --- Datos del usuario test ---
# REFRESH_TOKEN = "TG-68cc1fdfe6f3b50001130c56-2679650708"

# ML_BASE_URL = "https://api.mercadolibre.com"


# def get_access_token(refresh_token: str) -> dict:
#     """
#     Obtiene un access token válido usando el refresh token.
#     """
#     url = f"{ML_BASE_URL}/oauth/token"
#     payload = {
#         "grant_type": "refresh_token",
#         "client_id": CLIENT_ID,
#         "client_secret": CLIENT_SECRET,
#         "refresh_token": refresh_token,
#         "redirect_uri": REDIRECT_URI
#     }
#     response = requests.post(url, data=payload)
#     response.raise_for_status()
#     return response.json()


# def get_items(user_id: str, access_token: str) -> list:
#     """
#     Obtiene los items de un usuario de test.
#     """
#     url = f"{ML_BASE_URL}/users/{user_id}/items/search"
#     headers = {"Authorization": f"Bearer {access_token}"}
#     resp = requests.get(url, headers=headers)
#     resp.raise_for_status()
#     return resp.json().get("results", [])


# if __name__ == "__main__":
#     # 1️⃣ Obtener access token
#     token_data = get_access_token(REFRESH_TOKEN)
#     access_token = token_data["access_token"]
#     user_id = token_data["user_id"]
#     expires_in = token_data["expires_in"]

#     print("Access Token:", access_token)
#     print("User ID:", user_id)
#     print("Expires in:", expires_in, "seconds")

#     # 2️⃣ Usar el token para obtener items
#     try:
#         items = get_items(user_id, access_token)
#         print("Items del usuario test:")
#         for item in items:
#             print(item)
#     except requests.exceptions.HTTPError as e:
#         print("Error al consultar items:", e)
import requests

# --- Base URL ---
ML_BASE_URL = "https://api.mercadolibre.com"

# --- Access Token y User ID del usuario test ---
ACCESS_TOKEN = "APP_USR-4013894436730927-091811-340efa459158a16769ebef94807d7723-2679650708"
USER_ID = "2679650708"


def get_items():
    url = f"{ML_BASE_URL}/users/{USER_ID}/items/search"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json().get("results", [])


def create_test_item():
    url = f"{ML_BASE_URL}/items"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "title": "Item de Prueba - Por favor, NO OFERTAR",
        "category_id": "MCO1911",
        "price": 50000,
        "currency_id": "COP",
        "available_quantity": 10,
        "buying_mode": "buy_it_now",
        "condition": "new",
        "listing_type_id": "gold_special",
        "sale_terms": [
            {"id": "WARRANTY_TYPE", "value_name": "Garantía del vendedor"},
            {"id": "WARRANTY_TIME", "value_name": "90 días"}
        ],
        "pictures": [
            {"source": "http://mla-s2-p.mlstatic.com/968521-MLA20805195516_072016-O.jpg"}
        ],
        "attributes": [
            {"id": "SELLER_SKU", "value_name": "7898095297749"},
            {"id": "BRAND", "value_name": "Marca del producto"},
            {"id": "MODEL", "value_name": "Modelo de prueba"},
            {"id": "EAN", "value_name": "7898095297749"},
            {"id": "COLOR", "value_name": "Rojo"},
            {"id": "SIZE", "value_name": "M"},
            {"id": "GENDER", "value_name": "hombre"}
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code in [200, 201]:
        print("Item creado con éxito:", response.json())
    else:
        print("Error al crear item:", response.status_code, response.json())


if __name__ == "__main__":
    items = get_items()
    print("Items del usuario test:", items)

    # Crear un item de prueba
    create_test_item()
