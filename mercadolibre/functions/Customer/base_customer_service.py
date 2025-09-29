"""
BaseCustomerService: Core customer operations for MercadoLibre -> WMS.
Provides reusable methods for fetching, mapping, and creating customers.
"""

import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional
from mercadolibre.services.internal_api_service import InternalAPIService
from mercadolibre.utils.fetch_user import FetchUser
from mercadolibre.utils.mapper.data_mapper import CustomerMapper

logger = logging.getLogger(__name__)


# ------------------------------
# Excepciones personalizadas
# ------------------------------
class CustomerMappingError(Exception):
    """Error al mapear un cliente desde MercadoLibre a WMS."""

    def __init__(self, customer_id: str, message: str):
        self.customer_id = customer_id
        self.message = message
        super().__init__(f"[Customer {customer_id}] {message}")


class WMSRequestError(Exception):
    """Error en la comunicación o lógica con el WMS."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"[WMS {status_code}] {message}")


# ------------------------------
# Objeto de resultado unificado
# ------------------------------
@dataclass
class ServiceResult:
    success: bool
    action: str
    message: Optional[str] = None
    wms_response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ------------------------------
# Servicio principal
# ------------------------------
class BaseCustomerService:
    """
    Core reusable customer operations.
    Handles:
        - Fetching user from MercadoLibre
        - Mapping customer data to WMS format
        - Creating customer in WMS
    """

    CUSTOMER_ENDPOINT = "/wms/adapter/v2/clt"

    def __init__(self):
        self.wms = InternalAPIService()
        self.customer_mapper = CustomerMapper

    def get_customer_from_meli(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Fetch customer data from MercadoLibre using FetchUser helper."""
        return FetchUser.fetch_user(customer_id)

    def map_customer_to_wms(self, meli_customer: Dict[str, Any]) -> Dict[str, Any]:
        """Map MercadoLibre customer to WMS format using CustomerMapper."""
        try:
            mapper = self.customer_mapper.from_meli_customer(meli_customer)
            return mapper.to_dict()
        except Exception as e:
            logger.error(f"Error mapping customer {meli_customer.get('id')}: {e}")
            raise CustomerMappingError(
                customer_id=meli_customer.get("id", "unknown"),
                message="Failed to map MercadoLibre customer to WMS format",
            )

    def create_customer_in_wms(
        self, wms_customer: Dict[str, Any], original_request: Any = None
    ) -> ServiceResult:
        """Create a customer in WMS and return a structured result."""
        try:
            response = self.wms.post(
                self.CUSTOMER_ENDPOINT,
                original_request=original_request,
                json=[wms_customer],  # WMS expects an array
            )

            if response.status_code not in (200, 201):
                raise WMSRequestError(
                    status_code=response.status_code,
                    message=response.text[:200],
                )

            wms_response = response.json()
            created = wms_response.get("created", [])
            errors = wms_response.get("errors", [])

            if created:
                return ServiceResult(
                    success=True,
                    action="created",
                    wms_response=wms_response,
                )
            elif errors:
                return ServiceResult(
                    success=False,
                    action="error",
                    wms_response=wms_response,
                    message=f"WMS errors: {', '.join(errors)}",
                )

            return ServiceResult(
                success=True,
                action="processed",
                wms_response=wms_response,
            )

        except WMSRequestError as e:
            logger.error(str(e))
            return ServiceResult(success=False, action="error", message=e.message)

        except Exception as e:
            logger.exception("Unexpected error creating customer in WMS")
            return ServiceResult(success=False, action="error", message=str(e))
