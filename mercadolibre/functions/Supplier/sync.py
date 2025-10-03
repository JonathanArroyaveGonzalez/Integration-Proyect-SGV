from concurrent.futures import ThreadPoolExecutor
import datetime
from typing import Any, List, Optional, Dict
from mercadolibre.functions.Customer.base_customer_service import ServiceResult
from mercadolibre.functions.Supplier.base_supplier_service import BaseSupplierService
from mercadolibre.utils.exceptions import UserMappingError

import logging

logger = logging.getLogger(__name__)


class MeliSupplierService:

    ENDPOINT_SUPPLIER = "wms/adapter/v2/supplier"

    # La logica por la cual pienso es consumir el servicio de sincronizacion de
    # clientes y actualizacion de clientes, como tal para los datos
    def __init__(self):
        self.base_supplier_service = BaseSupplierService()

    def _sync_single_supplier(
        self, supplier_id: str, original_request: Any = None, force_update: bool = False
    ):
        try:
            # Step 1: Fetch customer from MercadoLibre
            supplier_data = self.base_supplier_service.get_supplier_from_meli(
                supplier_id
            )
            if not supplier_data:
                return ServiceResult(
                    success=False,
                    action="error",
                    message="Supplier not found in MercadoLibre",
                    error="not_found",
                )

            # Step 2: Map ML customer data to WMS format
            wms_supplier = self.base_supplier_service.map_supplier_to_wms(supplier_data)

            # Step 3: Create customer in WMS
            result = self.base_supplier_service.create_supplier_in_wms(
                wms_supplier, original_request
            )

            # Agregar datos extra al resultado
            result.wms_response = {
                "customer_id": supplier_id,
                "ml_data": supplier_data,
                "wms_data": wms_supplier,
                "raw": result.wms_response,
            }

            return result
        except UserMappingError as e:
            logger.error(f"Mapping error for customer {supplier_id}: {e}")
            return ServiceResult(
                success=False, action="error", message=str(e), error="mapping_error"
            )

    def sync_specific_suppliers(
        self,
        suppliers_ids: List[str],
        original_request: Any = None,
        force_update: bool = False,
    ):
        results_summary = {
            "success": True,
            "message": "",
            "total_processed": 0,
            "total_created": 0,
            "total_updated": 0,
            "total_errors": 0,
            "customers": [],
            "errors": [],
            "processed_at": datetime.datetime.now().isoformat(),
        }

        if not suppliers_ids:
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
                    self._sync_single_supplier, cid, original_request, force_update
                )
                for cid in suppliers_ids
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


_sync_service: Optional[MeliSupplierService] = None


def get_supplier_sync_service():
    """Get or create singleton instance of MeliCustomerSyncService."""
    global _sync_service
    if _sync_service is None:
        _sync_service = MeliSupplierService()
    return _sync_service


def sync_customers(
    supplier_ids: List[str], original_request: Any = None
) -> Dict[str, Any]:
    """Convenience function to sync customers without directly instantiating the service."""
    return get_supplier_sync_service().sync_specific_suppliers(
        supplier_ids, original_request
    )
