MercadoLibre App (API v1 + Services)

Resumen
- Esta app integra MercadoLibre con el WMS mediante una arquitectura por capas: api (v1), services, functions y utils.
- Los endpoints existentes se mantienen, redirigiendo ahora a vistas más delgadas.

Estructura principal
- api/v1
  - products.py: Endpoints de productos (listar, crear, actualizar por id; sync masivo; sync específicos; status)
  - customers.py: Endpoints de clientes (crear y actualizar por uno o múltiples IDs)
- services
  - product_service.py: Lógica de negocio de productos (list/create en ML, update ML->WMS)
  - customer_service.py: Lógica de negocio de clientes (create/update en WMS)
  - barcode_service.py: Fachada para operaciones de códigos de barras (delegación a functions)
- functions: Lógica funcional ya existente (se mantiene)
- utils: Helpers compartidos (respuestas, auth, api_client, mappers)

Rutas expuestas (mercadolibre/urls.py)
- Auth
  - POST/GET: /wms/ml/v1/auth/refresh (vista existente)
- Productos
  - GET/POST: /wms/ml/v1/products (api.v1.products.products)
  - PUT: /wms/ml/v1/products/update/<product_id> (api.v1.products.update_product)
  - POST: /wms/ml/v1/products/update (api.v1.products.update_product_post)
  - POST: /wms/ml/v1/products/sync/ (api.v1.products.sync_products_view)
  - GET: /wms/ml/v1/products/sync/status/ (api.v1.products.sync_status_view)
  - POST: /wms/ml/v1/products/sync/specific/ (api.v1.products.sync_specific_products_view)
- Clientes
  - POST: /wms/ml/v1/customer/sync/ (api.v1.customers.create)
  - PUT/PATCH: /wms/ml/v1/customer/update/ (api.v1.customers.update)

Patrones de uso
- Autenticación: Los endpoints de sync/update hacia el WMS aceptan Authorization en el header.
- Manejo de respuestas: Se estandarizó con utils/response_helpers.py (success/error/partial_success).
- Validaciones: Las vistas v1 son delgadas y delegan la lógica a services, que a su vez reutilizan functions preexistentes.

Ejemplos
- Listar productos ML
  - GET /wms/ml/v1/products
- Crear producto ML
  - POST /wms/ml/v1/products
  - Body: JSON del item ML
- Actualizar producto ML->WMS (path)
  - PUT /wms/ml/v1/products/update/MLA123
- Actualizar producto ML->WMS (body)
  - POST /wms/ml/v1/products/update { "product_id": "MLA123" }
- Sincronizar productos (masivo)
  - POST /wms/ml/v1/products/sync { "use_parallel": true, "assume_new": true }
- Sincronizar productos (específicos)
  - POST /wms/ml/v1/products/sync/specific { "product_ids": ["MLA1","MLA2"], "assume_new": true }
- Crear clientes
  - POST /wms/ml/v1/customer/sync { "ml_customer_id": "123" } o { "ml_customer_ids": ["123","456"] }
- Actualizar clientes
  - PUT /wms/ml/v1/customer/update { "ml_customer_id": "123" } o { "ml_customer_ids": ["123","456"] }

Buenas prácticas y próximos pasos
- Migrar vistas legacy restantes (Barcode si decides exponer endpoints públicos) a api v1.
- Añadir tests unitarios para services y api v1.
- Considerar DRF para serialización/validación más robusta a futuro.
- Centralizar configuración (variables de entorno) y tipado estricto.
