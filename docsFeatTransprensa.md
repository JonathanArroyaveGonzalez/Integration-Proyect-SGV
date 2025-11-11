# Documentación del Proyecto Transprensa - WMS Copernico Integration

## 📋 Tabla de Contenidos
1. [Descripción General](#descripción-general)
2. [Flujo de Procesamiento de Guías](#flujo-de-procesamiento-de-guías)
3. [Componentes Principales](#componentes-principales)
4. [API Endpoints](#api-endpoints)
5. [Diagramas de Flujo](#diagramas-de-flujo)
6. [Mapeo de Datos](#mapeo-de-datos)

---

## 🎯 Descripción General

El proyecto **Transprensa** es un módulo de integración que facilita el procesamiento automatizado de guías de envío desde el sistema WMS Copérnico hacia el servicio de Transprensa. El sistema procesa guías, las mapea a remesas, las crea en Transprensa y maneja la descarga de PDFs de forma asíncrona.

### 🎨 Características Principales
- ✅ Procesamiento completo de guías en una sola solicitud
- ✅ Mapeo automático de datos WMS a formato Transprensa
- ✅ Validación de ciudades con códigos DANE
- ✅ Descarga asíncrona de PDFs
- ✅ Manejo de errores robusto
- ✅ Cache inteligente para consultas de ciudades

---

## 🔄 Flujo de Procesamiento de Guías

### Flujo Principal (Síncrono)

```mermaid
sequenceDiagram
    participant C as Cliente
    participant V as RemesaView
    participant E as Executor
    participant CS as ClientService
    participant IS as InternalService
    participant M as Mapper
    participant TP as Transprensa API
    participant T as Thread Pool
    
    C->>V: POST /wms/tp/v1/guide/
    Note over C,V: {picking, bigpedido}
    
    V->>E: execute_guide_workflow()
    
    E->>CS: get_guide_data()
    CS->>IS: getGuiaData()
    IS->>IS: read_data_guide (sin detalle)
    IS->>IS: read_data_guide (con detalle)
    IS-->>CS: Datos combinados
    CS-->>E: Guía completa
    
    E->>M: mapear_guia_a_remesa()
    M->>M: Validar y mapear datos
    M->>CS: get_ciudad_codigo_by_nombre()
    CS->>TP: Consultar código DANE
    TP-->>CS: Código ciudad
    CS-->>M: Código DANE
    M-->>E: Remesa mapeada
    
    E->>M: crear_payload_api()
    M-->>E: Payload estructurado
    
    E->>CS: create_remesas()
    CS->>TP: servicio.Remesa.crear
    TP-->>CS: Respuesta creación
    CS-->>E: Número de remesa
    
    E->>CS: print_remesas()
    CS->>TP: servicio.Remesa.impresionRemesa
    TP-->>CS: URL del PDF
    CS-->>E: URL PDF
    
    E->>T: Iniciar descarga PDF (async)
    T->>T: download_pdf_from_url()
    T->>IS: save_guide_pdf()
    
    E-->>V: Resultado completo
    V-->>C: JSON Response
    
    Note over T: Proceso en background
    T->>T: Descargar PDF
    T->>IS: Guardar en BD
```

---

## 🧩 Componentes Principales

### 1. **RemesaView** (`transprensa/views/remesaView.py`)
- **Responsabilidad**: Endpoint HTTP para procesar guías
- **Endpoint**: `POST /wms/tp/v1/guide/`
- **Parámetros**: `picking`, `bigpedido`
- **Respuesta**: JSON con estado del procesamiento

### 2. **Execute Guide Workflow** (`transprensa/functions/create.py`)
- **Responsabilidad**: Orquestador principal del flujo
- **Funciones Clave**:
  - `execute_guide_workflow()`: Flujo principal
  - `download_pdf_from_url()`: Descarga PDFs
  - `_process_pdf_background()`: Procesamiento asíncrono

### 3. **Remesa Mapper** (`transprensa/functions/remesaMapper.py`)
- **Responsabilidad**: Transformación de datos WMS → Transprensa
- **Componentes**:
  - DataClasses para estructuras de datos
  - Funciones de mapeo y validación
  - Generación of payloads para API

### 4. **Client Service** (`transprensa/services/clientService.py`)
- **Responsabilidad**: Abstracción de servicios externos
- **Funciones**:
  - Consultas a WMS interno
  - Comunicación con Transprensa API
  - Cache de consultas de ciudades

### 5. **Transprensa Service** (`transprensa/services/transprensaService.py`)
- **Responsabilidad**: Cliente HTTP para Transprensa API
- **Características**:
  - Autenticación automática
  - Renovación de tokens
  - Reintentos automáticos

---

## 📡 API Endpoints

### Procesar Guía
```http
POST /wms/tp/v1/guide/
Content-Type: application/json

{
    "picking": "7746",
    "bigpedido": "PD-103888"
}
```

#### Respuesta Exitosa (200)
```json
{
    "success": true,
    "picking": "7746",
    "bigpedido": "PD-103888",
    "remesa_numero": "RM-123456",
    "msg": "Guía procesada exitosamente. PDF en procesamiento",
    "tiempo_ms": 2341,
    "pdf_en_background": true
}
```

#### Respuesta con Error (400/500)
```json
{
    "success": false,
    "picking": "7746",
    "bigpedido": "PD-103888",
    "remesa_numero": "",
    "mensaje": "La ciudad de origen y destino no pueden ser iguales",
    "tiempo_ms": 1205,
    "pdf_en_background": false
}
```

---

## 📊 Diagramas de Flujo

### Flujo de Validación y Mapeo

```mermaid
flowchart TD
    A[Inicio: Datos de Guía] --> B{¿Datos válidos?}
    B -->|No| C[Error: Datos faltantes]
    B -->|Sí| D[Obtener datos WMS]
    
    D --> E{¿Datos obtenidos?}
    E -->|No| F[Error: Sin datos de guía]
    E -->|Sí| G[Mapear destinatario]
    
    G --> H[Consultar código DANE ciudad]
    H --> I[Crear estructura remesa]
    I --> J[Validar ciudades origen/destino]
    
    J --> K{¿Ciudades diferentes?}
    K -->|No| L[Error: Ciudades iguales]
    K -->|Sí| M[Crear payload API]
    
    M --> N[Enviar a Transprensa]
    N --> O{¿Creación exitosa?}
    O -->|No| P[Error: Fallo en creación]
    O -->|Sí| Q[Solicitar PDF]
    
    Q --> R{¿PDF disponible?}
    R -->|No| S[Éxito sin PDF]
    R -->|Sí| T[Iniciar descarga async]
    T --> U[Éxito completo]
    
    style A fill:#e1f5fe
    style C fill:#ffebee
    style F fill:#ffebee
    style L fill:#ffebee
    style P fill:#ffebee
    style S fill:#fff3e0
    style U fill:#e8f5e8
```

### Flujo de Autenticación Transprensa

```mermaid
stateDiagram-v2
    [*] --> LoadConfig: Inicializar servicio
    LoadConfig --> HasToken: Cargar configuración
    
    HasToken --> MakeRequest: Token disponible
    MakeRequest --> CheckResponse: Enviar petición
    
    CheckResponse --> Success: Respuesta OK
    CheckResponse --> TokenExpired: Error 401/Token
    CheckResponse --> NetworkError: Error de red
    
    TokenExpired --> RefreshToken: Renovar token
    RefreshToken --> UpdateConfig: Login exitoso
    RefreshToken --> LoginFailed: Error de login
    
    UpdateConfig --> MakeRequest: Token actualizado
    NetworkError --> Retry: Reintentar
    Retry --> MakeRequest: Después de delay
    
    Success --> [*]
    LoginFailed --> [*]
    
    note right of RefreshToken
        Usa credenciales de MongoDB
        para obtener nuevo token
    end note
```

---

## 🗂️ Mapeo de Datos

### Estructura de Datos WMS → Remesa Transprensa

```mermaid
classDiagram
    class GuiaWMS {
        +string nit_destinatario
        +string nombre_destinatario
        +string direccion_destinatario
        +string telefono_destinatario
        +string ciudad_destinatario
        +string valor_declarado
        +string referencia
        +string observaciones
    }
    
    class DetalleWMS {
        +string peso_real
        +string volumen
        +string unidades
        +string descripcion
    }
    
    class RemesaTransprensa {
        +Cliente cliente
        +Remitente remitente
        +Destinatario destinatario
        +Detalle detalle
        +string ciudad_codigo_origen
        +string ciudad_codigo_destino
        +string tipo_servicio
        +string forma_pago
    }
    
    class Destinatario {
        +string destinatario_documento
        +string destinatario_nombre
        +string destinatario_direccion
        +string destinatario_telefono
        +string destinatario_ciudad_codigo
    }
    
    class Detalle {
        +string detalle_peso
        +string detalle_volumen
        +string detalle_cantidad
        +string detalle_descripcion
        +string detalle_valordeclarado
    }
    
    GuiaWMS --|> RemesaTransprensa : mapear_guia_a_remesa()
    DetalleWMS --|> Detalle : transform
    RemesaTransprensa --> Destinatario
    RemesaTransprensa --> Detalle
```
