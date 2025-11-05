import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from functools import wraps
from typing import Optional, Dict, Any

from settings.models.transprensa import TransprensaModel


def retry_on_failure(max_retries: int = 3, delay: int = 3):
    """Reintenta la petición si hay errores de red o timeout."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (requests.exceptions.RequestException, TimeoutError) as e:
                    print(f"Reintento {attempt}/{max_retries}: {e}")
                    if attempt < max_retries:
                        time.sleep(delay)
                    else:
                        raise

        return wrapper

    return decorator


class TransprensaService:
    """Servicio para enviar peticiones a la API de Transprensa con manejo de token y sesión persistente."""

    def __init__(self):
        self.repo = TransprensaModel()
        self.session = self._setup_session()
        self.config = self.repo.get_config()
        self._load_config_data()

    def _setup_session(self):
        """Configura la sesión de requests con reintentos."""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _load_config_data(self):
        """Carga variables de configuración desde Mongo."""
        trans_conf = self.config.get("transprensa_config", {})
        self.usuario = trans_conf.get("usuario_login")
        self.password = trans_conf.get("usuario_password")
        self.is_test = trans_conf.get("test", "True").lower() == "true"
        # URLs según documentación
        self.base_url = (
            "https://transprensa.colombiasoftware.co/index.php"
            if self.is_test
            else "https://transprensa.colombiasoftware.net/index.php"
        )
        self.token = trans_conf.get("token")
        self.cookie = trans_conf.get("cookie")
        self.api_login = "servicio.Seguridad.login"

    def _refresh_token(self) -> Optional[str]:
        """Solicita un nuevo token usando el login."""
        print("Refrescando token de Transprensa...")
        try:
            payload = {
                "usuario_login": self.usuario,
                "usuario_password": self.password,
            }
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Cookie": self.cookie,
            }

            print(f"[DEBUG] URL de login: {self.base_url}")
            print(f"[DEBUG] Payload de login: {payload}")

            # response = self.session.post(self.base_url, headers=headers, data=payload)
            login_url = f"{self.base_url}?api={self.api_login}"
            response = self.session.post(login_url, headers=headers, data=payload)

            print(f"[DEBUG] Status code login: {response.status_code}")
            print(
                f"[DEBUG] Response text login (primeros 200 chars): {response.text[:200]}"
            )

            response.raise_for_status()

            try:
                data = response.json()
            except ValueError as e:
                print(f"[ERROR] Respuesta de login no es JSON válido: {e}")
                print(f"[ERROR] Response text completo: {response.text}")
                raise RuntimeError(
                    f"La API de login devolvió una respuesta no válida: {response.text[:100]}"
                )

            if not data.get("success"):
                raise RuntimeError(
                    f"Error de login: {data.get('msg', 'Error desconocido')}"
                )

            new_token = data.get("data", {}).get("token")
            if not new_token:
                raise RuntimeError(f"No se obtuvo token en la respuesta: {data}")

            # Actualizar token en MongoDB
            self.repo.update_field("transprensa_config.token", new_token)
            self.token = new_token

            print(f"[SUCCESS] Token actualizado correctamente: {new_token[:20]}...")
            return new_token

        except Exception as e:
            print(f"[ERROR] Error al refrescar el token: {str(e)}")
            raise

    def request(
        self, method: str, endpoint: str, data: Optional[dict] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Envía una petición a la API de Transprensa.
        Si el token está vencido, lo renueva y reintenta.
        """
        # Construir la URL correctamente
        if endpoint.startswith("http"):
            url = endpoint
        else:
            # Construir URL base sin el endpoint de login
            base_without_login = self.base_url.replace(
                "?api=servicio.Seguridad.login", ""
            )
            url = f"{base_without_login}?api={endpoint}"

        # Intentar hasta 2 veces (primera vez + un retry si el token está vencido)
        for attempt in range(2):
            headers = {
                "Authorization": self.token,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Cookie": self.cookie if self.cookie else "",
            }

            try:
                print(f"[DEBUG] Realizando petición a: {url}")
                print(f"[DEBUG] Headers: {headers}")
                # No imprimir el payload completo si es muy grande (contiene PDFs en base64)
                if data and isinstance(data, dict):
                    data_str = str(data)
                    if len(data_str) > 500:
                        print(
                            f"[DEBUG] Data: {{payload de {len(data_str)} caracteres}}"
                        )
                    else:
                        print(f"[DEBUG] Data: {data}")
                else:
                    print(f"[DEBUG] Data: {data}")

                response = self.session.request(
                    method, url, headers=headers, json=data, timeout=10
                )

                print(f"[DEBUG] Status code: {response.status_code}")
                print(
                    f"[DEBUG] Response text (primeros 200 chars): {response.text[:200]}"
                )

                # Verificar si la respuesta es JSON válida
                try:
                    json_response = response.json()
                except ValueError as e:
                    print(f"[ERROR] Respuesta no es JSON válido: {e}")
                    print(f"[ERROR] Response text completo: {response.text}")
                    raise ValueError(
                        f"La API devolvió una respuesta no válida: {response.text[:100]}"
                    )

                # Verificar si el token está vencido
                if response.status_code == 401 or (
                    isinstance(json_response, dict)
                    and (
                        not json_response.get("success")
                        and (
                            "sesión han expirado" in json_response.get("msg", "")
                            or "token" in json_response.get("msg", "").lower()
                        )
                    )
                ):
                    if attempt == 0:  # Solo intentar refrescar en el primer intento
                        print("Token expirado detectado, refrescando...")
                        self._refresh_token()
                        continue  # Reintentar con el nuevo token
                    else:
                        raise RuntimeError(
                            f"Token sigue vencido después del refresh: {json_response}"
                        )

                # Si llegamos aquí, la respuesta es válida
                response.raise_for_status()
                return json_response

            except requests.exceptions.RequestException as e:
                print(f"[ERROR] Error en la petición HTTP: {e}")
                if attempt == 1:  # En el último intento, relanzar la excepción
                    raise
                # En el primer intento, intentar refrescar token
                print("Intentando refrescar token debido a error HTTP...")
                self._refresh_token()

        # Si llegamos aquí, algo salió mal
        raise RuntimeError(
            "No se pudo completar la petición después de intentar refrescar el token"
        )


# Singleton para TransprensaService
_transprensa_service: Optional[TransprensaService] = None


def get_transprensa_service() -> TransprensaService:
    global _transprensa_service
    if _transprensa_service is None:
        _transprensa_service = TransprensaService()
    return _transprensa_service
