Documentación de la App MercadoLibre (API v1 + Services)

Objetivo
- Integrar MercadoLibre con el WMS mediante servicios y funciones reutilizables, exponiendo endpoints REST consistentes.

Arquitectura
- api/v1: Endpoints delgados (views) que delegan a services y estandarizan respuestas.
- services: Lógica de negocio (ML/WMS) y orquestación; ocultan detalles de functions y clientes HTTP.
- functions: Lógica funcional existente; se mantiene para compatibilidad (Product, Customer, BarCode, Auth).
- utils: Utilidades compartidas (respuesta, auth, api_client, mappers).

Configuración relevante
- settings.WMS_BASE_URL: URL base del WMS (se trimea el trailing slash). Ej: http://localhost:8000
- Credenciales ML: se leen vía mercadolibre.functions.Auth.mongo_config.get_meli_config().

Rutas (mercadolibre/urls.py)
- Auth
  - POST/GET /wms/ml/v1/auth/refresh
- Productos
  - GET/POST /wms/ml/v1/products
  - PUT /wms/ml/v1/products/update/<product_id>
  - POST /wms/ml/v1/products/update
  - POST /wms/ml/v1/products/sync
  - GET /wms/ml/v1/products/sync/status
  - POST /wms/ml/v1/products/sync/specific
- Clientes
  - POST /wms/ml/v1/customer/sync
  - PUT/PATCH /wms/ml/v1/customer/update
- Barcodes (opcional si decides agregar a urls)
  - GET /wms/ml/v1/barcodes/<ean>
  - POST /wms/ml/v1/barcodes/sync_from_meli

Contratos de entrada principales
- Authorization: En endpoints que llegan al WMS, si se envía en cabecera se propaga.
- products (POST): body JSON con la definición de item de MercadoLibre.
- products/update (POST): { "product_id": "MLA123" }
- products/sync (POST): { "use_parallel"?: bool, "assume_new"?: bool }
- products/sync/specific (POST): { "product_ids": string[], "assume_new"?: bool, "use_parallel"?: bool }
- customer/sync (POST): { "ml_customer_id": string } o { "ml_customer_ids": string[] }
- customer/update (PUT/PATCH): { "ml_customer_id": string } o { "ml_customer_ids": string[] }
- barcodes/sync_from_meli (POST): { "meli_items": dict | dict[], "assume_new"?: bool }

Estándar de respuestas
- Éxito: { "status": "success", "message": string, "data"?: any }
- Error: { "status": "error", "message": string, "errors"?: any, "error_code"?: string }
- Éxito parcial: { "status": "partial_success", "message": string, "summary": { total_processed, successful, failed }, ... }

Buenas prácticas
- Mantener vistas (api/v1) delgadas y tests por capa (api, services, functions).
- Reutilizar utils/response_helpers para uniformidad.
- Añadir tipado y validación de entrada progresivamente.

Roadmap sugerido
- Tests unitarios y de integración con mocks a ML/WMS.
- DRF para serializers/validators.
- Settings por entorno y variables .env centralizadas.
