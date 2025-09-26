"""MercadoLibre customer synchronization views - Unified architecture."""

import json
import logging
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from mercadolibre.functions.Customer.sync import get_customer_sync_service
from mercadolibre.functions.Customer.update import get_customer_update_service
from mercadolibre.utils.response_helpers import get_response_status_code

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class MeliCustomerSyncView(View):
    """
    Unified view for customer synchronization operations.
    Only handles specific customer sync (POST) and updates (PUT).
    No full sync functionality - that's only for products.
    """
    
    def __init__(self):
        super().__init__()
        self.sync_service = get_customer_sync_service()
        self.update_service = get_customer_update_service()
    
    def post(self, request):
        """
        Sync specific customers by their MercadoLibre IDs.
        
        Expected JSON format:
        {
            "customer_ids": ["123", "456"],  // Required: List of ML customer IDs
            "force_update": false           // Optional: Force update existing customers
        }
        
        Returns:
            JSON response with sync results
        """
        try:
            data = json.loads(request.body)
            customer_ids = data.get('customer_ids', [])
            force_update = data.get('force_update', False)
            
            if not customer_ids:
                return JsonResponse({
                    'success': False,
                    'message': 'No customer_ids provided'
                }, status=400)
            
            if not isinstance(customer_ids, list):
                return JsonResponse({
                    'success': False,
                    'message': 'customer_ids must be a list'
                }, status=400)
            
            logger.info(f"Starting sync for {len(customer_ids)} customers (force_update={force_update})...")
            result = self.sync_service.sync_specific_customers(
                customer_ids, 
                request,
                force_update=force_update
            )
            
            # Use utility functions for response handling
            status_code = get_response_status_code(result)
            return JsonResponse(result, status=status_code)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON in request body'
            }, status=400)
        except Exception as e:
            logger.exception("Error in specific customer sync endpoint")
            return JsonResponse({
                'success': False,
                'message': f'Sync error: {str(e)}',
                'error': str(e)
            }, status=500)
    
    def put(self, request):
        """
        Update a single customer from MercadoLibre to WMS.
        
        Expected JSON format:
        {
            "customer_id": "123"  // Required: ML customer ID
        }
        
        Returns:
            JSON response with update results
        """
        try:
            data = json.loads(request.body)
            customer_id = data.get('customer_id')
            
            if not customer_id:
                return JsonResponse({
                    'success': False,
                    'message': 'No customer_id provided'
                }, status=400)
            
            # Ensure customer_id is a string, not a list
            if isinstance(customer_id, list):
                if len(customer_id) == 1:
                    customer_id = customer_id[0]
                    logger.warning(f"customer_id was provided as list, extracting single value: {customer_id}")
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'customer_id should be a single string, not a list'
                    }, status=400)
            
            customer_id = str(customer_id)  # Ensure it's a string
            
            logger.info(f"Updating customer {customer_id}...")
            result = self.update_service.update_single_customer(customer_id, request)
            
            # Use utility functions for response handling
            status_code = get_response_status_code(result)
            return JsonResponse(result, status=status_code)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON in request body'
            }, status=400)
        except Exception as e:
            logger.exception("Error in customer update endpoint")
            return JsonResponse({
                'success': False,
                'message': f'Unexpected error: {str(e)}'
            }, status=500)