"""MercadoLibre synchronization views."""

import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

#from services.meli_wms_sync import get_sync_service
from mercadolibre.functions.Product.product_sync import get_sync_service
from mercadolibre.functions.Product.update import get_update_service
from mercadolibre.utils.response_helpers import get_response_status_code

import logging
logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class MeliProductSyncView(View):
    """
    Unified view for MercadoLibre product synchronization.
    
    Endpoints:
    - GET: Sync all products (creation mode)
    - POST with product_ids: Sync specific products (creation or update mode)
    - PUT with product_id: Update single product (update mode only)
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sync_service = get_sync_service()
        self.update_service = get_update_service()
    
    def get(self, request):
        """
        Sync all products from MercadoLibre to WMS (creation mode).
        
        Returns:
            JSON response with sync results
        """
        try:
            logger.info("Starting full product sync...")
            result = self.sync_service.sync_all_products(request)
            
            # Use utility functions for response handling
            status_code = get_response_status_code(result)
            return JsonResponse(result, status=status_code)
            
        except Exception as e:
            logger.exception("Error in full sync endpoint")
            return JsonResponse({
                'success': False,
                'message': f'Unexpected error: {str(e)}'
            }, status=500)
    
    def post(self, request):
        """
        Sync specific products from MercadoLibre to WMS.
        
        Expected body:
        {
            "product_ids": ["MLM123", "MLM456", ...],
            "force_update": true  // Optional, for forcing update mode
        }
        """
        try:
            data = json.loads(request.body)
            product_ids = data.get('product_ids', [])
            force_update = data.get('force_update', False)
            
            if not product_ids:
                return JsonResponse({
                    'success': False,
                    'message': 'No product_ids provided'
                }, status=400)
            
            logger.info(f"Starting sync for {len(product_ids)} products (force_update={force_update})...")
            result = self.sync_service.sync_specific_products(
                product_ids, 
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
            logger.exception("Error in specific sync endpoint")
            return JsonResponse({
                'success': False,
                'message': f'Unexpected error: {str(e)}'
            }, status=500)
    
    def put(self, request):
        """
        Update a single product in WMS (update mode only).
        
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
            
            logger.info(f"Updating product {product_id}...")
            result = self.update_service.update_single_product(product_id, request)
            
            # Use utility functions for response handling
            status_code = get_response_status_code(result)
            return JsonResponse(result, status=status_code)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON in request body'
            }, status=400)
        except Exception as e:
            logger.exception("Error in update endpoint")
            return JsonResponse({
                'success': False,
                'message': f'Unexpected error: {str(e)}'
            }, status=500)
