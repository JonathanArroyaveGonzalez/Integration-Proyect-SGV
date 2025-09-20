import requests

ML_BASE_URL = "https://api.mercadolibre.com"

# ⚡ Configuración con los tokens actuales
ACCESS_TOKEN = "APP_USR-4013894436730927-091810-80594d566859ef30bc6a29edc7ce6a06-2679650708"
ML_USER_ID = "2679650708"   # nuevo user_id que te devolvió Mercado Libre


def get_items_from_user() -> list[str]:
    """Obtiene todos los IDs de publicaciones del usuario"""
    url = f"{ML_BASE_URL}/users/{ML_USER_ID}/items/search"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json().get("results", [])


def get_item_detail(item_id: str) -> dict:
    """Obtiene los detalles completos de un ítem"""
    url = f"{ML_BASE_URL}/items/{item_id}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()


def get_item_description(item_id: str) -> str:
    """Obtiene la descripción en texto plano del ítem"""
    url = f"{ML_BASE_URL}/items/{item_id}/description"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json().get("plain_text", "")
    return ""


def extract_attribute(attributes: list[dict], attr_id: str) -> str:
    """Busca un atributo específico por su ID (ej: SELLER_SKU, GTIN)"""
    for attr in attributes:
        if attr.get("id") == attr_id:
            return attr.get("value_name", "")
    return ""


def extract_all_items() -> list[dict]:
    """Extrae todos los ítems publicados del usuario"""
    item_ids = get_items_from_user()
    extracted = []

    for item_id in item_ids:
        try:
            item = get_item_detail(item_id)
            description = get_item_description(item_id)

            attributes = item.get("attributes", [])
            sku = item.get("seller_custom_field") or extract_attribute(attributes, "SELLER_SKU")
            ean = extract_attribute(attributes, "GTIN")

            extracted.append({
                "id": item["id"],
                "sku": sku,
                "ean": ean,
                "title": item.get("title"),
                "description": description,
                "category_id": item.get("category_id"),
                "price": item.get("price"),
                "currency": item.get("currency_id"),
                "stock": item.get("available_quantity")
            })
        except Exception as e:
            print(f"Error procesando item {item_id}: {e}")

    return extracted


if __name__ == "__main__":
    items = extract_all_items()
    for it in items:
        print(it)
