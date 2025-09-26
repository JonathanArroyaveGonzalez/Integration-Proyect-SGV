"""
Customer update service following the same architecture as products.
Handles individual customer update operations.
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from mercadolibre.services.meli_service import MeliService
from mercadolibre.services.internal_api_service import InternalAPIService
from mercadolibre.utils.mapper.data_mapper import CustomerMapper

logger = logging.getLogger(__name__)


class CustomerUpdateService:
    """Service for updating individual customers."""
    
    def __init__(self):
        """Initialize the customer update service."""
        self.meli = MeliService()
        self.wms = InternalAPIService()
        self.CUSTOMER_ENDPOINT = "/wms/adapter/v2/clt"
        
        logger.info("CustomerUpdateService initialized")
    
    def update_single_customer(
        self, 
        customer_id: str, 
        original_request: Any = None
    ) -> Dict[str, Any]:
        """
        Update a single customer from MercadoLibre to WMS.
        
        Args:
            customer_id: MercadoLibre customer ID
            original_request: Original Django request for auth
            
        Returns:
            Dictionary with update result using new structured format
        """
        try:
            logger.info(f"Starting update for customer {customer_id}")
            
            # Step 1: Get customer data from MercadoLibre
            customer_data = self._get_customer_from_meli(customer_id)
            if not customer_data:
                return self._build_final_response(
                    customer_id,
                    {
                        'success': False,
                        'status': 'not_found',
                        'message': f'Customer {customer_id} not found in MercadoLibre',
                        'action': 'error'
                    },
                    None
                )
            
            # Step 2: Map customer data to WMS format
            wms_customer = self._map_customer_to_wms(customer_data)
            if not wms_customer:
                return self._build_final_response(
                    customer_id,
                    {
                        'success': False,
                        'status': 'mapping_error',
                        'message': f'Failed to map customer {customer_id} to WMS format',
                        'action': 'error'
                    },
                    None
                )
            
            # Step 3: Update customer in WMS
            update_result = self._update_customer_in_wms(wms_customer, original_request)
            
            # Return structured response
            return self._build_final_response(customer_id, update_result, customer_data)
            
        except Exception as e:
            logger.exception(f"Error updating customer {customer_id}")
            return {
                'overall_success': False,
                'overall_status': 'error',
                'summary': f'Unexpected error occurred: {str(e)}',
                'customer_id': customer_id,
                'error_details': str(e),
                'updated_at': datetime.now().isoformat()
            }
    
    def _get_customer_from_meli(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get customer data from MercadoLibre."""
        try:
            response = self.meli.get(f'/users/{customer_id}')
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get customer {customer_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting customer {customer_id}: {e}")
            return None
    
    def _map_customer_to_wms(self, meli_customer: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Map MercadoLibre customer to WMS format."""
        try:
            mapper = CustomerMapper.from_meli_customer(meli_customer)
            return mapper.to_dict()
        except Exception as e:
            logger.error(f"Error mapping customer {meli_customer.get('id')}: {e}")
            return None
    
    def _update_customer_in_wms(
        self,
        wms_customer: Dict[str, Any],
        original_request: Any = None
    ) -> Dict[str, Any]:
        """
        Update customer in WMS.
        """
        try:
            # Customer ID is stored in 'item' field by CustomerMapper
            customer_id = wms_customer.get('item') or wms_customer.get('id') or wms_customer.get('customer_id')
            
            if not customer_id:
                logger.error(f"No customer ID found in WMS data. Available fields: {list(wms_customer.keys())}")
                return {
                    'success': False,
                    'status': 'invalid_data',
                    'message': 'Customer ID is required for WMS update',
                    'action': 'error'
                }
            
            logger.info(f"Updating customer in WMS: {customer_id}")
            
            # Try to update customer using PUT
            update_response = self.wms.put(
                self.CUSTOMER_ENDPOINT,
                original_request=original_request,
                json=wms_customer
            )
            
            if update_response.status_code in (200, 201):
                return {
                    'success': True,
                    'status': 'updated',
                    'message': 'Customer updated successfully',
                    'action': 'updated',
                    'wms_response': update_response.json() if update_response.text else {}
                }
            elif update_response.status_code == 404:
                # Customer doesn't exist - try to create it
                logger.info(f"Customer not found in WMS, creating: {customer_id}")
                return self._create_customer_in_wms(wms_customer, original_request)
            elif update_response.status_code == 400:
                error_text = update_response.text.lower()
                if 'already exists' in error_text:
                    return {
                        'success': True,
                        'status': 'exists',
                        'message': 'Customer already exists and is up to date',
                        'action': 'exists',
                        'wms_response': update_response.json() if update_response.text else {}
                    }
                else:
                    return {
                        'success': False,
                        'status': 'update_failed',
                        'message': f'Customer update failed: {update_response.text[:200]}',
                        'action': 'update_failed',
                        'error_details': update_response.text[:200] if update_response.text else 'No details'
                    }
            else:
                return {
                    'success': False,
                    'status': 'update_failed',
                    'message': f'Customer update failed: {update_response.status_code}',
                    'action': 'update_failed',
                    'error_details': update_response.text[:200] if update_response.text else 'No details'
                }
                
        except Exception as e:
            logger.exception("Error in WMS customer update operation")
            return {
                'success': False,
                'status': 'error',
                'message': f'WMS operation error: {str(e)}',
                'action': 'error',
                'error_details': str(e)
            }
    
    def _create_customer_in_wms(
        self,
        wms_customer: Dict[str, Any],
        original_request: Any = None
    ) -> Dict[str, Any]:
        """Create customer in WMS when update fails due to not found."""
        try:
            logger.info("Customer not found in WMS - creating via POST")
            
            create_response = self.wms.post(
                self.CUSTOMER_ENDPOINT,
                original_request=original_request,
                json=[wms_customer]  # WMS expects array format
            )
            
            if create_response.status_code in (200, 201):
                wms_response = create_response.json()
                
                # Parse WMS response format
                if isinstance(wms_response, dict):
                    created = wms_response.get('created', [])
                    errors = wms_response.get('errors', [])
                    
                    if created:
                        return {
                            'success': True,
                            'status': 'created',
                            'message': 'Customer created successfully (not found in WMS)',
                            'action': 'created',
                            'wms_response': wms_response
                        }
                    elif errors:
                        return {
                            'success': False,
                            'status': 'creation_failed',
                            'message': f'Customer creation failed: {", ".join(errors)}',
                            'action': 'creation_failed',
                            'error_details': ", ".join(errors)
                        }
                    else:
                        return {
                            'success': True,
                            'status': 'processed',
                            'message': 'Customer processed by WMS',
                            'action': 'processed',
                            'wms_response': wms_response
                        }
                else:
                    return {
                        'success': True,
                        'status': 'created',
                        'message': 'Customer created successfully',
                        'action': 'created',
                        'wms_response': wms_response
                    }
            elif create_response.status_code == 400 and 'already exists' in create_response.text.lower():
                return {
                    'success': True,
                    'status': 'exists',
                    'message': 'Customer already exists in WMS',
                    'action': 'exists',
                    'wms_response': create_response.json() if create_response.text else {}
                }
            else:
                return {
                    'success': False,
                    'status': 'creation_failed',
                    'message': f'Customer creation failed: {create_response.status_code}',
                    'action': 'creation_failed',
                    'error_details': create_response.text[:200] if create_response.text else 'No details'
                }
                
        except Exception as e:
            logger.exception("Error creating customer in WMS")
            return {
                'success': False,
                'status': 'error',
                'message': f'Customer creation error: {str(e)}',
                'action': 'error',
                'error_details': str(e)
            }
    
    def _build_final_response(
        self, 
        customer_id: str, 
        customer_result: Dict[str, Any], 
        ml_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build the final standardized response."""
        # Determine overall success and status
        customer_success = customer_result.get('success', False)
        customer_action = customer_result.get('action', 'unknown')
        
        # Overall success logic
        if customer_success:
            overall_success = True
            if customer_action in ['updated', 'created']:
                overall_status = "complete_success"
                summary = f"Customer {customer_action} successfully"
            elif customer_action == 'exists':
                overall_status = "already_synchronized"
                summary = "Customer already exists and is synchronized"
            else:
                overall_status = "complete_success"
                summary = f"Customer operation completed: {customer_result.get('message', '')}"
        else:
            overall_success = False
            overall_status = "complete_failure"
            summary = f"Customer operation failed: {customer_result.get('message', '')}"

        # Build changes summary
        changes_summary = {
            'customer_changed': customer_action in ['updated', 'created'],
            'synchronized': customer_action in ['exists', 'updated', 'created']
        }

        response = {
            'overall_success': overall_success,
            'overall_status': overall_status,
            'summary': summary,
            'customer_id': customer_id,
            'customer_operation': {
                'success': customer_success,
                'status': customer_action,
                'message': customer_result.get('message', ''),
                'details': {k: v for k, v in customer_result.items() 
                           if k not in ['success', 'message', 'action']}
            },
            'changes_summary': changes_summary,
            'ml_data': ml_data,
            'updated_at': datetime.now().isoformat()
        }

        return response


# Singleton instance
_update_service: Optional[CustomerUpdateService] = None


def get_customer_update_service() -> CustomerUpdateService:
    """Get or create customer update service singleton."""
    global _update_service
    if _update_service is None:
        _update_service = CustomerUpdateService()
    return _update_service


# Convenience functions for backward compatibility
def update_single_customer(customer_id: str, original_request: Any = None) -> Dict[str, Any]:
    """Update a single customer - convenience function."""
    service = get_customer_update_service()
    return service.update_single_customer(customer_id, original_request)