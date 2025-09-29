"""
Customer synchronization service.

Handles syncing specific customers from MercadoLibre to WMS using BaseCustomerService.
Provides both single-customer and batch synchronization with detailed logging and results.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from .base_customer_service import (
    BaseCustomerService,
    ServiceResult,
    CustomerMappingError,
    WMSRequestError,
)

logger = logging.getLogger(__name__)


class MeliCustomerSyncService:
    """
    Service to synchronize MercadoLibre customers with WMS.

    Attributes:
        base_service (BaseCustomerService): Core service handling fetch, mapping, and creation.
    """

    def __init__(self):
        """Initialize the service with a BaseCustomerService instance."""
        self.base_service = BaseCustomerService()

    def _sync_single_customer(
        self, customer_id: str, original_request: Any = None, force_update: bool = False
    ) -> ServiceResult:
        """
        Synchronize a single customer from MercadoLibre to WMS.
        """
        try:
            # Step 1: Fetch customer from MercadoLibre
            customer_data = self.base_service.get_customer_from_meli(customer_id)
            if not customer_data:
                return ServiceResult(
                    success=False,
                    action="error",
                    message="Customer not found in MercadoLibre",
                    error="not_found",
                )

            # Step 2: Map ML customer data to WMS format
            wms_customer = self.base_service.map_customer_to_wms(customer_data)

            # Step 3: Create customer in WMS
            result = self.base_service.create_customer_in_wms(
                wms_customer, original_request
            )

            # Agregar datos extra al resultado
            result.wms_response = {
                "customer_id": customer_id,
                "ml_data": customer_data,
                "wms_data": wms_customer,
                "raw": result.wms_response,
            }

            return result

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
            logger.exception(f"Unexpected error syncing customer {customer_id}")
            return ServiceResult(
                success=False, action="error", message=str(e), error="unexpected_error"
            )

    def sync_specific_customers(
        self,
        customer_ids: List[str],
        original_request: Any = None,
        force_update: bool = False,
    ) -> Dict[str, Any]:
        """
        Synchronize multiple customers in parallel.
        """
        results_summary = {
            "success": True,
            "message": "",
            "total_processed": 0,
            "total_created": 0,
            "total_updated": 0,
            "total_errors": 0,
            "customers": [],
            "errors": [],
            "processed_at": datetime.now().isoformat(),
        }

        if not customer_ids:
            results_summary.update(
                {
                    "success": False,
                    "total_errors": 1,
                    "errors": ["Customer IDs list is empty"],
                    "message": "No customer IDs provided",
                }
            )
            return results_summary

        # Step 1: Process customers in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                cid: executor.submit(
                    self._sync_single_customer, cid, original_request, force_update
                )
                for cid in customer_ids
            }
            for cid, future in futures.items():
                try:
                    result: ServiceResult = future.result()
                    results_summary["customers"].append(result.__dict__)
                    results_summary["total_processed"] += 1

                    if result.success:
                        if result.action == "created":
                            results_summary["total_created"] += 1
                        elif result.action == "updated":
                            results_summary["total_updated"] += 1
                    else:
                        results_summary["total_errors"] += 1
                        results_summary["errors"].append(
                            f"Customer {cid}: {result.message}"
                        )

                except Exception as e:
                    logger.exception(f"Error processing customer {cid}")
                    results_summary["total_processed"] += 1
                    results_summary["total_errors"] += 1
                    results_summary["errors"].append(f"Customer {cid}: {str(e)}")

        # Step 2: Build summary message
        if results_summary["total_errors"] == 0:
            results_summary["message"] = (
                f"All {results_summary['total_processed']} customers synced successfully"
            )
        elif results_summary["total_errors"] < results_summary["total_processed"]:
            results_summary["message"] = (
                f"{results_summary['total_processed'] - results_summary['total_errors']} "
                f"customers synced, {results_summary['total_errors']} errors"
            )
        else:
            results_summary["success"] = False
            results_summary["message"] = (
                f"All {results_summary['total_errors']} customers failed to sync"
            )

        return results_summary


# ----------------------------
# Singleton + convenience functions
# ----------------------------
_sync_service: Optional[MeliCustomerSyncService] = None


def get_customer_sync_service() -> MeliCustomerSyncService:
    """Get or create singleton instance of MeliCustomerSyncService."""
    global _sync_service
    if _sync_service is None:
        _sync_service = MeliCustomerSyncService()
    return _sync_service


def sync_customers(
    customer_ids: List[str], original_request: Any = None
) -> Dict[str, Any]:
    """Convenience function to sync customers without directly instantiating the service."""
    return get_customer_sync_service().sync_specific_customers(
        customer_ids, original_request
    )
