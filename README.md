# 🛒 Sistema de Integración MercadoLibre - WMS (SGV)

[![Django](https://img.shields.io/badge/Django-5.2.5-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.14.1-green.svg)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Descripción General

Sistema empresarial de integración entre **MercadoLibre** y **WMS COPERNICO** (Sistema de Gestión de Ventas) construido con Django. Proporciona sincronización bidireccional en tiempo real de:

- 📦 **Productos**: Catálogo completo con atributos y multimedia
- 👥 **Clientes**: Información fiscal y de contacto
- 🏪 **Proveedores**: Gestión multi-moneda y multi-sucursal
- 📊 **Inventario**: Stock en tiempo real por bodega y ubicación
- 📋 **Órdenes**: Sincronización automática de pedidos (venta, compra, producción)
- 🔄 **Ajustes de Inventario**: Trazabilidad completa de movimientos

### ✨ Características Principales

- ✅ **Autenticación OAuth2** con refresh automático de tokens
- ✅ **Mapeo de datos inteligente** preservando identificadores originales
- ✅ **APIs REST unificadas** para operaciones CRUD
- ✅ **Manejo robusto de errores** con reintentos y rate limiting
- ✅ **Arquitectura escalable** con servicios centralizados
- ✅ **Logging detallado** para debugging y auditoría
- ✅ **Soporte multi-moneda** (ARS, MXN, COP, BRL, CLP, USD)

## 🏗️ Arquitectura del Sistema

### 🔧 Stack Tecnológico

| Componente | Tecnología | Versión |
|------------|-----------|---------|
| **Backend Framework** | Django | 5.2.5 |
| **Lenguaje** | Python | 3.13+ |
| **Base de Datos Config** | MongoDB | 4.14.1 |
| **Base de Datos WMS** | SQL Server | - |
| **HTTP Client** | Requests + urllib3 | 2.32.5 |
| **CORS** | django-cors-headers | 4.7.0 |
| **Environment** | python-dotenv | 1.1.1 |
| **Arquitectura** | Clean Architecture + Repository Pattern | - |

### 📁 Estructura del Proyecto

```
Integration-Proyect-SGV/
│
├── 📂 mercadolibre/                    # 🎯 App principal - Integración MercadoLibre
│   ├── functions/                      # Lógica de negocio por dominio
│   │   ├── Auth/                       # 🔐 Autenticación OAuth2
│   │   │   ├── mongo_config.py         # Configuración MongoDB
│   │   │   └── refresh_token.py        # Refresh automático de tokens
│   │   ├── Customer/                   # 👥 Gestión de clientes
│   │   │   ├── base_customer_service.py
│   │   │   ├── sync.py                 # Sincronización de clientes
│   │   │   └── update.py               # Actualización individual
│   │   ├── Product/                    # 📦 Gestión de productos
│   │   │   ├── sync.py                 # Sincronización de productos
│   │   │   └── update.py               # Actualización individual
│   │   ├── Supplier/                   # 🏢 Gestión de proveedores
│   │   │   ├── base_supplier_service.py
│   │   │   ├── sync.py                 # Sincronización de proveedores
│   │   │   └── update.py               # Actualización individual
│   │   ├── Inventory/                  # 📊 Gestión de inventario
│   │   │   ├── create.py               # Creación de inventario
│   │   │   └── update.py               # Actualización de stock
│   │   └── Order/                      # 📋 Gestión de órdenes
│   │       ├── create.py               # Creación de órdenes
│   │       └── update.py               # Actualización de estados
│   │
│   ├── services/                       # 🔗 Servicios centralizados
│   │   ├── meli_service.py             # Cliente MercadoLibre API
│   │   └── internal_api_service.py     # Cliente WMS API
│   │
│   ├── utils/                          # 🛠️ Utilidades
│   │   ├── exceptions.py               # Excepciones personalizadas
│   │   ├── response_helpers.py         # Helpers de respuesta
│   │   └── mapper/                     # Mappers de datos
│   │       └── data_mapper.py          # Transformaciones ML ↔ WMS
│   │
│   ├── views/                          # 🌐 Endpoints REST
│   │   ├── auth.py                     # Autenticación
│   │   ├── Customer.py                 # API Clientes
│   │   ├── product.py                  # API Productos
│   │   ├── Supplier.py                 # API Proveedores
│   │   ├── inventory.py                # API Inventario
│   │   └── order.py                    # API Órdenes
│   │
│   └── urls.py                         # Rutas de la app
│
├── 📂 wmsAdapterV2/                    # 🔌 Adaptador WMS COPERNICO V2
│   ├── functions/                      # Funciones por dominio
│   │   ├── Product/                    # Productos WMS
│   │   ├── Customer/                   # Clientes WMS
│   │   ├── Supplier/                   # Proveedores WMS
│   │   ├── Inventory/                  # Inventario WMS
│   │   ├── InventoryAdjustment/        # Ajustes de inventario
│   │   ├── SaleOrder/                  # Órdenes de venta
│   │   ├── PurchaseOrder/              # Órdenes de compra
│   │   └── ProductionOrder/            # Órdenes de producción
│   │
│   ├── models/                         # 📋 Modelos SQL Server
│   │   ├── TdaWmsArt.py                # Artículos
│   │   ├── TdaWmsClt.py                # Clientes
│   │   ├── TdaWmsPrv.py                # Proveedores
│   │   ├── TdaWmsDpk.py                # Órdenes de venta
│   │   ├── TdaWmsDpn.py                # Órdenes de compra
│   │   ├── TdaWmsDuk.py                # Órdenes de producción
│   │   └── ...                         # Más modelos WMS
│   │
│   ├── views/                          # Endpoints WMS
│   └── urls.py                         # Rutas del adaptador
│
├── 📂 wmsBase/                         # 🔧 Base WMS
│   ├── functions/                      # Funciones base
│   ├── models/                         # Modelos base
│   ├── views/                          # Vistas base
│   └── urls.py                         # Rutas base
│
├── 📂 project/                         # ⚙️ Configuración Django
│   ├── config_db/                      # 🗄️ Servicio MongoDB
│   │   ├── connection.py               # Conexión MongoDB
│   │   ├── models.py                   # Modelos de configuración
│   │   └── repository.py               # Repository pattern
│   │
│   ├── settings.py                     # Configuración Django
│   ├── urls.py                         # Rutas principales
│   ├── middleware.py                   # Middleware personalizado
│   ├── wsgi.py                         # WSGI config
│   └── asgi.py                         # ASGI config
│
├── � settings/                        # 🔧 Configuraciones sistema
│   ├── functions/                      # Funciones de configuración
│   │   └── read.py                     # Lectura de configs
│   └── models/                         # Modelos de configuración
│       └── config.py                   # Clases de configuración
│

## 🔄 Flujo de Datos Principal

### 1. 🔐 Autenticación OAuth2 (MercadoLibre)

```mermaid
sequenceDiagram
    participant Client
    participant Django
    participant MongoDB
    participant MercadoLibre
    
    Client->>Django: POST /wms/ml/v1/auth/
    Django->>MongoDB: MeliConfigRepository.get_config()
    MongoDB-->>Django: {client_id, client_secret, refresh_token}
    Django->>MercadoLibre: POST /oauth/token
    MercadoLibre-->>Django: {access_token, refresh_token, expires_in}
    Django->>MongoDB: MeliConfigRepository.update_tokens()
    MongoDB-->>Django: Updated successfully
    Django-->>Client: {success: true, access_token, expires_in}
```

**Características:**
- ✅ Refresh automático cuando el token expira (21,600 segundos)
- ✅ Almacenamiento seguro en MongoDB
- ✅ Validación de configuración antes de cada request
- ✅ Manejo de errores con reintentos automáticos

---

### 2. 🔄 Sincronización y Mapeo de Datos

```mermaid
flowchart TD
    A[API Request] --> B{Tipo de Operación}
    B -->|Productos| C[ProductSyncService]
    B -->|Inventario| D[InventoryService]
    B -->|Clientes| E[CustomerSyncService]
    B -->|Proveedores| P[SupplierSyncService]
    B -->|Órdenes| F[OrderSyncService]
    
    C --> G[MeliService]
    D --> G
    E --> G
    P --> G
    F --> G
    
    G -->|GET /items/:id| H[MercadoLibre API]
    H --> I{Mapper Strategy}
    
    I -->|ProductMapper| J[Product Data Transform]
    I -->|BarCodeMapper| K[Barcode Data Transform]
    I -->|CustomerMapper| M[Customer Data Transform]
    I -->|SupplierMapper| N[Supplier Data Transform]
    I -->|InventoryMapper| L[Stock Data Transform]
    
    J --> O[InternalAPIService]
    K --> O
    L --> O
    M --> O
    N --> O
    
    O -->|POST/PUT| Q[WMS Adapter V2]
    Q --> R[SQL Server WMS]
    R --> S[Response Unificada]
    S --> T[Client]
```

---

### 3. 🎯 Características de Integración

#### 📦 Mapeo de Productos
- **ProductMapper**:
  - `productoean`: ID de MercadoLibre (identificador único estable)
  - `referencia`: EAN/SKU del producto
  - `descripcion`: Título optimizado + atributos relevantes
  - `preciounitario`: Precio sincronizado en tiempo real
  - `estado`: Activo/Inactivo basado en status ML
  - `ingredientes`: Concatenación de atributos (marca, modelo)
  - Soporte de imágenes y multimedia

- **BarCodeMapper**:
  - `idinternoean`: ID de MercadoLibre (preservado para búsquedas)
  - `codbarrasasignado`: EAN/SKU real del producto
  - `descripcion`: Descripción del código de barras
  - Manejo inteligente de múltiples códigos por producto

#### 👥 Mapeo de Clientes
- **CustomerMapper**:
  - `item`: ID de cliente MercadoLibre (⚠️ CAMPO CLAVE)
  - `nit`: Número de identificación fiscal
  - `nombrecliente`: Nombre completo o nickname
  - `direccion`: Dirección completa de envío
  - `telefono`: Código de área + número
  - `email`: Email de contacto
  - `codigopais`: Código ISO del país (CO, MX, AR, etc.)
  - `isactivocliente`: Estado activo/inactivo

#### 🏢 Mapeo de Proveedores
- **SupplierMapper**:
  - Mapeo completo de datos fiscales
  - Soporte multi-moneda (ARS, MXN, COP, BRL, CLP, USD)
  - Control de estados y condiciones comerciales
  - Gestión de múltiples sucursales
  - Integración con sistema de facturación
  - Campos de contacto y detalles fiscales

#### 📊 Gestión de Inventario
- **InventoryMapper**:
  - `bod`: Código de bodega (default "01", configurable)
  - `ubicacion`: Ubicación física en bodega
  - `saldopt`: Stock disponible en tiempo real
  - `cantbloqueadoerp`: Control de stock reservado
  - `saldowms`: Saldo sincronizado con WMS
  - `fechaactualiza`: Timestamp de última actualización
  - Control de estado ETL y transferencias entre bodegas
  - Trazabilidad completa de movimientos

#### 📋 Sistema de Órdenes
- **Sincronización Automática**:
  - Monitoreo en tiempo real de nuevas órdenes
  - Filtrado por estado (paid, confirmed, cancelled, etc.)
  - Procesamiento en lotes configurable
  - Control de concurrencia con ThreadPoolExecutor
  - Mapeo de ítems y cantidades

- **Gestión de Estados**:
  - Seguimiento de estados de pedidos
  - Actualización bidireccional de estados ML ↔ WMS
  - Notificaciones automáticas de cambios
  - Control de inventario reservado
  - Integración con sistema de envíos

---

### 4. 📡 Flujo de Sincronización Completo

```mermaid
flowchart TD
    A[Cliente solicita sync] --> B[Django View]
    B --> C{Método HTTP}
    C -->|GET| D[Sync masiva]
    C -->|POST| E[Sync específica por IDs]
    C -->|PUT| F[Update único]
    
    D --> G[Service Layer]
    E --> G
    F --> G
    
    G --> H[MeliService.get]
    H --> I[MercadoLibre API]
    I --> J[Validación de respuesta]
    J --> K{¿Datos válidos?}
    
    K -->|No| L[Error Handler]
    L --> M[Respuesta de error estructurada]
    
    K -->|Sí| N[Mapper.transform]
    N --> O[InternalAPIService.post/put]
    O --> P[WMS Adapter]
    P --> Q[SQL Server]
    Q --> R[Respuesta WMS]
    R --> S[Response Builder]
    S --> T[Respuesta unificada al cliente]
```


### 1. 🔐 Autenticación OAuth2

```mermaid
sequenceDiagram
    participant Client
    participant Django
    participant MongoDB
    participant MercadoLibre
    
    Client->>Django: POST /auth/refresh
    Django->>MongoDB: get_meli_config()
    MongoDB-->>Django: {client_id, client_secret, refresh_token}
    Django->>MercadoLibre: POST /oauth/token
    MercadoLibre-->>Django: {access_token, refresh_token}
    Django->>MongoDB: update_meli_tokens()
    Django-->>Client: {success: true, tokens}
```

### 2. � Sincronización y Mapeo de Datos

```mermaid
flowchart TD
    A[API Request] --> B{Tipo de Operación}
    B -->|Productos| C[ProductSync]
    B -->|Inventario| D[InventorySync]
    B -->|Clientes| E[CustomerSync]
    B -->|Órdenes| F[OrderSync]
    
    C --> G[MeliService]
    D --> G
    E --> G
    F --> G
    
    G --> H[Optimized Mappers]
    H -->|ProductMapper| I[Product Data]
    H -->|BarCodeMapper| J[Barcode Data]
    H -->|InventoryMapper| K[Stock Data]
    
    I --> L[InternalAPIService]
    J --> L
    K --> L
    L --> M[WMS API]
```

### 3. 🔍 Características Principales

#### Mapeo de Datos Optimizado
- **ProductMapper**:
  - `productoean`: ID de MercadoLibre (identificador estable)
  - `referencia`: EAN/SKU del producto
  - Descripción optimizada con título + detalles

- **BarCodeMapper**:
  - `idinternoean`: ID de MercadoLibre (preservado)
  - `codbarrasasignado`: EAN/SKU real del producto
  - Manejo inteligente de identificadores

#### Gestión de Inventario
- **InventoryMapper**:
  - `bod`: Código de bodega (default "01")
  - `ubicacion`: Ubicación en bodega
  - `saldopt`: Stock disponible en tiempo real
  - `cantbloqueadoerp`: Control de stock reservado
  - `saldowms`: Saldo en WMS
  - Seguimiento de fechas de actualización
  - Control de estado ETL y transferencias

#### Sistema de Órdenes
- **Sincronización Automática**:
  - Monitoreo en tiempo real de nuevas órdenes
  - Filtrado por estado (paid, confirmed, cancelled)
  - Procesamiento en lotes configurable
  - Control de concurrencia con ThreadPoolExecutor

- **Gestión de Estados**:
  - Seguimiento de estados de pedidos
  - Actualización bidireccional de estados
  - Notificaciones automáticas
  - Control de inventario reservado

#### Gestión de Proveedores
- **SupplierMapper**:
  - Mapeo completo de datos fiscales
  - Soporte multi-moneda (ARS, MXN, COP, BRL, CLP)
  - Control de estados y condiciones
  - Gestión de sucursales
  - Integración con facturación

```mermaid
flowchart TD
    A[Cliente solicita sync] --> B[MeliCustomerSyncView]
    B --> C{Método HTTP}
    C -->|POST| D[Sync clientes específicos]
    C -->|PUT| E[Update cliente único]
    
    D --> F[CustomerSyncService]
    E --> G[CustomerUpdateService]
    
    F --> H[MeliService get]
    G --> H
    H --> I[MercadoLibre API]
    I --> J[CustomerMapper]
    J --> K[InternalAPIService post/put]
    K --> L[WMS API]
    L --> M[Respuesta estructurada]
```


## 🗂️ Mapeo de Datos Detallado

### 📦 ProductMapper: MercadoLibre → WMS

#### Entrada: API MercadoLibre
```json
{
  "id": "MLM123456789",
  "title": "Samsung Galaxy S21 128GB Negro",
  "price": 15999.99,
  "available_quantity": 50,
  "condition": "new",
  "status": "active",
  "category_id": "MLM1234",
  "pictures": [
    {"url": "https://http2.mlstatic.com/..."}
  ],
  "attributes": [
    {"id": "BRAND", "value_name": "Samsung"},
    {"id": "MODEL", "value_name": "Galaxy S21"},
    {"id": "GTIN", "value_name": "8806090963339"}
  ],
  "shipping": {"free_shipping": true},
  "warranty": "12 meses de garantía de fábrica"
}
```

#### Salida: WMS COPERNICO
```json
{
  "productoean": "MLM123456789",
  "descripcion": "Samsung Galaxy S21 128GB Negro",
  "referencia": "MLM123456789",
  "inventariable": 1,
  "um1": "UND",
  "bodega": "DEFAULT",
  "factor": 1.0,
  "estado": 1,
  "preciounitario": 15999.99,
  "peso": 0.169,
  "descripcioningles": "Samsung Galaxy S21 128GB Black",
  "ingredientes": "Samsung Galaxy S21",
  "fecharegistro": "2025-10-16 14:30:00"
}
```

#### 🔄 Lógica de Mapeo
```python
# Ejemplo simplificado de la lógica
product_id = ml_product.get("id")  # MLM123456789
estado = 1 if ml_product.get("status") == "active" else 0
brand = extract_attribute(attributes, "BRAND")  # Samsung
model = extract_attribute(attributes, "MODEL")  # Galaxy S21
ingredientes = f"{brand} {model}".strip()  # Samsung Galaxy S21
```

---

### 👥 CustomerMapper: MercadoLibre → WMS

#### Entrada: API MercadoLibre (User Info)
```json
{
  "id": 2702572568,
  "nickname": "TESTUSER1096697426",
  "country_id": "CO",
  "first_name": "Juan Carlos",
  "last_name": "Pérez Rodríguez",
  "email": "juancarlos@email.com",
  "phone": {
    "area_code": "57",
    "number": "3001234567"
  },
  "address": {
    "address": "Calle 123 #45-67",
    "city": "Bogotá",
    "state": "CO-CUN",
    "zip_code": "110111"
  },
  "identification": {
    "type": "CC",
    "number": "1234567890"
  }
}
```

#### Salida: WMS COPERNICO
```json
{
  "item": "2702572568",
  "nit": "1234567890",
  "nombrecliente": "Juan Carlos Pérez Rodríguez",
  "direccion": "Calle 123 #45-67",
  "codigopais": "CO",
  "telefono": "573001234567",
  "cuidad": "Bogotá",
  "email": "juancarlos@email.com",
  "zip_code": "110111",
  "isactivocliente": 1,
  "fecharegistro": "2025-10-16 14:30:00"
}
```

#### ⚠️ Campo Crítico
- **`item`**: Este campo contiene el ID del cliente de MercadoLibre
- Es el identificador principal para búsquedas y actualizaciones
- Nunca usar el NIT como identificador principal

---

### 🏢 SupplierMapper: MercadoLibre → WMS

#### Soporte Multi-Moneda
```python
CURRENCY_MAP = {
    "ARS": "Peso Argentino",
    "MXN": "Peso Mexicano",
    "COP": "Peso Colombiano",
    "BRL": "Real Brasileño",
    "CLP": "Peso Chileno",
    "USD": "Dólar Americano"
}
```

#### Mapeo de Campos
```json
{
  "idproveedor": "<supplier_id>",
  "nit": "<tax_id>",
  "nombreproveedor": "<business_name>",
  "direccion": "<address>",
  "telefono": "<phone>",
  "email": "<email>",
  "codigopais": "<country_code>",
  "moneda": "<currency_code>",
  "estado": 1,
  "condicionpago": "30 días",
  "fecharegistro": "2025-10-16 14:30:00"
}
```

---

### 📊 InventoryMapper: Stock en Tiempo Real

#### Estructura de Datos
```json
{
  "productoean": "MLM123456789",
  "bod": "01",
  "ubicacion": "A-01-01",
  "saldopt": 50,
  "cantbloqueadoerp": 5,
  "saldowms": 45,
  "fechaactualiza": "2025-10-16 14:30:00",
  "estadoetl": "SYNC",
  "estadotrans": "OK"
}
```

#### Control de Stock
- **saldopt**: Stock físico total
- **cantbloqueadoerp**: Stock reservado para órdenes
- **saldowms**: Stock disponible real (saldopt - cantbloqueadoerp)
- **estadoetl**: Estado de sincronización
- **estadotrans**: Estado de transferencias




## 🛠️ Servicios Principales

### 🔗 MeliService - Cliente MercadoLibre API

Servicio centralizado para todas las interacciones con la API de MercadoLibre.

#### Características Principales
```python
class MeliService:
    """Cliente centralizado para MercadoLibre API."""
    
    BASE_URL = "https://api.mercadolibre.com"
    
    # Métodos HTTP
    def get(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response
    def post(self, endpoint: str, data: Dict) -> requests.Response
    def put(self, endpoint: str, data: Dict) -> requests.Response
    def delete(self, endpoint: str) -> requests.Response
    
    # Autenticación
    def _refresh_token_if_needed(self) -> None
    def _get_auth_headers(self) -> Dict[str, str]
```

#### ✨ Funcionalidades
- ✅ **Refresh Automático de Tokens**: Detecta expiraciones y renueva automáticamente
- ✅ **Retry con Backoff**: Reintentos automáticos con estrategia exponencial
- ✅ **Rate Limit Handling**: Manejo inteligente de límites de API
- ✅ **Session Management**: Pool de conexiones para mejor rendimiento
- ✅ **Logging Detallado**: Trazabilidad completa de requests/responses
- ✅ **Error Handling**: Excepciones personalizadas por tipo de error

#### Excepciones Personalizadas
```python
from mercadolibre.utils.exceptions import (
    MeliError,              # Error genérico de ML
    MeliAuthError,          # Error de autenticación (401)
    MeliNotFoundError,      # Recurso no encontrado (404)
    MeliBadRequestError,    # Request inválido (400)
    MeliRateLimitError,     # Límite de rate excedido (429)
    MeliServerError,        # Error del servidor ML (5xx)
)
```

#### Ejemplo de Uso
```python
from mercadolibre.services.meli_service import MeliService

# Inicializar servicio
meli = MeliService()

# GET - Obtener información de producto
response = meli.get(f"/items/{product_id}")
product_data = response.json()

# POST - Crear publicación
new_product = {
    "title": "Producto Nuevo",
    "category_id": "MLM1234",
    "price": 299.99,
    # ...
}
response = meli.post("/items", data=new_product)

# PUT - Actualizar producto
updates = {"available_quantity": 100}
response = meli.put(f"/items/{product_id}", data=updates)
```

---

### 🏢 InternalAPIService - Cliente WMS API

Servicio para comunicación con las APIs internas del WMS (Adapter V2).

#### Características Principales
```python
class InternalAPIService:
    """Cliente para APIs internas del WMS."""
    
    def __init__(self, base_url: Optional[str] = None)
    
    # Métodos HTTP
    def get(self, endpoint: str, original_request=None) -> requests.Response
    def post(self, endpoint: str, json: Dict, original_request=None) -> requests.Response
    def put(self, endpoint: str, json: Dict, original_request=None) -> requests.Response
    def delete(self, endpoint: str, original_request=None) -> requests.Response
```

#### ✨ Funcionalidades
- ✅ **Propagación de Headers**: Copia automática de headers de autenticación
- ✅ **Base URL Configurable**: Fácil cambio entre ambientes
- ✅ **Timeout Configurable**: Control de timeouts por request
- ✅ **Connection Pooling**: Reutilización de conexiones
- ✅ **Error Handling**: Manejo robusto de errores de red
- ✅ **Logging**: Registro detallado de operaciones

#### Configuración
```python
# En settings.py
WMS_BASE_URL = "http://localhost:8000"  # URL base del WMS
WMS_TIMEOUT = 30  # Timeout en segundos
```

#### Ejemplo de Uso
```python
from mercadolibre.services.internal_api_service import InternalAPIService

# Inicializar servicio
wms_api = InternalAPIService()

# POST - Crear producto en WMS
product_data = {
    "productoean": "MLM123456789",
    "descripcion": "Producto Test",
    # ...
}
response = wms_api.post("/wms/adapter/v2/art", json=product_data)

# PUT - Actualizar cliente en WMS
customer_data = {
    "item": "2702572568",
    "nombrecliente": "Juan Pérez",
    # ...
}
response = wms_api.put("/wms/adapter/v2/clt", json=customer_data)

# GET - Consultar inventario
response = wms_api.get("/wms/adapter/v2/inventory")
inventory = response.json()
```

---

### 🗄️ MeliConfigRepository - Gestión de Configuración

Repository para operaciones CRUD de configuración en MongoDB.

#### Características
```python
class MeliConfigRepository:
    """Repository para configuración de MercadoLibre."""
    
    COLLECTION_NAME = "meli_test"
    CONFIG_FIELD = "meli_config"
    
    # Métodos principales
    def get_config(self) -> Optional[MeliConfig]
    def get_tokens(self) -> Optional[Dict[str, str]]
    def get_credentials(self) -> Optional[Dict[str, str]]
    def update_tokens(self, access_token: str, refresh_token: str) -> bool
    def update_config(self, config_data: Dict[str, Any]) -> bool
```

#### Estructura en MongoDB
```json
{
  "_id": ObjectId("..."),
  "meli_config": {
    "user_account_id": "123456789",
    "access_token": "APP_USR-...",
    "refresh_token": "TG-...",
    "client_id": "1234567890123456",
    "client_secret": "ABCdefGHIjklMNOpqrSTUvwx",
    "redirect_uri": "https://example.com/callback"
  }
}
```

#### Ejemplo de Uso
```python
from project.config_db.repository import MeliConfigRepository

repo = MeliConfigRepository()

# Obtener configuración completa
config = repo.get_config()
print(f"User ID: {config.user_account_id}")

# Obtener solo tokens
tokens = repo.get_tokens()
access_token = tokens['access_token']
refresh_token = tokens['refresh_token']

# Actualizar tokens
repo.update_tokens(
    access_token="APP_USR-new-token",
    refresh_token="TG-new-refresh"
)
```




## 📍 Endpoints API

La aplicación expone tres grupos principales de endpoints:

### 🌐 Rutas Base

| Prefijo | Módulo | Descripción |
|---------|--------|-------------|
| `/wms/ml/v1/` | mercadolibre | Integración MercadoLibre |
| `/wms/adapter/v2/` | wmsAdapterV2 | Adaptador WMS COPERNICO |
| `/wms/base/v2/` | wmsBase | Funcionalidades base WMS |

---

### 🔐 Autenticación

#### Refresh de Tokens
```http
POST /wms/ml/v1/auth/
```

**Descripción**: Refresca los tokens de acceso de MercadoLibre usando el refresh_token almacenado en MongoDB.

**Request**: No requiere body

**Response Exitosa** (200 OK):
```json
{
  "success": true,
  "message": "Tokens refreshed successfully",
  "access_token": "APP_USR-1234567890-123456-abc...",
  "refresh_token": "TG-xyz...",
  "expires_in": 21600,
  "token_type": "Bearer",
  "scope": "offline_access read write"
}
```

**Response Error** (400/500):
```json
{
  "success": false,
  "error": "Error refreshing MercadoLibre tokens",
  "details": "Invalid refresh token"
}
```

---

### 📦 Productos

#### Sincronización Masiva
```http
GET /wms/ml/v1/product/
```
**Descripción**: Sincroniza todos los productos activos de MercadoLibre.

**Query Parameters**:
- `limit` (opcional): Número máximo de productos a sincronizar
- `offset` (opcional): Desplazamiento para paginación

**Response**:
```json
{
  "overall_success": true,
  "summary": "Synchronized 50 products successfully",
  "total_products": 50,
  "successful": 48,
  "failed": 2,
  "products": [...]
}
```

---

#### Sincronización Específica
```http
POST /wms/ml/v1/product/
Content-Type: application/json
```

**Request Body**:
```json
{
  "product_ids": ["MLM123456789", "MLM987654321"],
  "force_update": false
}
```

**Parámetros**:
- `product_ids` (requerido): Array de IDs de productos de MercadoLibre
- `force_update` (opcional): Si `true`, actualiza incluso si no hay cambios

**Response** (200 OK):
```json
{
  "overall_success": true,
  "overall_status": "partial_success",
  "summary": "2 products processed: 1 success, 1 failed",
  "results": [
    {
      "product_id": "MLM123456789",
      "success": true,
      "status": "updated",
      "message": "Product synchronized successfully"
    },
    {
      "product_id": "MLM987654321",
      "success": false,
      "status": "error",
      "error": "Product not found in MercadoLibre"
    }
  ]
}
```

---

#### Actualización Individual
```http
PUT /wms/ml/v1/product/
Content-Type: application/json
```

**Request Body**:
```json
{
  "product_id": "MLM123456789"
}
```

**Response** (200 OK):
```json
{
  "overall_success": true,
  "overall_status": "complete_success",
  "summary": "Product updated successfully",
  "product_id": "MLM123456789",
  "product_operation": {
    "success": true,
    "status": "updated",
    "message": "Product data synchronized",
    "details": {
      "wms_response": {
        "status": "updated",
        "productoean": "MLM123456789"
      }
    }
  },
  "changes_summary": {
    "product_changed": true,
    "price_changed": false,
    "stock_changed": true
  },
  "ml_data": {...},
  "updated_at": "2025-10-16T14:30:00.123456"
}
```

---

### 👥 Clientes

#### Sincronización Específica
```http
POST /wms/ml/v1/customer/
Content-Type: application/json
```

**Request Body**:
```json
{
  "customer_ids": ["2702572568", "1234567890"],
  "force_update": false
}
```

**Response**:
```json
{
  "overall_success": true,
  "summary": "2 customers synchronized",
  "results": [
    {
      "customer_id": "2702572568",
      "success": true,
      "message": "Customer created successfully"
    },
    {
      "customer_id": "1234567890",
      "success": true,
      "message": "Customer updated successfully"
    }
  ]
}
```

---

#### Actualización Individual
```http
PUT /wms/ml/v1/customer/
Content-Type: application/json
```

**Request Body**:
```json
{
  "customer_id": "2702572568"
}
```

**Response**:
```json
{
  "success": true,
  "customer_id": "2702572568",
  "status": "updated",
  "message": "Customer data synchronized successfully",
  "wms_response": {...}
}
```

---

### 🏢 Proveedores

#### Sincronización
```http
POST /wms/ml/v1/supplier/
Content-Type: application/json
```

**Request Body**:
```json
{
  "supplier_ids": ["SUPP001", "SUPP002"]
}
```

**Response**:
```json
{
  "success": true,
  "summary": "2 suppliers synchronized",
  "results": [...]
}
```

---

### 📊 Inventario

#### Crear/Actualizar Inventario
```http
POST /wms/ml/v1/inventory/
Content-Type: application/json
```

**Request Body**:
```json
{
  "product_id": "MLM123456789",
  "warehouse_code": "01",
  "location": "A-01-01",
  "quantity": 100
}
```

**Response**:
```json
{
  "success": true,
  "message": "Inventory updated successfully",
  "product_id": "MLM123456789",
  "warehouse": "01",
  "available_stock": 100,
  "reserved_stock": 5,
  "total_stock": 105
}
```

---

#### Consultar Inventario
```http
GET /wms/ml/v1/inventory/?product_id=MLM123456789
```

**Response**:
```json
{
  "product_id": "MLM123456789",
  "warehouses": [
    {
      "warehouse_code": "01",
      "location": "A-01-01",
      "available": 100,
      "reserved": 5,
      "total": 105
    }
  ]
}
```

---

### 📋 Órdenes

#### Sincronización de Órdenes
```http
POST /wms/ml/v1/order/
Content-Type: application/json
```

**Request Body**:
```json
{
  "order_ids": ["12345678901", "98765432109"],
  "status_filter": "paid"
}
```

**Parámetros**:
- `order_ids` (opcional): IDs específicos de órdenes
- `status_filter` (opcional): Filtrar por estado (paid, confirmed, cancelled)

**Response**:
```json
{
  "success": true,
  "summary": "2 orders synchronized",
  "results": [
    {
      "order_id": "12345678901",
      "status": "created",
      "items": 3,
      "total": 1599.99
    },
    {
      "order_id": "98765432109",
      "status": "updated",
      "items": 1,
      "total": 299.99
    }
  ]
}
```

---

### 🔧 Adaptador WMS V2

Endpoints para interactuar directamente con el WMS COPERNICO:

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/wms/adapter/v2/art` | GET, POST, PUT | Gestión de artículos |
| `/wms/adapter/v2/clt` | GET, POST, PUT | Gestión de clientes |
| `/wms/adapter/v2/prv` | GET, POST, PUT | Gestión de proveedores |
| `/wms/adapter/v2/inventory` | GET, POST, PUT | Gestión de inventario |
| `/wms/adapter/v2/sale_order` | POST | Órdenes de venta |
| `/wms/adapter/v2/purchase_order` | POST | Órdenes de compra |
| `/wms/adapter/v2/production_order` | POST | Órdenes de producción |
| `/wms/adapter/v2/inventory_adjustment` | POST | Ajustes de inventario |




## 📊 Formato de Respuestas Unificado

Todas las operaciones del sistema devuelven respuestas en formato estructurado consistente.

### ✅ Respuesta de Éxito Completo

```json
{
  "overall_success": true,
  "overall_status": "complete_success",
  "summary": "Product updated successfully",
  "product_id": "MLM123456789",
  "product_operation": {
    "success": true,
    "status": "updated",
    "message": "Product synchronized successfully",
    "details": {
      "wms_response": {
        "status": 200,
        "productoean": "MLM123456789",
        "descripcion": "Samsung Galaxy S21"
      }
    }
  },
  "changes_summary": {
    "product_changed": true,
    "price_changed": false,
    "stock_changed": true,
    "synchronized": true
  },
  "ml_data": {
    "id": "MLM123456789",
    "title": "Samsung Galaxy S21",
    "price": 15999.99,
    "available_quantity": 50
  },
  "updated_at": "2025-10-16T14:30:00.123456"
}
```

---

### ⚠️ Respuesta de Éxito Parcial

```json
{
  "overall_success": true,
  "overall_status": "partial_success",
  "summary": "3 products processed: 2 success, 1 failed",
  "total_processed": 3,
  "successful": 2,
  "failed": 1,
  "results": [
    {
      "product_id": "MLM123",
      "success": true,
      "status": "updated",
      "message": "Product synchronized"
    },
    {
      "product_id": "MLM456",
      "success": true,
      "status": "created",
      "message": "New product created"
    },
    {
      "product_id": "MLM789",
      "success": false,
      "status": "error",
      "error": "Product not found in MercadoLibre"
    }
  ],
  "updated_at": "2025-10-16T14:30:00.123456"
}
```

---

### ❌ Respuesta de Error

```json
{
  "overall_success": false,
  "overall_status": "complete_failure",
  "summary": "Product operation failed: Not found in MercadoLibre",
  "product_id": "MLM123456789",
  "error_type": "MeliNotFoundError",
  "error_details": "HTTP 404: Item MLM123456789 not found",
  "timestamp": "2025-10-16T14:30:00.123456"
}
```

---

### 🔑 Campos de Respuesta

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `overall_success` | boolean | Estado general de la operación |
| `overall_status` | string | Estado detallado: `complete_success`, `partial_success`, `complete_failure` |
| `summary` | string | Resumen legible de la operación |
| `results` | array | Array de resultados individuales (en operaciones múltiples) |
| `changes_summary` | object | Resumen de cambios realizados |
| `updated_at` | string | Timestamp ISO 8601 de la operación |
| `error_type` | string | Tipo de error (solo en errores) |
| `error_details` | string | Detalles del error (solo en errores) |




## ⚙️ Configuración e Instalación

### � Requisitos Previos

- **Python**: 3.13 o superior
- **MongoDB**: 4.x o superior (para configuración)
- **SQL Server**: Para base de datos WMS
- **Git**: Para clonar el repositorio

---

### 🚀 Instalación Paso a Paso

#### 1. Clonar el Repositorio
```powershell
git clone https://github.com/JonathanArroyaveGonzalez/Integration-Proyect-SGV.git
cd Integration-Proyect-SGV
```

#### 2. Crear Entorno Virtual
```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Si hay error de ejecución de scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 3. Instalar Dependencias
```powershell
pip install -r requirements.txt
```

**Dependencias principales**:
- Django 5.2.5
- pymongo 4.14.1
- requests 2.32.5
- django-cors-headers 4.7.0
- python-dotenv 1.1.1
- mssql-django 1.6
- pyodbc 5.2.0

#### 4. Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Django
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# MongoDB (Configuración)
DATABASE_URL=mongodb://localhost:27017
APIDBMONGO=integration_db

# SQL Server (WMS)
DB_HOST=your-sql-server-host
DB_PORT=1433
DB_NAME=WMS_COPERNICO
DB_USER=your-db-user
DB_PASSWORD=your-db-password

# WMS API
WMS_BASE_URL=http://localhost:8000
WMS_TIMEOUT=30

# MercadoLibre (se configura en MongoDB)
# Estos valores se obtienen desde el dashboard de ML
MELI_CLIENT_ID=your-meli-client-id
MELI_CLIENT_SECRET=your-meli-client-secret
```

#### 5. Configurar MongoDB

Insertar configuración inicial de MercadoLibre en MongoDB:

```javascript
// En MongoDB shell o Compass
use integration_db;

db.meli_test.insertOne({
  "meli_config": {
    "user_account_id": "123456789",
    "access_token": "APP_USR-your-access-token",
    "refresh_token": "TG-your-refresh-token",
    "client_id": "your-client-id",
    "client_secret": "your-client-secret",
    "redirect_uri": "https://your-domain.com/callback"
  }
});
```


#### Configuración de Logging

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/integration.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'mercadolibre': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'wmsAdapterV2': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

#### Configuración de Base de Datos SQL Server

En `project/settings.py`:

```python
DATABASES = {
    'wms': {
        'ENGINE': 'mssql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '1433'),
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'unicode_results': True,
        },
    }
}
```

---

### 🌐 Ambientes

#### Desarrollo
```env
DEBUG=True
WMS_BASE_URL=http://localhost:8000
DATABASE_URL=mongodb://localhost:27017
```

#### Producción
```env
DEBUG=False
ALLOWED_HOSTS=your-production-domain.com
WMS_BASE_URL=https://wms-api.your-domain.com
DATABASE_URL=mongodb://user:password@mongodb-host:27017/production_db
SECRET_KEY=use-a-strong-random-secret-key
```




### 🛠️ Tests Manuales de Endpoints

#### 1. Test de Autenticación
```powershell
# PowerShell
$response = Invoke-RestMethod -Uri "http://localhost:8000/wms/ml/v1/auth/" -Method POST
$response | ConvertTo-Json -Depth 10
```

```bash
# cURL (Git Bash o WSL)
curl -X POST http://localhost:8000/wms/ml/v1/auth/
```

**Respuesta esperada**:
```json
{
  "success": true,
  "message": "Tokens refreshed successfully",
  "access_token": "APP_USR-...",
  "expires_in": 21600
}
```

---

#### 2. Test de Sincronización de Producto
```powershell
# PowerShell
$body = @{
    product_id = "MLM123456789"
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Uri "http://localhost:8000/wms/ml/v1/product/" `
    -Method PUT `
    -ContentType "application/json" `
    -Body $body

$response | ConvertTo-Json -Depth 10
```

```bash
# cURL
curl -X PUT http://localhost:8000/wms/ml/v1/product/ \
  -H "Content-Type: application/json" \
  -d '{"product_id": "MLM123456789"}'
```

---

#### 3. Test de Sincronización de Cliente
```powershell
# PowerShell
$body = @{
    customer_id = "2702572568"
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Uri "http://localhost:8000/wms/ml/v1/customer/" `
    -Method PUT `
    -ContentType "application/json" `
    -Body $body

$response | ConvertTo-Json -Depth 10
```

---

#### 4. Test de Múltiples Productos
```powershell
# PowerShell
$body = @{
    product_ids = @("MLM123", "MLM456", "MLM789")
    force_update = $false
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Uri "http://localhost:8000/wms/ml/v1/product/" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body

$response | ConvertTo-Json -Depth 10
```


### ✅ Validación de Configuración

#### Verificar MongoDB
```powershell
# PowerShell
python -c "from project.config_db.repository import MeliConfigRepository; repo = MeliConfigRepository(); config = repo.get_config(); print(f'Config OK: {config is not None}')"
```

#### Verificar Conexión WMS
```powershell
python -c "from mercadolibre.services.internal_api_service import InternalAPIService; service = InternalAPIService(); print('WMS Service initialized successfully')"
```

#### Verificar MercadoLibre API
```powershell
python -c "from mercadolibre.services.meli_service import MeliService; service = MeliService(); print('MeliService initialized successfully')"
```

---

### 🐛 Debugging

#### Modo Debug Detallado
En `settings.py`:
```python
DEBUG = True

LOGGING = {
    'loggers': {
        'mercadolibre': {
            'level': 'DEBUG',  # Mostrar todos los logs
        },
    }
}
```

#### Ver Logs en Tiempo Real
```powershell
# PowerShell
Get-Content logs/integration.log -Wait -Tail 50
```

```bash
# Git Bash / WSL
tail -f logs/integration.log
```




## 🐛 Troubleshooting

### Problemas Comunes y Soluciones

#### ❌ Error: "Error refreshing MercadoLibre tokens: 'grant_type'"

**Causa**: Configuración incompleta en MongoDB

**Solución**:
```powershell
# Verificar configuración en MongoDB
python -c "from project.config_db.repository import MeliConfigRepository; repo = MeliConfigRepository(); config = repo.get_config(); print(config)"
```

Asegurarse de que todos los campos estén presentes:
- `client_id`
- `client_secret`
- `refresh_token`

---

#### ❌ Error: "Customer ID is required for WMS update"

**Causa**: El ID del cliente no se está mapeando correctamente al campo `item`

**Solución**:
- Verificar que el mapper use el campo `item` (no `nit`) como identificador principal
- El campo `item` debe contener el ID de MercadoLibre

```python
# Correcto
customer_data = {
    "item": "2702572568",  # ID de ML
    "nit": "1234567890",   # Identificación fiscal
    # ...
}
```

---

#### ❌ Error: "Connection error while updating product"

**Causa**: El servicio WMS no está accesible

**Solución**:
1. Verificar que `WMS_BASE_URL` esté configurado correctamente
2. Verificar que el servicio WMS esté ejecutándose
3. Verificar conectividad de red

```powershell
# Verificar URL configurada
python -c "from django.conf import settings; print(f'WMS URL: {settings.WMS_BASE_URL}')"

# Test de conectividad
Test-NetConnection -ComputerName localhost -Port 8000
```

---

#### ❌ Error: "401 Unauthorized" en MercadoLibre

**Causa**: Token de acceso expirado o inválido

**Solución**:
```powershell
# Forzar refresh de tokens
Invoke-RestMethod -Uri "http://localhost:8000/wms/ml/v1/auth/" -Method POST
```

Si persiste, verificar que el `refresh_token` en MongoDB sea válido.

---

#### ❌ Error: "404 Not Found" para producto/cliente

**Causa**: El ID proporcionado no existe en MercadoLibre

**Solución**:
- Verificar que el ID sea correcto (formato: MLM123456789)
- Verificar que el producto/cliente exista en tu cuenta de ML
- Verificar que tengas permisos para acceder al recurso

---

#### ❌ Error: "Rate limit exceeded (429)"

**Causa**: Se excedió el límite de requests a la API de MercadoLibre

**Solución**:
- El sistema reintenta automáticamente después de un delay
- Reducir la frecuencia de requests
- Implementar throttling en cliente

```python
# El decorador @retry_on_rate_limit maneja esto automáticamente
@retry_on_rate_limit(max_retries=3, delay=5)
def sync_products():
    # ...
```

---

#### ❌ Error: "ModuleNotFoundError" al ejecutar

**Causa**: Dependencias no instaladas o entorno virtual no activado

**Solución**:
```powershell
# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Reinstalar dependencias
pip install -r requirements.txt
```

---

#### ❌ Error: "ODBC Driver not found" (SQL Server)

**Causa**: Driver ODBC de SQL Server no instalado

**Solución**:
1. Descargar [ODBC Driver 17 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
2. Instalar el driver
3. Reiniciar el servidor Django

---

#### ❌ Error: "Cannot connect to MongoDB"

**Causa**: MongoDB no está ejecutándose o URL incorrecta

**Solución**:
```powershell
# Verificar si MongoDB está corriendo
Get-Process mongod

# Iniciar MongoDB (si está instalado localmente)
mongod --dbpath "C:\data\db"

# Verificar URL en .env
echo $env:DATABASE_URL
```

---

### 📝 Logs y Debugging

#### Ubicación de Logs
- **Logs de aplicación**: `logs/integration.log`
- **Logs de Django**: Console output
- **Logs de MeliService**: `logs/meli_service.log`

#### Habilitar Logging Detallado
```python
# En settings.py
LOGGING = {
    'loggers': {
        'mercadolibre': {
            'level': 'DEBUG',  # Cambiar de INFO a DEBUG
        },
    }
}
```

#### Ver Logs en Tiempo Real
```powershell
# PowerShell
Get-Content logs/integration.log -Wait -Tail 50
```

---

### 🔍 Validación de Datos

#### Verificar Mapeo de Productos
```python
from mercadolibre.utils.mapper.data_mapper import ProductMapper

# Ejemplo de datos de ML
ml_data = {
    "id": "MLM123456789",
    "title": "Producto Test",
    "price": 299.99,
    # ...
}

# Probar mapeo
mapper = ProductMapper.from_meli_product(ml_data)
print(mapper.__dict__)
```

#### Verificar Respuesta de WMS
```python
from mercadolibre.services.internal_api_service import InternalAPIService

service = InternalAPIService()
response = service.get("/wms/adapter/v2/art")
print(response.status_code)
print(response.json())
```

---



## 📈 Arquitectura y Mejores Prácticas

### 🎯 Patrones de Diseño Implementados

#### 1. Repository Pattern
Abstracción de acceso a datos en MongoDB:
```python
class MeliConfigRepository:
    """Centraliza todas las operaciones de configuración"""
    def get_config() -> MeliConfig
    def update_tokens() -> bool
```

#### 2. Service Layer
Lógica de negocio centralizada:
```python
class MeliService:
    """Encapsula toda la comunicación con MercadoLibre"""
    
class InternalAPIService:
    """Encapsula toda la comunicación con WMS"""
```

#### 3. Mapper Pattern
Transformación de datos entre sistemas:
```python
class ProductMapper:
    """Transforma datos ML → WMS"""
    @classmethod
    def from_meli_product(ml_product) -> ProductMapper
```

---









