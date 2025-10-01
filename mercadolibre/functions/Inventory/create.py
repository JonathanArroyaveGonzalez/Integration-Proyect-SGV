"""Service for creating inventory in WMS."""

from typing import Dict, Any
from django.http import HttpRequest

from mercadolibre.services.meli_service import get_meli_service
from mercadolibre.services.internal_api_service import get_internal_api_service
from mercadolibre.utils.mapper.data_mapper import InventoryMapper

import logging
logger = logging.getLogger(__name__)


class InventoryCreateService:
    """Service for creating inventory from MercadoLibre to WMS."""
    
    def __init__(self):
        self.meli_service = get_meli_service()
        self.internal_service = get_internal_api_service()
    
    def create_inventory(self, product_id: str, request: HttpRequest) -> Dict[str, Any]:
        """
        Create inventory in WMS for a MercadoLibre product.
        
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
            
            # Create inventory in WMS
            response = self.internal_service.post(
                'wms/adapter/v2/inventory',
                json=inventory_data,
                original_request=request
            )
            
            if response.status_code != 201:
                return {
                    'success': False,
                    'message': f'Error creating inventory in WMS: {response.text}'
                }
            
            return {
                'success': True,
                'message': f'Inventory created successfully for product {product_id}',
                'data': response.json()
            }
            
        except Exception as e:
            logger.exception(f"Error creating inventory for product {product_id}")
            return {
                'success': False,
                'message': f'Unexpected error: {str(e)}'
            }


# Singleton instance
_create_service = None


def get_create_service() -> InventoryCreateService:
    """Get or create inventory create service singleton."""
    global _create_service
    if _create_service is None:
        _create_service = InventoryCreateService()
    return _create_service
