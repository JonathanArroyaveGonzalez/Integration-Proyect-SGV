"""MercadoLibre inventory synchronization views."""

import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from mercadolibre.functions.Inventory.create import get_create_service
from mercadolibre.functions.Inventory.update import get_update_service
from mercadolibre.utils.response_helpers import get_response_status_code

import logging
logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class MeliInventoryView(View):
    """
    View for MercadoLibre inventory management.
    
    Endpoints:
    - POST with product_id: Create inventory for a product
    - PUT with product_id: Update inventory for a product
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_service = get_create_service()
        self.update_service = get_update_service()
    
    def post(self, request):
        """
        Create inventory for a product in WMS.
        
        Expected body:
        {
            "product_id": "MLM123"
        }
        
        Returns:
            JSON response with creation results
        """
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            
            if not product_id:
                return JsonResponse({
                    'success': False,
                    'message': 'No product_id provided'
                }, status=400)
            
            logger.info(f"Creating inventory for product {product_id}...")
            result = self.create_service.create_inventory(product_id, request)
            
            # Use utility functions for response handling
            status_code = get_response_status_code(result)
            return JsonResponse(result, status=status_code)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON in request body'
            }, status=400)
        except Exception as e:
            logger.exception("Error in inventory creation endpoint")
            return JsonResponse({
                'success': False,
                'message': f'Unexpected error: {str(e)}'
            }, status=500)
    
    def put(self, request):
        """
        Update inventory for a product in WMS.
        
        Expected body:
        {
            "product_id": "MLM123"
        }
        
        Returns:
            JSON response with update results
        """
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            
            if not product_id:
                return JsonResponse({
                    'success': False,
                    'message': 'No product_id provided'
                }, status=400)
            
            logger.info(f"Updating inventory for product {product_id}...")
            result = self.update_service.update_inventory(product_id, request)
            
            # Use utility functions for response handling
            status_code = get_response_status_code(result)
            return JsonResponse(result, status=status_code)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON in request body'
            }, status=400)
        except Exception as e:
            logger.exception("Error in inventory update endpoint")
            return JsonResponse({
                'success': False,
                'message': f'Unexpected error: {str(e)}'
            }, status=500)
