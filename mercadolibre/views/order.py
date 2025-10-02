"""MercadoLibre order synchronization views."""

import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from mercadolibre.functions.Order.create import get_sync_service
from mercadolibre.functions.Order.update import get_update_service
from mercadolibre.utils.response_helpers import get_response_status_code

import logging
logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class MeliOrderSyncView(View):
    """
    Unified view for MercadoLibre order synchronization.
    
    Endpoints:
    - GET: Sync recent orders (creation mode)
    - POST with order_ids: Sync specific orders (creation or update mode)
    - PUT with order_id: Update single order (update mode only)
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sync_service = get_sync_service()
        self.update_service = get_update_service()
    
    def get(self, request):
        """
        Sync recent orders from MercadoLibre to WMS (creation mode).
        
        Query parameters:
            status: Optional order status filter (paid, cancelled, etc.)
            limit: Maximum number of orders to sync (default: 50)
        
        Returns:
            JSON response with sync results
        """
        try:
            status = request.GET.get('status')
            limit = int(request.GET.get('limit', 50))
            
            logger.info(f"Starting order sync (status={status}, limit={limit})...")
            result = self.sync_service.sync_all_orders(request, status, limit)
            
            # Use utility functions for response handling
            status_code = get_response_status_code(result)
            return JsonResponse(result, status=status_code)
            
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'message': f'Invalid limit parameter: {str(e)}'
            }, status=400)
        except Exception as e:
            logger.exception("Error in order sync endpoint")
            return JsonResponse({
                'success': False,
                'message': f'Unexpected error: {str(e)}'
            }, status=500)
    
    def post(self, request):
        """
        Sync specific orders from MercadoLibre to WMS.
        
        Expected body:
        {
            "order_ids": ["2000001234", "2000001235", ...],
            "force_update": true  // Optional, for forcing update mode
        }
        """
        try:
            data = json.loads(request.body)
            order_ids = data.get('order_ids', [])
            force_update = data.get('force_update', False)
            
            if not order_ids:
                return JsonResponse({
                    'success': False,
                    'message': 'No order_ids provided'
                }, status=400)
            
            logger.info(f"Starting sync for {len(order_ids)} orders (force_update={force_update})...")
            result = self.sync_service.sync_specific_orders(
                order_ids,
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
            logger.exception("Error in specific order sync endpoint")
            return JsonResponse({
                'success': False,
                'message': f'Unexpected error: {str(e)}'
            }, status=500)
    
    def put(self, request):
        """
        Update a single order in WMS (update mode only).
        
        Expected body:
        {
            "order_id": "2000001234"
        }
        
        Returns:
            JSON response with update results
        """
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            
            if not order_id:
                return JsonResponse({
                    'success': False,
                    'message': 'No order_id provided'
                }, status=400)
            
            logger.info(f"Updating order {order_id}...")
            result = self.update_service.update_single_order(order_id, request)
            
            # Use utility functions for response handling
            status_code = get_response_status_code(result)
            return JsonResponse(result, status=status_code)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON in request body'
            }, status=400)
        except Exception as e:
            logger.exception("Error in order update endpoint")
            return JsonResponse({
                'success': False,
                'message': f'Unexpected error: {str(e)}'
            }, status=500)
