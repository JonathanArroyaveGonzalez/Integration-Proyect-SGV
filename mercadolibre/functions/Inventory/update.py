"""Service for updating inventory in WMS."""

from typing import Dict, Any
from django.http import HttpRequest

from mercadolibre.services.meli_service import get_meli_service
from mercadolibre.services.internal_api_service import get_internal_api_service
from mercadolibre.utils.mapper.data_mapper import InventoryMapper

import logging
logger = logging.getLogger(__name__)


class InventoryUpdateService:
    """Service for updating inventory from MercadoLibre to WMS."""
    
    def __init__(self):
        self.meli_service = get_meli_service()
        self.internal_service = get_internal_api_service()
    
    def update_inventory(self, product_id: str, request: HttpRequest) -> Dict[str, Any]:
        """
        Update inventory in WMS for a MercadoLibre product.
        
        Args:
            product_id: MercadoLibre product ID
            request: Original request for auth forwarding
            
        Returns:
            Dict with operation results
        """
        try:
            # Get product details from MercadoLibre
            product_data = self.meli_service.get_product(product_id)
            
            if not product_data:
                return {
                    'success': False,
                    'message': f'Product {product_id} not found in MercadoLibre'
                }
            
            # Map product data to WMS inventory format
            inventory = InventoryMapper.from_meli_item(product_data)
            inventory_data = inventory.to_wms_format()
            
            # Update inventory in WMS using product_id as referencia
            response = self.internal_service.put(
                f'wms/adapter/v2/inventory?referencia={product_id}',
                json=inventory_data,
                original_request=request
            )
            
            if response.status_code not in [200, 201]:
                return {
                    'success': False,
                    'message': f'Error updating inventory in WMS: {response.text}'
                }
            
            return {
                'success': True,
                'message': f'Inventory updated successfully for product {product_id}',
                'data': response.json()
            }
            
        except Exception as e:
            logger.exception(f"Error updating inventory for product {product_id}")
            return {
                'success': False,
                'message': f'Unexpected error: {str(e)}'
            }


# Singleton instance
_update_service = None


def get_update_service() -> InventoryUpdateService:
    """Get or create inventory update service singleton."""
    global _update_service
    if _update_service is None:
        _update_service = InventoryUpdateService()
    return _update_service
