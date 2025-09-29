"""MercadoLibre to WMS synchronization and creation service."""

import logging
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from mercadolibre.services.meli_service import get_meli_service
from mercadolibre.services.internal_api_service import get_internal_api_service
from project.config_db import MeliConfigRepository
from mercadolibre.utils.mapper.data_mapper import ProductMapper, BarCodeMapper

logger = logging.getLogger(__name__)


class MeliWMSSyncService:
    """Service for synchronizing MercadoLibre products with WMS (creation and sync operations only)."""
    
    # Endpoints base para productos y códigos de barras
    PRODUCT_ENDPOINT = 'wms/adapter/v2/art'
    BARCODE_ENDPOINT = 'wms/base/v2/tRelacionCodbarras'
    
    def __init__(self):
        """Initialize sync service with required services."""
        self.meli = get_meli_service()
        self.wms = get_internal_api_service()
        self.config_repo = MeliConfigRepository()
        
    def sync_all_products(self, original_request: Any = None) -> Dict[str, Any]:
        """
        Sync all products from MercadoLibre to WMS.
        
        Args:
            original_request: Original Django request for auth
            
        Returns:
            Sync result
        """
        try:
            logger.info("Starting full product sync...")
            
            # Get all product IDs
            product_ids = self.get_user_products_ids()
            if not product_ids:
                return {
                    'success': False,
                    'message': 'No products found for user'
                }
            
            logger.info(f"Found {len(product_ids)} products to sync")
            
            # Get product details
            meli_items = self.get_products_details(product_ids)
            if not meli_items:
                return {
                    'success': False,
                    'message': 'Could not get product details'
                }
            
            # Map to WMS format
            wms_products = self.map_products_to_wms(meli_items)
            
            # Process products and barcodes in parallel
            with ThreadPoolExecutor(max_workers=2) as executor:
                products_future = executor.submit(
                    self.create_products_batch,
                    wms_products,
                    original_request
                )
                
                barcodes_future = executor.submit(
                    self.create_barcodes_batch,
                    meli_items,
                    original_request
                )
                
                products_result = products_future.result(timeout=30)
                barcodes_result = barcodes_future.result(timeout=30)
            
            return {
                'success': products_result['success'] and barcodes_result['success'],
                'message': f"{products_result['message']} | {barcodes_result['message']}",
                'products': products_result,
                'barcodes': barcodes_result,
                'total_products': len(product_ids),
                'synced_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.exception("Error in full sync")
            return {
                'success': False,
                'message': f'Full sync error: {str(e)}'
            }
        
    def get_user_products_ids(self) -> List[str]:
        """
        Get all product IDs for the configured MercadoLibre user.
        
        Returns:
            List of product IDs
        """
        try:
            user_id = self.config_repo.get_user_account_id()
            if not user_id:
                raise ValueError("No user account ID configured")
            
            response = self.meli.get(f'/users/{user_id}/items/search')
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                logger.error(f"Failed to get product IDs: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error extracting product IDs: {e}")
            return []
    
    def get_products_details(self, product_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get detailed information for multiple products.
        
        Args:
            product_ids: List of product IDs
            
        Returns:
            List of product details
        """
        if not product_ids:
            return []
        
        products = []
        
        # MercadoLibre allows max 20 IDs per request
        for i in range(0, len(product_ids), 20):
            batch = product_ids[i:i+20]
            ids_param = ','.join(batch)
            
            try:
                response = self.meli.get(f'/items?ids={ids_param}')
                if response.status_code == 200:
                    items = response.json()
                    products.extend(items)
                else:
                    logger.error(f"Failed to get product details: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Error getting product details batch: {e}")
                continue
                
        return products
    
    def get_product_detail(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a single product.
        
        Args:
            product_id: Product ID
            
        Returns:
            Product details or None
        """
        try:
            response = self.meli.get(f'/items/{product_id}')
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get product {product_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting product detail: {e}")
            return None
    
    def map_products_to_wms(self, meli_items: List[Dict]) -> List[Dict]:
        """
        Map MercadoLibre products to WMS format.
        
        Args:
            meli_items: List of MercadoLibre items
            
        Returns:
            List of WMS-formatted products
        """
        wms_products = []
        
        for item in meli_items:
            try:
                # Extract product data
                product_data = item.get('body', item)
                
                # Map using ProductMapper
                mapper = ProductMapper.from_meli_item(product_data)
                wms_product = mapper.to_wms_format()
                
                # Ensure required fields
                if self._validate_product(wms_product):
                    wms_products.append(wms_product)
                else:
                    logger.warning(f"Product {product_data.get('id')} missing required fields")
                    
            except Exception as e:
                logger.error(f"Error mapping product {item.get('id')}: {e}")
                continue
                
        return wms_products
    
    def _validate_product(self, product: Dict) -> bool:
        """Validate product has required fields."""
        required = {'productoean', 'descripcion', 'referencia'}
        return required.issubset(product.keys())
    
    def create_products_batch(
        self, 
        products: List[Dict], 
        original_request: Any = None
    ) -> Dict[str, Any]:
        """
        Create products in WMS (batch creation only).
        
        Args:
            products: List of products in WMS format
            original_request: Original Django request for auth
            
        Returns:
            Result dictionary
        """
        if not products:
            return {
                'success': False,
                'message': 'No products to create'
            }
        
        try:
            # Use POST for creation
            response = self.wms.post(
                self.PRODUCT_ENDPOINT,
                original_request=original_request,
                json=products
            )
            
            if response.status_code in (200, 201):
                return {
                    'success': True,
                    'message': f'Successfully created {len(products)} products',
                    'data': response.json() if response.text else {},
                    'action': 'create'
                }
            else:
                return {
                    'success': False,
                    'message': f'WMS error: {response.status_code} - {response.text}'
                }
                
        except Exception as e:
            logger.error(f"Error creating products in WMS: {e}")
            return {
                'success': False,
                'message': f'Error creating products: {str(e)}'
            }
    
    def create_barcodes_batch(
        self, 
        meli_items: List[Dict],
        original_request: Any = None
    ) -> Dict[str, Any]:
        """
        Create barcodes for MercadoLibre items (batch creation only).
        
        Args:
            meli_items: List of MercadoLibre items
            original_request: Original Django request for auth
            
        Returns:
            Result dictionary
        """
        results = []
        errors = []
        
        for item in meli_items:
            try:
                product_data = item.get('body', item)
                barcode_mapper = BarCodeMapper.from_meli_item(product_data)
                
                if barcode_mapper:
                    barcode_data = barcode_mapper.to_dict()
                    logger.info(f"Processing barcode creation: {barcode_data}")
                    
                    # Use POST for creation
                    response = self.wms.post(
                        self.BARCODE_ENDPOINT,
                        original_request=original_request,
                        json=barcode_data
                    )
                    
                    if response.status_code in (200, 201):
                        results.append({
                            'item_id': product_data.get('id'),
                            'barcode': barcode_mapper.codbarrasasignado,
                            'success': True,
                            'action': 'created'
                        })
                    else:
                        errors.append({
                            'item_id': product_data.get('id'),
                            'error': f'WMS error: {response.status_code} - {response.text[:200] if response.text else "No message"}'
                        })
                else:
                    logger.warning(f"No barcode found for item {product_data.get('id')}")
                        
            except Exception as e:
                logger.error(f"Error creating barcode: {e}")
                errors.append({
                    'item_id': item.get('id'),
                    'error': str(e)
                })
        
        return {
            'success': len(results) > 0 or len(errors) == 0,
            'message': f'Created {len(results)} barcodes, {len(errors)} errors',
            'created': len(results),
            'errors': len(errors),
            'results': results,
            'error_details': errors
        }
    
    def sync_specific_products(
        self, 
        product_ids: List[str],
        original_request: Any = None,
        force_update: bool = False
    ) -> Dict[str, Any]:
        """
        Sync specific products from MercadoLibre to WMS.
        
        Args:
            product_ids: List of specific product IDs
            original_request: Original Django request for auth
            force_update: If True, delegate to update service instead
            
        Returns:
            Sync result
        """
        try:
            logger.info(f"Syncing {len(product_ids)} specific products (force_update={force_update})...")
            
            # If force_update is True, delegate to update service
            if force_update:
                from .update import get_update_service
                update_service = get_update_service()
                
                results = []
                for product_id in product_ids:
                    result = update_service.update_single_product(product_id, original_request)
                    results.append(result)
                
                successful = sum(1 for r in results if r['success'])
                return {
                    'success': successful > 0,
                    'message': f'Updated {successful}/{len(product_ids)} products',
                    'results': results,
                    'synced_at': datetime.now().isoformat()
                }
            
            # If not force_update, create new products (sync mode)
            meli_items = self.get_products_details(product_ids)
            
            if not meli_items:
                return {
                    'success': False,
                    'message': 'Could not get product details'
                }
            
            wms_products = self.map_products_to_wms(meli_items)
            
            with ThreadPoolExecutor(max_workers=2) as executor:
                products_future = executor.submit(
                    self.create_products_batch,
                    wms_products,
                    original_request
                )
                
                barcodes_future = executor.submit(
                    self.create_barcodes_batch,
                    meli_items,
                    original_request
                )
                
                products_result = products_future.result(timeout=15)
                barcodes_result = barcodes_future.result(timeout=15)
            
            return {
                'success': products_result['success'],
                'message': f"{products_result['message']} | {barcodes_result['message']}",
                'products': products_result,
                'barcodes': barcodes_result,
                'product_ids': product_ids,
                'synced_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.exception("Error in specific sync")
            return {
                'success': False,
                'message': f'Sync error: {str(e)}'
            }


# Singleton instance
_sync_service: Optional[MeliWMSSyncService] = None


def get_sync_service() -> MeliWMSSyncService:
    """Get or create sync service singleton."""
    global _sync_service
    if _sync_service is None:
        _sync_service = MeliWMSSyncService()
    return _sync_service
