"""
Servicio para interactuar con la API de Transprensa.
Maneja autenticación, tokens y reintentos automáticos.
"""

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
                except (requests.exceptions.RequestException, TimeoutError):
                    if attempt < max_retries:
                        time.sleep(delay)
                    else:
                        raise

        return wrapper

    return decorator


class TransprensaService:
    """Servicio para enviar peticiones a la API de Transprensa."""

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
        self.base_url = (
            "https://transprensa.colombiasoftware.co/index.php"
            if self.is_test
            else "https://transprensa.colombiasoftware.net/index.php"
        )
        self.token = trans_conf.get("token")
        self.cookie = trans_conf.get("cookie")
        self.api_login = "servicio.Seguridad.login"

    def _refresh_token(self) -> Optional[str]:
        """
        Solicita un nuevo token usando el login.

        Returns:
            Nuevo token o None si falla
        """
        try:
            payload = {
                "usuario_login": self.usuario,
                "usuario_password": self.password,
            }
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Cookie": self.cookie,
            }
            print("Refrescando token de Transprensa...")
            login_url = f"{self.base_url}?api={self.api_login}"
            response = self.session.post(login_url, headers=headers, data=payload)
            response.raise_for_status()

            try:
                data = response.json()
            except ValueError:
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

            self.repo.update_field("transprensa_config.token", new_token)
            self.token = new_token

            return new_token

        except Exception:
            raise

    def request(
        self, method: str, endpoint: str, data: Optional[dict] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Envía una petición a la API de Transprensa.
        Si el token está vencido, lo renueva y reintenta.

        Args:
            method: Método HTTP (GET, POST, etc.)
            endpoint: Endpoint de la API
            data: Datos a enviar en el body
            **kwargs: Argumentos adicionales para requests

        Returns:
            Dict con respuesta de la API
        """
        if endpoint.startswith("http"):
            url = endpoint
        else:
            base_without_login = self.base_url.replace(
                "?api=servicio.Seguridad.login", ""
            )
            url = f"{base_without_login}?api={endpoint}"

        max_retries = 2
        for attempt in range(max_retries):
            headers = {
                "Authorization": self.token,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Cookie": self.cookie if self.cookie else "",
            }

            try:
                response = self.session.request(
                    method, url, headers=headers, json=data, timeout=10
                )

                try:
                    json_response = response.json()
                except ValueError:
                    raise ValueError(
                        f"La API devolvió una respuesta no válida: {response.text[:100]}"
                    )

                if response.status_code == 401 or (
                    isinstance(json_response, dict)
                    and not json_response.get("success")
                    and (
                        "sesión han expirado" in json_response.get("msg", "")
                        or "token" in json_response.get("msg", "").lower()
                    )
                ):
                    if attempt == 0:
                        self._refresh_token()
                        continue
                    else:
                        raise RuntimeError(
                            f"Token sigue vencido después del refresh: {json_response}"
                        )
                if response.status_code == 400 and isinstance(json_response, dict):
                    return json_response

                response.raise_for_status()
                return json_response

            except requests.exceptions.RequestException:
                if attempt == 1:
                    raise
                self._refresh_token()
        raise RuntimeError(
            "No se pudo completar la petición después de intentar refrescar el token"
        )


_transprensa_service: Optional[TransprensaService] = None


def get_transprensa_service() -> TransprensaService:
    """
    Obtiene la instancia singleton del servicio de Transprensa.

    Returns:
        TransprensaService: Instancia singleton
    """
    global _transprensa_service
    if _transprensa_service is None:
        _transprensa_service = TransprensaService()
    return _transprensa_service
