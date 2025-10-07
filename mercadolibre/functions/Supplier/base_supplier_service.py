from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

import logging
from mercadolibre.services.internal_api_service import (
    get_internal_api_service,
)
from mercadolibre.services.meli_service import FetchUser
from mercadolibre.utils.exceptions import UserMappingError, WMSRequestError
from mercadolibre.utils.mapper.data_mapper import SupplierMapper


logger = logging.getLogger(__name__)


@dataclass
class ServiceResult:
    success: bool
    action: str
    message: Optional[str] = None
    wms_response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a un dict limpio para serializar en JSON."""
        return asdict(self)


class BaseSupplierService:

    SUPPLIER_ENDPOINT = "/wms/adapter/v2/prv"

    def __init__(self):
        self.internal_api_service = get_internal_api_service()
        self.supplier_mapper = SupplierMapper

    def get_internal_api(self):
        return self.internal_api_service

    def get_supplier_from_meli(self, supplier_id):
        return FetchUser.fetch_user(supplier_id)

    def map_supplier_to_wms(self, meli_supplier):
        try:
            mapper = self.supplier_mapper.from_meli_to_wms_supplier(meli_supplier)
            return mapper.to_dict()
        except Exception as exception:
            logger.error(
                f"Error mapping customer {meli_supplier.get('id')}: {exception}"
            )
            raise UserMappingError(
                type_user="Supplier",
                message="Failed to map MercadoLibre Supplier to WMS format",
                user_id=meli_supplier.get("id", "unknown"),
            )

    def create_supplier_in_wms(self, wms_supplier, original_request):
        try:
            print(f"{original_request}")
            response = self.internal_api_service.post(
                self.SUPPLIER_ENDPOINT,
                original_request=original_request,
                json=[wms_supplier],  # WMS expects an array
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
