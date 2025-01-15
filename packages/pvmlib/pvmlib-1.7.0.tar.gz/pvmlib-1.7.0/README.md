# pvmlib

Una librería personalizada para manejo de logging, validación de tokens, manejo de excepciones y consumo de servicios REST.

## Instalación

Para instalar la librería, usa pip:

```bash
pip install pvmlib
```

## Implementación

### Logger

```python
from pvmlib import logger_singleton, default_logger, application, measurement
from datetime import datetime

# Crear instancias de Application y Measurement
app_info = application(
    name="bs-customer",
    version="1.3.7",
    env="PROD",
    kind="rest-service"
)

measure = measurement(
    method="getClientInfo",
    elapsedTime=50
)

# Crear una entrada de log
log_entry = default_logger(
    level="INFO",
    schemaVersion="1.0.0",
    logType="TRANSACTION",
    sourceIP="10.1.130.25",
    status="SUCCESS",
    message="Obtener info del cliente",
    logOrigin="INTERNAL",
    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
    tracingId="48ad2b64a76dc6ab66da565b6298e0e6fad5b7796a8a35aa6b",
    hostname="server-1",
    eventType="TRANSACTION_PAYMENT_PROCESSING_FAILED",
    application=app_info,
    measurement=measure,
    destinationIP="10.10.129.200",
    additionalInfo={"clientID": 123}
)

# Obtener el logger y registrar la entrada de log
logger = logger_singleton().get_logger()
logger.info(log_entry.json())
```

### Interceptor

```python
from fastapi import FastAPI
from pvmlib import intercept_middleware, application

app = FastAPI()

app_info = application(
    name="bs-customer",
    version="1.3.7",
    env="PROD",
    kind="rest-service"
)

auth_service_url = "https://auth-service-url.com"

app.add_middleware(intercept_middleware, app_info=app_info, auth_service_url=auth_service_url)
```

### RestClient

```python
from pvmlib import call_service_network

base_url = "https://api.example.com"
client = call_service_network(base_url)

# Realizar una solicitud GET
response = client.get("/endpoint", params={"key": "value"}, headers={"Authorization": "Bearer token"})
print(response)

# Realizar una solicitud POST
response = client.post("/endpoint", json={"key": "value"}, headers={"Authorization": "Bearer token"})
print(response)
```

### Manejo de Excepciones

```python
from pvmlib import response_exception

try:
    # Código que puede lanzar una excepción
    raise response_exception(
        error_code="CUSTOM_ERROR",
        message="Ocurrió un error personalizado",
        http_status_code=400,
        headers={"X-Custom-Header": "value"}
    )
except response_exception as e:
    print(e.to_dict())
```

### Respuesta Exitosa

```python
from pvmlib import response_ok

response = response_ok(
    status_code=200,
    message="Operación exitosa",
    transaction_id="12345",
    time_elapsed=100,
    data={"key": "value"}
)

print(response.to_dict())
```

## Contribución

Si deseas contribuir a este proyecto, por favor abre un issue o envía un pull request en el repositorio de GitHub.

## Licencia

Este proyecto está licenciado bajo los términos de la licencia MIT.