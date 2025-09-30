"""
Order update service for MercadoLibre.
Handles individual order update operations.
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from mercadolibre.services.meli_service import MeliService
from mercadolibre.services.internal_api_service import InternalAPIService
from mercadolibre.utils.mapper.data_mapper import OrderMapper

logger = logging.getLogger(__name__)


class OrderUpdateService:
    """Service for updating individual orders."""
    
    def __init__(self):
        """Initialize the order update service."""
        self.meli = MeliService()
        self.wms = InternalAPIService()
        self.ORDER_ENDPOINT = "/wms/adapter/v2/sale_order"
        
        logger.info("OrderUpdateService initialized")
    
    def update_single_order(
        self,
        order_id: str,
        original_request: Any = None
    ) -> Dict[str, Any]:
        """
        Update a single order from MercadoLibre to WMS.
        
        Args:
            order_id: MercadoLibre order ID
            original_request: Original Django request for auth
            
        Returns:
            Dictionary with update result using structured format
        """
        try:
            logger.info(f"Starting update for order {order_id}")
            
            # Step 1: Get complete order from MercadoLibre
            order_data = self.meli.get_order(order_id)
            if not order_data:
                return self._build_final_response(
                    order_id,
                    {
                        'success': False,
                        'status': 'not_found',
                        'message': f'Order {order_id} not found in MercadoLibre',
                        'action': 'error'
                    },
                    None
                )
            
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
            
            # Step 4: Update in WMS
            update_result = self._update_order_in_wms(wms_order, order_id, original_request)
            
            # Return structured response
            return self._build_final_response(order_id, update_result, order_data)
            
        except Exception as e:
            logger.exception(f"Error updating order {order_id}")
            return {
                'overall_success': False,
                'overall_status': 'error',
                'summary': f'Unexpected error occurred: {str(e)}',
                'order_id': order_id,
                'error_details': str(e),
                'updated_at': datetime.now().isoformat()
            }
    
    def _update_order_in_wms(
        self,
        wms_order: Dict[str, Any],
        order_id: str,
        original_request: Any = None
    ) -> Dict[str, Any]:
        """Update order in WMS."""
        try:
            # Get buyer ID for query parameter
            buyer_id = wms_order.get('item') or wms_order.get('nit')
            
            if not buyer_id:
                logger.error(f"No buyer ID found in WMS data for order {order_id}")
                return {
                    'success': False,
                    'status': 'invalid_data',
                    'message': 'Buyer ID is required for WMS update',
                    'action': 'error'
                }
            
            logger.info(f"Updating order in WMS: {order_id} (buyer: {buyer_id})")
            
            # Try to update order using PUT
            update_response = self.wms.put(
                f"{self.ORDER_ENDPOINT}?item={buyer_id}",
                original_request=original_request,
                json=wms_order
            )
            
            if update_response.status_code in (200, 201):
                return {
                    'success': True,
                    'status': 'updated',
                    'message': 'Order updated successfully',
                    'action': 'updated',
                    'wms_response': update_response.json() if update_response.text else {}
                }
            elif update_response.status_code == 404:
                # Order doesn't exist - try to create it
                logger.info(f"Order not found in WMS, creating: {order_id}")
                return self._create_order_in_wms(wms_order, original_request)
            elif update_response.status_code == 400:
                error_text = update_response.text.lower()
                if 'already exists' in error_text:
                    return {
                        'success': True,
                        'status': 'exists',
                        'message': 'Order already exists and is up to date',
                        'action': 'exists',
                        'wms_response': update_response.json() if update_response.text else {}
                    }
                else:
                    return {
                        'success': False,
                        'status': 'update_failed',
                        'message': f'Order update failed: {update_response.text[:200]}',
                        'action': 'update_failed',
                        'error_details': update_response.text[:200] if update_response.text else 'No details'
                    }
            else:
                return {
                    'success': False,
                    'status': 'update_failed',
                    'message': f'Order update failed: {update_response.status_code}',
                    'action': 'update_failed',
                    'error_details': update_response.text[:200] if update_response.text else 'No details'
                }
                
        except Exception as e:
            logger.exception("Error in WMS order update operation")
            return {
                'success': False,
                'status': 'error',
                'message': f'WMS operation error: {str(e)}',
                'action': 'error',
                'error_details': str(e)
            }
    
    def _create_order_in_wms(
        self,
        wms_order: Dict[str, Any],
        original_request: Any = None
    ) -> Dict[str, Any]:
        """Create order in WMS when update fails due to not found."""
        try:
            logger.info("Order not found in WMS - creating via POST")
            
            create_response = self.wms.post(
                self.ORDER_ENDPOINT,
                original_request=original_request,
                json=[wms_order]  # WMS expects array format
            )
            
            if create_response.status_code in (200, 201):
                wms_response = create_response.json()
                
                if isinstance(wms_response, dict):
                    created = wms_response.get('created', [])
                    errors = wms_response.get('errors', [])
                    
                    if created:
                        return {
                            'success': True,
                            'status': 'created',
                            'message': 'Order created successfully (not found in WMS)',
                            'action': 'created',
                            'wms_response': wms_response
                        }
                    elif errors:
                        return {
                            'success': False,
                            'status': 'creation_failed',
                            'message': f'Order creation failed: {", ".join(errors)}',
                            'action': 'creation_failed',
                            'error_details': ", ".join(errors)
                        }
                    else:
                        return {
                            'success': True,
                            'status': 'processed',
                            'message': 'Order processed by WMS',
                            'action': 'processed',
                            'wms_response': wms_response
                        }
                else:
                    return {
                        'success': True,
                        'status': 'created',
                        'message': 'Order created successfully',
                        'action': 'created',
                        'wms_response': wms_response
                    }
            elif create_response.status_code == 400 and 'already exists' in create_response.text.lower():
                return {
                    'success': True,
                    'status': 'exists',
                    'message': 'Order already exists in WMS',
                    'action': 'exists',
                    'wms_response': create_response.json() if create_response.text else {}
                }
            else:
                return {
                    'success': False,
                    'status': 'creation_failed',
                    'message': f'Order creation failed: {create_response.status_code}',
                    'action': 'creation_failed',
                    'error_details': create_response.text[:200] if create_response.text else 'No details'
                }
                
        except Exception as e:
            logger.exception("Error creating order in WMS")
            return {
                'success': False,
                'status': 'error',
                'message': f'Order creation error: {str(e)}',
                'action': 'error',
                'error_details': str(e)
            }
    
    def _build_final_response(
        self,
        order_id: str,
        order_result: Dict[str, Any],
        ml_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build the final standardized response."""
        order_success = order_result.get('success', False)
        order_action = order_result.get('action', 'unknown')
        
        if order_success:
            overall_success = True
            if order_action in ['updated', 'created']:
                overall_status = "complete_success"
                summary = f"Order {order_action} successfully"
            elif order_action == 'exists':
                overall_status = "already_synchronized"
                summary = "Order already exists and is synchronized"
            else:
                overall_status = "complete_success"
                summary = f"Order operation completed: {order_result.get('message', '')}"
        else:
            overall_success = False
            overall_status = "complete_failure"
            summary = f"Order operation failed: {order_result.get('message', '')}"

        changes_summary = {
            'order_changed': order_action in ['updated', 'created'],
            'synchronized': order_action in ['exists', 'updated', 'created']
        }

        return {
            'overall_success': overall_success,
            'overall_status': overall_status,
            'summary': summary,
            'order_id': order_id,
            'order_operation': {
                'success': order_success,
                'status': order_action,
                'message': order_result.get('message', ''),
                'details': {k: v for k, v in order_result.items() 
                           if k not in ['success', 'message', 'action']}
            },
            'changes_summary': changes_summary,
            'ml_data': ml_data,
            'updated_at': datetime.now().isoformat()
        }


# Singleton instance
_update_service: Optional[OrderUpdateService] = None


def get_update_service() -> OrderUpdateService:
    """Get or create order update service singleton."""
    global _update_service
    if _update_service is None:
        _update_service = OrderUpdateService()
    return _update_service
