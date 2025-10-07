"""
Customer update service.

Handles updating individual customers from MercadoLibre to WMS.
If a customer does not exist in WMS, it will be created automatically.
Uses BaseCustomerService for core operations (fetching, mapping, creating).
"""

import logging
from typing import Any, Optional
from datetime import datetime

from mercadolibre.utils.exceptions import UserMappingError, WMSRequestError
from .base_customer_service import BaseCustomerService, ServiceResult

logger = logging.getLogger(__name__)


class CustomerUpdateService:
    """Service for updating single MercadoLibre customers in WMS."""

    def __init__(self):
        self.base_service = BaseCustomerService()

    def update_single_customer(
        self, customer_id: str, original_request: Any = None
    ) -> ServiceResult:
        # 0️⃣ Validación inicial
        if not customer_id:
            logger.warning("No customer_id provided to update_single_customer")
            return ServiceResult(
                success=False,
                action="error",
                message="Customer ID is None or empty",
                error="invalid_customer_id",
            )

        try:
            # 1️⃣ Traer datos desde MercadoLibre
            customer_data = self.base_service.get_customer_from_meli(customer_id)
            if not customer_data:
                return ServiceResult(
                    success=False,
                    action="error",
                    message="Customer not found in MercadoLibre",
                    error="not_found",
                )

            # 2️⃣ Mapear a WMS
            wms_customer = self.base_service.map_customer_to_wms(customer_data)
            if not isinstance(wms_customer, dict):
                wms_customer = getattr(wms_customer, "to_dict", lambda: wms_customer)()

            # 3️⃣ Intentar actualizar en WMS
            response = self.base_service.wms.put(
                self.base_service.CUSTOMER_ENDPOINT,
                original_request=original_request,
                json=wms_customer,
            )

            resp_json = (
                response.json() if hasattr(response, "json") and response.text else {}
            )

            # ✅ PUT exitoso
            if response.status_code in (200, 201):
                action = "updated"
                message = "Customer updated successfully"

            # 4️⃣ PUT devuelve 404 → fallback a creación
            elif response.status_code == 404:
                logger.warning(f"Customer {customer_id} not found in WMS. Creating...")
                create_result = self.base_service.create_customer_in_wms(
                    wms_customer, original_request
                )
                return ServiceResult(
                    success=create_result.success,
                    action="created_via_fallback",
                    message="Customer did not exist in WMS, created instead.",
                    wms_response=create_result.wms_response,
                )

            # 5️⃣ PUT devuelve 400 con "record already exists"
            elif response.status_code == 400 and "record already exists" in str(
                resp_json.get("errors", [])
            ):
                logger.info(
                    f"Customer {customer_id} already exists in WMS, skipping creation."
                )
                action = "already_exists"
                message = "Customer already exists in WMS"

            # 6️⃣ Otros errores
            else:
                raise WMSRequestError(
                    status_code=response.status_code, message=response.text[:200]
                )

            return ServiceResult(
                success=True,
                action=action,
                message=message,
                wms_response={
                    "customer_id": customer_id,
                    "ml_data": customer_data,
                    "wms_data": wms_customer,
                    "raw": resp_json,
                    "updated_at": datetime.now().isoformat(),
                },
            )

        except (UserMappingError, WMSRequestError) as e:
            logger.exception(f"Mapping or WMS error for customer {customer_id}")
            return ServiceResult(
                success=False,
                action="error",
                message=str(e),
                error=getattr(e, "status_code", "mapping_or_wms_error"),
            )

        except Exception as e:
            logger.exception(f"Unexpected error updating customer {customer_id}")
            return ServiceResult(
                success=False,
                action="error",
                message=str(e),
                error="unexpected_error",
            )


# ----------------------------
# Singleton + convenience functions
# ----------------------------
_update_service: Optional[CustomerUpdateService] = None


def get_customer_update_service() -> CustomerUpdateService:
    global _update_service
    if _update_service is None:
        _update_service = CustomerUpdateService()
    return _update_service


def update_single_customer(
    customer_id: str, original_request: Any = None
) -> ServiceResult:
    return get_customer_update_service().update_single_customer(
        customer_id, original_request
    )
