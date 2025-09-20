

def ml_product_to_wsm(ml_product: dict):

    return {
        "productoean": ml_product.get("id"),
        "descripcion": ml_product.get("description"),
        "referencia": ml_product.get("id"),
        "um1": ml_product,
        "presentacion": ml_product,
        "item": ml_product.get("title"),
        "grupo": ml_product.get(''),
        "nuevoean": ml_product,
        "fecharegistro": ml_product,
        "procedencia": ml_product.get("selle_address.state"),
        "preciounitario": ml_product.get("price"),
    }
