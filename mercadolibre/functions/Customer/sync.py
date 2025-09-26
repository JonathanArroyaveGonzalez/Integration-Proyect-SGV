"""
Customer synchronization service following the same architecture as products.
Handles customer sync operations from MercadoLibre to WMS.
"""
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor
from mercadolibre.services.meli_service import MeliService
from mercadolibre.services.internal_api_service import InternalAPIService
from mercadolibre.utils.mapper.data_mapper import CustomerMapper

logger = logging.getLogger(__name__)


class MeliCustomerSyncService:
    """Service for synchronizing customers from MercadoLibre to WMS."""
    
    def __init__(self):
        """Initialize the customer sync service."""
        self.meli = MeliService()
        self.wms = InternalAPIService()
        self.CUSTOMER_ENDPOINT = "/wms/adapter/v2/clt"
        
        logger.info("CustomerSyncService initialized")
    
    def sync_all_customers(self, original_request: Any = None) -> Dict[str, Any]:
        """
        Sync all available customers from MercadoLibre to WMS.
        This is a placeholder - actual implementation would need ML customer listing API.
        
        Args:
            original_request: Original Django request for auth
            
        Returns:
            Dictionary with sync results
        """
        try:
            logger.info("Starting full customer synchronization...")
            
            # Note: MercadoLibre doesn't provide a direct way to list all customers
            # This would typically be based on orders/transactions or specific business logic
            
            return {
                'success': True,
                'message': 'Full customer sync not implemented - customers are synced on-demand',
                'total_processed': 0,
                'total_created': 0,
                'total_updated': 0,
                'total_errors': 0,
                'customers': [],
                'errors': [],
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.exception("Error in full customer sync")
            return {
                'success': False,
                'message': f'Full sync error: {str(e)}',
                'total_processed': 0,
                'total_created': 0,
                'total_updated': 0,
                'total_errors': 1,
                'customers': [],
                'errors': [str(e)],
                'processed_at': datetime.now().isoformat()
            }
    
    def sync_specific_customers(
        self,
        customer_ids: List[str],
        original_request: Any = None,
        force_update: bool = False
    ) -> Dict[str, Any]:
        """
        Sync specific customers by their MercadoLibre IDs.
        
        Args:
            customer_ids: List of MercadoLibre customer IDs
            original_request: Original Django request for auth
            force_update: Whether to force update existing customers
            
        Returns:
            Dictionary with sync results
        """
        try:
            if not customer_ids:
                return {
                    'success': False,
                    'message': 'No customer IDs provided',
                    'total_processed': 0,
                    'total_created': 0,
                    'total_updated': 0,
                    'total_errors': 1,
                    'customers': [],
                    'errors': ['Customer IDs list is empty'],
                    'processed_at': datetime.now().isoformat()
                }
            
            logger.info(f"Starting sync for {len(customer_ids)} customers (force_update={force_update})")
            
            results = {
                'success': True,
                'message': '',
                'total_processed': 0,
                'total_created': 0,
                'total_updated': 0,
                'total_errors': 0,
                'customers': [],
                'errors': [],
                'processed_at': datetime.now().isoformat()
            }
            
            # Process customers in parallel
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                for customer_id in customer_ids:
                    future = executor.submit(
                        self._sync_single_customer,
                        customer_id,
                        original_request,
                        force_update
                    )
                    futures.append((customer_id, future))
                
                # Collect results
                for customer_id, future in futures:
                    try:
                        result = future.result()
                        results['customers'].append(result)
                        results['total_processed'] += 1
                        
                        if result['success']:
                            if result.get('action') == 'created':
                                results['total_created'] += 1
                            elif result.get('action') == 'updated':
                                results['total_updated'] += 1
                        else:
                            results['total_errors'] += 1
                            results['errors'].append(f"Customer {customer_id}: {result.get('message', 'Unknown error')}")
                            
                    except Exception as e:
                        logger.exception(f"Error processing customer {customer_id}")
                        results['total_processed'] += 1
                        results['total_errors'] += 1
                        results['errors'].append(f"Customer {customer_id}: {str(e)}")
            
            # Update overall success status
            if results['total_errors'] == 0:
                results['message'] = f"All {results['total_processed']} customers synced successfully"
            elif results['total_errors'] < results['total_processed']:
                results['message'] = f"{results['total_processed'] - results['total_errors']} customers synced, {results['total_errors']} errors"
            else:
                results['success'] = False
                results['message'] = f"All {results['total_errors']} customers failed to sync"
            
            return results
            
        except Exception as e:
            logger.exception("Error in specific customer sync")
            return {
                'success': False,
                'message': f'Sync error: {str(e)}',
                'total_processed': 0,
                'total_created': 0,
                'total_updated': 0,
                'total_errors': len(customer_ids) if customer_ids else 1,
                'customers': [],
                'errors': [str(e)],
                'processed_at': datetime.now().isoformat()
            }
    
    def _sync_single_customer(
        self,
        customer_id: str,
        original_request: Any = None,
        force_update: bool = False
    ) -> Dict[str, Any]:
        """
        Sync a single customer from MercadoLibre to WMS.
        
        Args:
            customer_id: MercadoLibre customer ID
            original_request: Original Django request for auth
            force_update: Whether to force update existing customers
            
        Returns:
            Dictionary with single customer sync result
        """
        try:
            logger.info(f"Syncing customer {customer_id} (force_update={force_update})")
            
            # Step 1: Get customer data from MercadoLibre
            customer_data = self._get_customer_from_meli(customer_id)
            if not customer_data:
                return {
                    'success': False,
                    'message': f'Customer {customer_id} not found in MercadoLibre',
                    'customer_id': customer_id,
                    'action': 'error'
                }
            
            # Step 2: Map customer data to WMS format
            wms_customer = self._map_customer_to_wms(customer_data)
            if not wms_customer:
                return {
                    'success': False,
                    'message': f'Failed to map customer {customer_id} to WMS format',
                    'customer_id': customer_id,
                    'action': 'error'
                }
            
            # Step 3: Create/update customer in WMS
            result = self._create_customer_in_wms(wms_customer, original_request)
            
            # Add customer ID to result
            result['customer_id'] = customer_id
            result['ml_data'] = customer_data
            result['wms_data'] = wms_customer
            
            return result
            
        except Exception as e:
            logger.exception(f"Error syncing customer {customer_id}")
            return {
                'success': False,
                'message': f'Sync error: {str(e)}',
                'customer_id': customer_id,
                'action': 'error',
                'error': str(e)
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
    
    def _create_customer_in_wms(
        self,
        wms_customer: Dict[str, Any],
        original_request: Any = None
    ) -> Dict[str, Any]:
        """Create customer in WMS."""
        try:
            response = self.wms.post(
                self.CUSTOMER_ENDPOINT,
                original_request=original_request,
                json=[wms_customer]  # WMS expects array format
            )
            
            if response.status_code in (200, 201):
                wms_response = response.json()
                
                # Parse WMS response format
                if isinstance(wms_response, dict):
                    created = wms_response.get('created', [])
                    errors = wms_response.get('errors', [])
                    
                    if created:
                        return {
                            'success': True,
                            'message': 'Customer created successfully',
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
                            'message': 'Customer processed by WMS',
                            'action': 'processed',
                            'wms_response': wms_response
                        }
                else:
                    return {
                        'success': True,
                        'message': 'Customer created successfully',
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
            logger.exception("Error creating customer in WMS")
            return {
                'success': False,
                'message': f'WMS error: {str(e)}',
                'action': 'error',
                'error': str(e)
            }


# Singleton instance
_sync_service: Optional[MeliCustomerSyncService] = None


def get_customer_sync_service() -> MeliCustomerSyncService:
    """Get or create customer sync service singleton."""
    global _sync_service
    if _sync_service is None:
        _sync_service = MeliCustomerSyncService()
    return _sync_service


# Convenience functions for backward compatibility
def sync_customers(customer_ids: List[str], original_request: Any = None) -> Dict[str, Any]:
    """Sync customers - convenience function."""
    service = get_customer_sync_service()
    return service.sync_specific_customers(customer_ids, original_request)