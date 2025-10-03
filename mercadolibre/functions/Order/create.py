"""
Order synchronization service for MercadoLibre.
Handles order sync operations from MercadoLibre to WMS.
"""
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from mercadolibre.services.meli_service import MeliService
from mercadolibre.services.internal_api_service import InternalAPIService
from mercadolibre.utils.mapper.data_mapper import OrderMapper

logger = logging.getLogger(__name__)


class MeliOrderSyncService:
    """Service for synchronizing orders from MercadoLibre to WMS."""
    
    def __init__(self):
        """Initialize the order sync service."""
        self.meli = MeliService()
        self.wms = InternalAPIService()
        self.ORDER_ENDPOINT = "/wms/adapter/v2/sale_order"
        
        logger.info("OrderSyncService initialized")
    
    def sync_all_orders(
        self,
        original_request: Any = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Sync recent orders from MercadoLibre to WMS.
        
        Args:
            original_request: Original Django request for auth
            status: Optional order status filter (paid, confirmed, cancelled)
            limit: Maximum number of orders to sync
            
        Returns:
            Dictionary with sync results
        """
        try:
            logger.info(f"Starting order synchronization (status={status}, limit={limit})...")
            
            # Get MeLi configuration to get seller ID
            from project.config_db.repository import MeliConfigRepository
            config = MeliConfigRepository().get_config()
            
            if not config or not config.user_id:
                return {
                    'success': False,
                    'message': 'MercadoLibre user ID not configured',
                    'total_processed': 0,
                    'total_created': 0,
                    'total_updated': 0,
                    'total_errors': 1,
                    'orders': [],
                    'errors': ['User ID not found in configuration'],
                    'processed_at': datetime.now().isoformat()
                }
            
            # Get orders from MercadoLibre
            orders = self.meli.get_user_orders(config.user_id, status, limit)
            
            if not orders:
                return {
                    'success': True,
                    'message': 'No orders found to sync',
                    'total_processed': 0,
                    'total_created': 0,
                    'total_updated': 0,
                    'total_errors': 0,
                    'orders': [],
                    'errors': [],
                    'processed_at': datetime.now().isoformat()
                }
            
            # Extract order IDs
            order_ids = [str(order.get('id')) for order in orders]
            
            # Sync specific orders
            return self.sync_specific_orders(order_ids, original_request)
            
        except Exception as e:
            logger.exception("Error in full order sync")
            return {
                'success': False,
                'message': f'Full sync error: {str(e)}',
                'total_processed': 0,
                'total_created': 0,
                'total_updated': 0,
                'total_errors': 1,
                'orders': [],
                'errors': [str(e)],
                'processed_at': datetime.now().isoformat()
            }
    
    def sync_specific_orders(
        self,
        order_ids: List[str],
        original_request: Any = None,
        force_update: bool = False
    ) -> Dict[str, Any]:
        """
        Sync specific orders by their MercadoLibre IDs.
        
        Args:
            order_ids: List of MercadoLibre order IDs
            original_request: Original Django request for auth
            force_update: Whether to force update existing orders
            
        Returns:
            Dictionary with sync results
        """
        try:
            if not order_ids:
                return {
                    'success': False,
                    'message': 'No order IDs provided',
                    'total_processed': 0,
                    'total_created': 0,
                    'total_updated': 0,
                    'total_errors': 1,
                    'orders': [],
                    'errors': ['Order IDs list is empty'],
                    'processed_at': datetime.now().isoformat()
                }
            
            logger.info(f"Starting sync for {len(order_ids)} orders (force_update={force_update})")
            
            results = {
                'success': True,
                'message': '',
                'total_processed': 0,
                'total_created': 0,
                'total_updated': 0,
                'total_errors': 0,
                'orders': [],
                'errors': [],
                'processed_at': datetime.now().isoformat()
            }
            
            # Process orders in parallel
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                for order_id in order_ids:
                    future = executor.submit(
                        self._sync_single_order,
                        order_id,
                        original_request,
                        force_update
                    )
                    futures.append((order_id, future))
                
                # Collect results
                for order_id, future in futures:
                    try:
                        result = future.result()
                        results['orders'].append(result)
                        results['total_processed'] += 1
                        
                        if result['success']:
                            if result.get('action') == 'created':
                                results['total_created'] += 1
                            elif result.get('action') == 'updated':
                                results['total_updated'] += 1
                        else:
                            results['total_errors'] += 1
                            results['errors'].append(
                                f"Order {order_id}: {result.get('message', 'Unknown error')}"
                            )
                            
                    except Exception as e:
                        logger.exception(f"Error processing order {order_id}")
                        results['total_processed'] += 1
                        results['total_errors'] += 1
                        results['errors'].append(f"Order {order_id}: {str(e)}")
            
            # Update overall success status
            if results['total_errors'] == 0:
                results['message'] = f"All {results['total_processed']} orders synced successfully"
            elif results['total_errors'] < results['total_processed']:
                results['message'] = (
                    f"{results['total_processed'] - results['total_errors']} orders synced, "
                    f"{results['total_errors']} errors"
                )
            else:
                results['success'] = False
                results['message'] = f"All {results['total_errors']} orders failed to sync"
            
            return results
            
        except Exception as e:
            logger.exception("Error in specific order sync")
            return {
                'success': False,
                'message': f'Sync error: {str(e)}',
                'total_processed': 0,
                'total_created': 0,
                'total_updated': 0,
                'total_errors': len(order_ids) if order_ids else 1,
                'orders': [],
                'errors': [str(e)],
                'processed_at': datetime.now().isoformat()
            }
    
    def _sync_single_order(
        self,
        order_id: str,
        original_request: Any = None,
        force_update: bool = False
    ) -> Dict[str, Any]:
        """
        Sync a single order from MercadoLibre to WMS.
        
        Args:
            order_id: MercadoLibre order ID
            original_request: Original Django request for auth
            force_update: Whether to force update existing orders
            
        Returns:
            Dictionary with single order sync result
        """
        try:
            logger.info(f"Syncing order {order_id}")
            
            # Step 1: Get complete order from MercadoLibre
            order_data = self.meli.get_order(order_id)
            if not order_data:
                return {
                    'success': False,
                    'message': f'Order {order_id} not found in MercadoLibre',
                    'order_id': order_id,
                    'action': 'error'
                }
            
            # Step 2: Get buyer details (optional but recommended)
            buyer = order_data.get('buyer', {})
            buyer_id = buyer.get('id')
            buyer_data = None
            
            if buyer_id:
                try:
                    buyer_data = self.meli.get_customer(str(buyer_id))
                    logger.info(f"Got buyer data for order {order_id}")
                except Exception as e:
                    logger.warning(f"Could not get buyer data for order {order_id}: {e}")
            
            # Step 3: Map to WMS format using single mapper
            wms_order = OrderMapper.from_meli_order(order_data, buyer_data).to_dict()
            
            # Step 4: Create in WMS
            result = self._create_order_in_wms(wms_order, original_request)
            
            # Add metadata to result
            result['order_id'] = order_id
            result['ml_data'] = order_data
            result['wms_data'] = wms_order
            
            return result
            
        except Exception as e:
            logger.exception(f"Error syncing order {order_id}")
            return {
                'success': False,
                'message': f'Sync error: {str(e)}',
                'order_id': order_id,
                'action': 'error',
                'error': str(e)
            }
    
    def _create_order_in_wms(
        self,
        wms_order: Dict[str, Any],
        original_request: Any = None
    ) -> Dict[str, Any]:
        """Create order in WMS."""
        try:
            response = self.wms.post(
                self.ORDER_ENDPOINT,
                original_request=original_request,
                json=[wms_order]  # WMS expects array format
            )
            
            if response.status_code in (200, 201):
                wms_response = response.json()
                
                # Parse WMS response
                if isinstance(wms_response, dict):
                    created = wms_response.get('created', [])
                    errors = wms_response.get('errors', [])
                    
                    if created:
                        return {
                            'success': True,
                            'message': 'Order created successfully',
                            'action': 'created',
                            'wms_response': wms_response
                        }
                    elif errors:
                        return {
                            'success': False,
                            'message': f'WMS errors: {", ".join(errors)}',
                            'action': 'error',
                            'wms_response': wms_response
                        }
                    else:
                        return {
                            'success': True,
                            'message': 'Order processed by WMS',
                            'action': 'processed',
                            'wms_response': wms_response
                        }
                else:
                    return {
                        'success': True,
                        'message': 'Order created successfully',
                        'action': 'created',
                        'wms_response': wms_response
                    }
            else:
                return {
                    'success': False,
                    'message': f'WMS request failed: {response.status_code}',
                    'action': 'error',
                    'error': response.text[:200] if response.text else 'No details'
                }
                
        except Exception as e:
            logger.exception("Error creating order in WMS")
            return {
                'success': False,
                'message': f'WMS error: {str(e)}',
                'action': 'error',
                'error': str(e)
            }


# Singleton instance
_sync_service: Optional[MeliOrderSyncService] = None


def get_sync_service() -> MeliOrderSyncService:
    """Get or create order sync service singleton."""
    global _sync_service
    if _sync_service is None:
        _sync_service = MeliOrderSyncService()
    return _sync_service
