"""
Customer update service.

Handles updating individual customers from MercadoLibre to WMS.
If a customer does not exist in WMS, it will be created automatically.
Uses BaseCustomerService for core operations (fetching, mapping, creating).
"""

import logging
from typing import Any, Dict, Optional
from datetime import datetime
from .base_customer_service import (
    BaseCustomerService,
    ServiceResult,
    CustomerMappingError,
    WMSRequestError,
)

logger = logging.getLogger(__name__)


class CustomerUpdateService:
    """
    Service for updating single MercadoLibre customers in WMS.
    """

    def __init__(self):
        """Initialize the service with a BaseCustomerService instance."""
        self.base_service = BaseCustomerService()

    def update_single_customer(
        self, customer_id: str, original_request: Any = None
    ) -> ServiceResult:
        """
        Update a single customer in WMS, creating if not exists.
        """
        try:
            # Step 1: Fetch from MercadoLibre
            customer_data = self.base_service.get_customer_from_meli(customer_id)
            if not customer_data:
                return ServiceResult(
                    success=False,
                    action="error",
                    message="Customer not found in MercadoLibre",
                    error="not_found",
                )

            # Step 2: Map to WMS
            wms_customer = self.base_service.map_customer_to_wms(customer_data)

            # Step 3: Try update, fallback to creation
            update_result = self._update_customer_in_wms(wms_customer, original_request)

            # Step 4: Enrich result with metadata
            update_result.wms_response = {
                "customer_id": customer_id,
                "ml_data": customer_data,
                "wms_data": wms_customer,
                "raw": update_result.wms_response,
                "updated_at": datetime.now().isoformat(),
            }

            return update_result

        except CustomerMappingError as e:
            logger.error(f"Mapping error for customer {customer_id}: {e}")
            return ServiceResult(
                success=False, action="error", message=str(e), error="mapping_error"
            )

        except WMSRequestError as e:
            logger.error(f"WMS error for customer {customer_id}: {e}")
            return ServiceResult(
                success=False,
                action="error",
                message=e.message,
                error=f"wms_{e.status_code}",
            )

        except Exception as e:
            logger.exception(f"Unexpected error updating customer {customer_id}")
            return ServiceResult(
                success=False, action="error", message=str(e), error="unexpected_error"
            )

    def _update_customer_in_wms(
        self, wms_customer: Dict[str, Any], original_request: Any = None
    ) -> ServiceResult:
        """
        Try updating customer in WMS. If not found (404), create the customer.
        """
        try:
            response = self.base_service.wms.put(
                self.base_service.CUSTOMER_ENDPOINT,
                original_request=original_request,
                json=wms_customer,
            )

            if response.status_code in (200, 201):
                return ServiceResult(
                    success=True,
                    action="updated",
                    message="Customer updated successfully",
                    wms_response=response.json() if response.text else {},
                )

            elif response.status_code == 404:
                # Not found → fallback to creation
                return self.base_service.create_customer_in_wms(
                    wms_customer, original_request
                )

            # Other failures
            raise WMSRequestError(
                status_code=response.status_code,
                message=response.text[:200],
            )

        except WMSRequestError as e:
            logger.error(str(e))
            return ServiceResult(
                success=False,
                action="update_failed",
                message=e.message,
                error=f"wms_{e.status_code}",
            )

        except Exception as e:
            logger.exception("Unexpected error updating customer in WMS")
            return ServiceResult(
                success=False, action="error", message=str(e), error="unexpected_error"
            )


# ----------------------------
# Singleton + convenience functions
# ----------------------------
_update_service: Optional[CustomerUpdateService] = None


def get_customer_update_service() -> CustomerUpdateService:
    """Get or create singleton instance of CustomerUpdateService."""
    global _update_service
    if _update_service is None:
        _update_service = CustomerUpdateService()
    return _update_service


def update_single_customer(
    customer_id: str, original_request: Any = None
) -> ServiceResult:
    """Convenience function to update a customer without directly instantiating the service."""
    return get_customer_update_service().update_single_customer(
        customer_id, original_request
    )
