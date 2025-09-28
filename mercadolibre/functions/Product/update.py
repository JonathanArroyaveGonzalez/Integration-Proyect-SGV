"""Product and Barcode Update Operations."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from mercadolibre.services.meli_service import get_meli_service
from mercadolibre.services.internal_api_service import get_internal_api_service
from mercadolibre.utils.mapper.data_mapper import ProductMapper, BarCodeMapper

logger = logging.getLogger(__name__)


class ProductUpdateService:
    """Service for updating individual products and barcodes."""
    
    # Endpoints
    PRODUCT_ENDPOINT = 'wms/adapter/v2/art'
    BARCODE_ENDPOINT = 'wms/base/v2/tRelacionCodbarras'
    
    def __init__(self):
        """Initialize update service with required services."""
        self.meli = get_meli_service()
        self.wms = get_internal_api_service()

    
    def update_single_product(
        self,
        product_id: str,
        original_request: Any = None
    ) -> Dict[str, Any]:
        """
        Update a single product in WMS.
        Always fetches fresh data from MercadoLibre and updates in WMS.
        
        Args:
            product_id: MercadoLibre Product ID to update
            original_request: Original Django request for auth
            
        Returns:
            Update result
        """
        try:
            logger.info(f"Starting update for product {product_id}...")
            
            # Step 1: Get fresh product detail from MercadoLibre
            logger.info(f"Fetching product {product_id} from MercadoLibre...")
            meli_item = self._get_product_detail(product_id)
            
            if not meli_item:
                return {
                    'success': False,
                    'message': f'Product {product_id} not found in MercadoLibre',
                    'product_id': product_id
                }
            
            # Step 2: Map product to WMS format
            logger.info(f"Mapping product {product_id} to WMS format...")
            wms_product = self._map_product_to_wms(meli_item)
            
            if not wms_product:
                return {
                    'success': False,
                    'message': 'Could not map product to WMS format',
                    'product_id': product_id
                }
            
            product_ean = wms_product.get('productoean')
            if not product_ean:
                return {
                    'success': False,
                    'message': 'Product EAN not found in mapped data',
                    'product_id': product_id
                }
            
            logger.info(f"Product EAN: {product_ean}")
            
            # Step 3: Update product in WMS using new reference-based logic
            logger.info(f"Updating product {product_ean} (reference: {wms_product.get('referencia')}) in WMS using reference-based search...")
            product_result = self._update_product_in_wms(wms_product, original_request)
            
            # Step 4: Update barcode with optimized logic
            barcode_result = {'success': False, 'message': 'Barcode not processed'}
            
            if product_result['success'] or product_result.get('action') in ['exists', 'already_synchronized']:
                logger.info(f"Processing optimized barcode update for product {product_ean}...")
                
                # Pass product information to barcode update for optimized processing
                barcode_result = self.update_single_barcode_with_product_info(
                    meli_item, 
                    product_result.get('existing_product'),
                    product_result.get('ean_changed', False),
                    product_result.get('previous_ean'),
                    original_request
                )
                
                # Log EAN change if detected
                if barcode_result.get('ean_change'):
                    logger.info(f"EAN change detected and handled: {barcode_result.get('previous_ean')} → {barcode_result.get('new_ean')}")
                elif barcode_result.get('action') == 'already_synchronized':
                    logger.info("Barcode already synchronized - no update needed")
            else:
                logger.warning(f"Skipping barcode update due to product operation failure: {product_result.get('message')}")

            # Return structured response
            return self._build_final_response(product_id, product_ean, product_result, barcode_result)
            
        except Exception as e:
            logger.exception(f"Error updating product {product_id}")
            return {
                'overall_success': False,
                'overall_status': 'error',
                'summary': f'Unexpected error occurred: {str(e)}',
                'product_id': product_id,
                'error_details': str(e),
                'updated_at': datetime.now().isoformat()
            }
    
    def update_single_barcode(
        self,
        meli_item: Dict[str, Any],
        original_request: Any = None
    ) -> Dict[str, Any]:
        """
        Update a single barcode in WMS with intelligent EAN change handling.
        
        Args:
            meli_item: MercadoLibre item data
            original_request: Original Django request for auth
            
        Returns:
            Update result
        """
        try:
            # Extract barcode data from MercadoLibre item
            barcode_mapper = BarCodeMapper.from_meli_item(meli_item)
            
            if not barcode_mapper:
                return {
                    'success': False,
                    'message': 'No barcode/EAN found in MercadoLibre product'
                }
            
            barcode_data = barcode_mapper.to_dict()
            current_ean = barcode_data.get('codbarrasasignado')
            product_reference = barcode_data.get('idinternoean')  # This is usually the product reference/ID
            
            logger.info(f"Processing barcode - Current EAN: {current_ean}, Reference: {product_reference}")
            
            # Step 1: Get previous product data from the product update result
            # The product update should have already provided us this information
            existing_product = None
            ean_changed = False
            previous_ean = None
            
            # Try to get existing product info from MercadoLibre item or by reference
            if product_reference:
                existing_product = self._get_product_from_wms_by_reference(
                    product_reference, 
                    original_request
                )
            
            # Step 2: Detect if EAN has changed
            if existing_product:
                previous_ean = existing_product.get('productoean')
                ean_changed = previous_ean and previous_ean != current_ean
                
                logger.info(f"Barcode analysis - Current: {current_ean}, Previous: {previous_ean}, Changed: {ean_changed}")
            
            if ean_changed and previous_ean:
                # EAN has changed - handle barcode change properly
                logger.info(f"EAN change detected for reference {product_reference}: {previous_ean} → {current_ean}")
                
                # Step 1: Create the barcode relationship (previous_ean -> current_ean)
                relationship_result = self._create_barcode_relationship(
                    previous_ean,
                    current_ean,
                    original_request
                )
                
                # Step 2: Try to update the existing barcode record using the PREVIOUS EAN
                # The existing barcode record should have idinternoean = previous_ean
                logger.info(f"Attempting to update existing barcode record with previous EAN: {previous_ean}")
                
                # Prepare barcode data with the NEW EAN as the assigned code
                update_barcode_data = {
                    'idinternoean': previous_ean,  # Use previous EAN to find existing record
                    'codbarrasasignado': current_ean,  # Update to new EAN
                    'cantidad': barcode_data.get('cantidad', 1)
                }
                
                barcode_response = self.wms.put(
                    self.BARCODE_ENDPOINT,
                    original_request=original_request,
                    params={'idinternoean': previous_ean},  # Search by previous EAN
                    json=update_barcode_data
                )
                
                # Step 3: If updating existing record fails, try creating new one
                if barcode_response.status_code not in (200, 201):
                    logger.info(f"Updating existing barcode failed ({barcode_response.status_code}), trying to create new barcode record")
                    
                    # Create new barcode record with current EAN
                    new_barcode_data = {
                        'idinternoean': current_ean,
                        'codbarrasasignado': current_ean,
                        'cantidad': barcode_data.get('cantidad', 1)
                    }
                    
                    create_barcode_response = self.wms.post(
                        self.BARCODE_ENDPOINT,
                        original_request=original_request,
                        json=new_barcode_data
                    )
                    
                    barcode_success = create_barcode_response.status_code in (200, 201)
                    barcode_action = 'created_new' if barcode_success else 'failed'
                    barcode_message = f"New barcode created: {create_barcode_response.status_code}" if barcode_success else f"Barcode creation failed: {create_barcode_response.status_code}"
                else:
                    barcode_success = True
                    barcode_action = 'updated_existing'
                    barcode_message = f"Existing barcode updated: {barcode_response.status_code}"
                
                # Combine results
                if relationship_result['success']:
                    return {
                        'success': True,  # Success if relationship was created
                        'message': f"EAN change handled: {relationship_result['message']}. {barcode_message}",
                        'action': f'ean_change_{barcode_action}',
                        'ean_change': True,
                        'previous_ean': previous_ean,
                        'new_ean': current_ean,
                        'relationship_result': relationship_result,
                        'barcode_success': barcode_success
                    }
                else:
                    return {
                        'success': False,
                        'message': f"Failed to handle EAN change: {relationship_result['message']}",
                        'action': 'ean_change_failed',
                        'ean_change': True,
                        'previous_ean': previous_ean,
                        'new_ean': current_ean,
                        'relationship_result': relationship_result
                    }
            
            else:
                # No EAN change - standard barcode update
                logger.info("No EAN change detected - performing standard barcode update")
                
                update_barcode_data = {
                    k: v for k, v in barcode_data.items() if v is not None
                }

                # Attempt to update barcode
                barcode_response = self.wms.put(
                    self.BARCODE_ENDPOINT,
                    original_request=original_request,
                    params={'idinternoean': barcode_data['idinternoean']},
                    json=update_barcode_data
                )
                
                if barcode_response.status_code in (200, 201):
                    return {
                        'success': True,
                        'message': 'Barcode updated successfully',
                        'barcode': barcode_data['codbarrasasignado'],
                        'action': 'updated',
                        'ean_change': False
                    }
                elif barcode_response.status_code == 404:
                    # Try to create the barcode instead
                    create_response = self.wms.post(
                        self.BARCODE_ENDPOINT,
                        original_request=original_request,
                        json=update_barcode_data
                    )
                    
                    if create_response.status_code in (200, 201):
                        return {
                            'success': True,
                            'message': 'Barcode created successfully (not found for update)',
                            'barcode': barcode_data['codbarrasasignado'],
                            'action': 'created',
                            'ean_change': False
                        }
                    else:
                        return {
                            'success': False,
                            'message': f'Barcode creation failed: {create_response.status_code}',
                            'error': create_response.text[:200] if create_response.text else 'No details',
                            'action': 'failed',
                            'ean_change': False
                        }
                        
                elif barcode_response.status_code == 400 and 'already exists' in barcode_response.text.lower():
                    return {
                        'success': True,
                        'message': 'Barcode already exists and up to date',
                        'barcode': barcode_data['codbarrasasignado'],
                        'action': 'exists',
                        'ean_change': False
                    }
                else:
                    return {
                        'success': False,
                        'message': f'Barcode update failed: {barcode_response.status_code}',
                        'error': barcode_response.text[:200] if barcode_response.text else 'No details',
                        'action': 'failed',
                        'ean_change': False
                    }
                
        except Exception as e:
            logger.exception("Error updating barcode")
            return {
                'success': False,
                'message': f'Error updating barcode: {str(e)}',
                'ean_change': False
            }
    
    def update_single_barcode_with_product_info(
        self,
        meli_item: Dict[str, Any],
        existing_product: Optional[Dict[str, Any]] = None,
        ean_changed: bool = False,
        previous_ean: Optional[str] = None,
        original_request: Any = None
    ) -> Dict[str, Any]:
        """
        Update barcode with product information already determined.
        This is more efficient than re-discovering product info.
        """
        try:
            # Extract barcode data from MercadoLibre item
            barcode_mapper = BarCodeMapper.from_meli_item(meli_item)
            
            if not barcode_mapper:
                return {
                    'success': False,
                    'message': 'No barcode/EAN found in MercadoLibre product'
                }
            
            barcode_data = barcode_mapper.to_dict()
            current_ean = barcode_data.get('codbarrasasignado')
            
            logger.info(f"Processing barcode with product info - Current EAN: {current_ean}, EAN changed: {ean_changed}, Previous: {previous_ean}")
            
            if ean_changed and previous_ean:
                # EAN has changed - handle barcode change using provided info
                logger.info(f"EAN change detected: {previous_ean} → {current_ean}")
                
                # Step 1: Create the barcode relationship
                relationship_result = self._create_barcode_relationship(
                    previous_ean,
                    current_ean,
                    original_request
                )
                
                # Step 2: Try to update existing barcode record using previous EAN
                logger.info(f"Updating existing barcode record with previous EAN: {previous_ean}")
                
                update_barcode_data = {
                    'idinternoean': previous_ean,
                    'codbarrasasignado': current_ean,
                    'cantidad': barcode_data.get('cantidad', 1)
                }
                
                barcode_response = self.wms.put(
                    self.BARCODE_ENDPOINT,
                    original_request=original_request,
                    params={'idinternoean': previous_ean},
                    json=update_barcode_data
                )
                
                # Step 3: If updating fails, try creating new record
                if barcode_response.status_code not in (200, 201):
                    logger.info("Updating existing barcode failed, creating new barcode record")
                    
                    new_barcode_data = {
                        'idinternoean': current_ean,
                        'codbarrasasignado': current_ean,
                        'cantidad': barcode_data.get('cantidad', 1)
                    }
                    
                    create_response = self.wms.post(
                        self.BARCODE_ENDPOINT,
                        original_request=original_request,
                        json=new_barcode_data
                    )
                    
                    barcode_success = create_response.status_code in (200, 201)
                    if barcode_success:
                        barcode_message = f"New barcode created successfully (status: {create_response.status_code})"
                        error_details = None
                    else:
                        error_details = create_response.text[:200] if create_response.text else f'HTTP {create_response.status_code}'
                        barcode_message = f"Failed to create barcode (status: {create_response.status_code})"
                else:
                    barcode_success = True
                    barcode_message = f"Existing barcode updated successfully (status: {barcode_response.status_code})"
                    error_details = None
                
                return {
                    'success': relationship_result['success'] and barcode_success,
                    'message': f"EAN change handled: {relationship_result['message']}. {barcode_message}",
                    'action': 'ean_change_handled',
                    'ean_change': True,
                    'previous_ean': previous_ean,
                    'new_ean': current_ean,
                    'relationship_result': relationship_result,
                    'error_details': error_details,
                    'status_code': create_response.status_code if 'create_response' in locals() else barcode_response.status_code
                }
                
            else:
                # No EAN change - intelligent barcode handling
                logger.info("No EAN change - checking barcode existence and needs")
                
                # Check if barcode exists in WMS
                barcode_check = self._barcode_exists_in_wms(
                    barcode_data['idinternoean'], 
                    original_request
                )
                
                if barcode_check['exists']:
                    # Barcode exists - check if it needs updating or is already synchronized
                    logger.info(f"Barcode exists in WMS: {barcode_data['idinternoean']}")
                    
                    # For now, assume existing barcode is synchronized
                    # Future enhancement: compare barcode data for changes
                    return {
                        'success': True,
                        'message': 'Barcode already exists and is synchronized',
                        'barcode': barcode_data['codbarrasasignado'],
                        'action': 'already_synchronized',
                        'ean_change': False,
                        'existing_barcode': barcode_check['barcode_data']
                    }
                else:
                    # Barcode doesn't exist - create it
                    logger.info(f"Barcode doesn't exist in WMS - creating: {barcode_data['idinternoean']}")
                    
                    update_barcode_data = {
                        k: v for k, v in barcode_data.items() if v is not None
                    }
                    
                    create_response = self.wms.post(
                        self.BARCODE_ENDPOINT,
                        original_request=original_request,
                        json=update_barcode_data
                    )
                    
                    if create_response.status_code in (200, 201):
                        return {
                            'success': True,
                            'message': 'Barcode created successfully (did not exist in WMS)',
                            'barcode': barcode_data['codbarrasasignado'],
                            'action': 'created',
                            'ean_change': False
                        }
                    elif create_response.status_code == 400 and 'already exists' in create_response.text.lower():
                        # Race condition - barcode was created between our check and creation attempt
                        return {
                            'success': True,
                            'message': 'Barcode already exists (race condition detected)',
                            'barcode': barcode_data['codbarrasasignado'],
                            'action': 'exists',
                            'ean_change': False
                        }
                    else:
                        error_details = create_response.text[:200] if create_response.text else f'HTTP {create_response.status_code}'
                        return {
                            'success': False,
                            'message': f'Barcode creation failed with status {create_response.status_code}',
                            'error_details': error_details,
                            'status_code': create_response.status_code,
                            'action': 'creation_failed',
                            'ean_change': False
                        }
                
        except Exception as e:
            logger.exception("Error updating barcode with product info")
            return {
                'success': False,
                'message': f'Error updating barcode: {str(e)}',
                'ean_change': ean_changed
            }
    
    def _compare_product_data(
        self, 
        existing_product: Dict[str, Any], 
        new_product: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare existing product in WMS with new product data from MercadoLibre.
        
        Args:
            existing_product: Current product in WMS
            new_product: New product data from MercadoLibre
            
        Returns:
            Dictionary with comparison results and detected changes
        """
        changes_detected = []
        
        # Define fields to compare (key fields that matter for synchronization)
        comparison_fields = {
            'productoean': 'productoean',
            'descripcion': 'descripcion', 
            'preciounitario': 'preciounitario',
            'peso': 'peso',
            'presentacion': 'presentacion',
            'observacion': 'observacion'
        }
        
        try:
            for wms_field, new_field in comparison_fields.items():
                existing_value = existing_product.get(wms_field)
                new_value = new_product.get(new_field)
                
                # Normalize values for comparison
                existing_normalized = self._normalize_field_value(existing_value)
                new_normalized = self._normalize_field_value(new_value)
                
                if existing_normalized != new_normalized:
                    changes_detected.append({
                        'field': wms_field,
                        'old_value': existing_normalized,
                        'new_value': new_normalized
                    })
                    logger.info(f"Change detected in {wms_field}: '{existing_normalized}' → '{new_normalized}'")
            
            has_changes = len(changes_detected) > 0
            
            return {
                'has_changes': has_changes,
                'changes_detected': changes_detected,
                'total_changes': len(changes_detected)
            }
            
        except Exception as e:
            logger.error(f"Error comparing product data: {e}")
            # If comparison fails, assume changes exist to be safe
            return {
                'has_changes': True,
                'changes_detected': [{'field': 'comparison_error', 'error': str(e)}],
                'total_changes': 1
            }
    
    def _normalize_field_value(self, value: Any) -> str:
        """
        Normalize field value for comparison.
        Handles None, strips whitespace, converts to string.
        """
        if value is None:
            return ""
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, str):
            return value.strip()
        return str(value)
    
    def _needs_product_update(
        self, 
        existing_product: Dict[str, Any], 
        new_product: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine if product needs updating based on field comparison.
        
        Args:
            existing_product: Current product in WMS
            new_product: New product data from MercadoLibre
            
        Returns:
            Dictionary indicating if update is needed and why
        """
        comparison_result = self._compare_product_data(existing_product, new_product)
        
        return {
            'needs_update': comparison_result['has_changes'],
            'reason': f"{comparison_result['total_changes']} fields changed" if comparison_result['has_changes'] else "No changes detected",
            'changes': comparison_result['changes_detected']
        }
    
    def _barcode_exists_in_wms(
        self, 
        idinternoean: str, 
        original_request: Any = None
    ) -> Dict[str, Any]:
        """
        Check if barcode exists in WMS before attempting update.
        
        Args:
            idinternoean: Internal EAN to search for
            original_request: Original Django request for auth
            
        Returns:
            Dictionary with existence info and barcode data if found
        """
        try:
            logger.info(f"Checking if barcode exists in WMS: {idinternoean}")
            
            # Search for existing barcode
            search_response = self.wms.get(
                self.BARCODE_ENDPOINT,
                original_request=original_request,
                params={'idinternoean': idinternoean}
            )
            
            if search_response.status_code == 200:
                barcode_data = search_response.json()
                
                # Check if we got results
                if isinstance(barcode_data, list) and len(barcode_data) > 0:
                    logger.info(f"Barcode exists in WMS: {idinternoean}")
                    return {
                        'exists': True,
                        'barcode_data': barcode_data[0],
                        'message': f'Barcode {idinternoean} found in WMS'
                    }
                elif isinstance(barcode_data, dict) and barcode_data:
                    logger.info(f"Barcode exists in WMS: {idinternoean}")
                    return {
                        'exists': True,
                        'barcode_data': barcode_data,
                        'message': f'Barcode {idinternoean} found in WMS'
                    }
                else:
                    logger.info(f"Barcode does not exist in WMS: {idinternoean}")
                    return {
                        'exists': False,
                        'barcode_data': None,
                        'message': f'Barcode {idinternoean} not found in WMS'
                    }
            else:
                logger.info(f"Barcode search failed or not found: {idinternoean} (Status: {search_response.status_code})")
                return {
                    'exists': False,
                    'barcode_data': None,
                    'message': f'Barcode search failed: {search_response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error checking barcode existence {idinternoean}: {e}")
            return {
                'exists': False,  # Assume doesn't exist if we can't check
                'barcode_data': None,
                'message': f'Error checking barcode: {str(e)}'
            }
    
    def _get_product_detail(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product detail from MercadoLibre including description."""
        try:
            return self.meli.get_product(product_id)
        except Exception as e:
            logger.error(f"Error getting product detail: {e}")
            return None
    
    def _map_product_to_wms(self, meli_item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Map MercadoLibre item to WMS format."""
        try:
            mapper = ProductMapper.from_meli_item(meli_item)
            wms_product = mapper.to_wms_format()
            
            # Validate required fields
            required = {'productoean', 'descripcion', 'referencia'}
            if required.issubset(wms_product.keys()):
                return wms_product
            else:
                logger.warning(f"Product {meli_item.get('id')} missing required fields")
                return None
                
        except Exception as e:
            logger.error(f"Error mapping product {meli_item.get('id')}: {e}")
            return None
    
    def _get_product_from_wms_by_reference(
        self, 
        referencia: str, 
        original_request: Any = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get product from WMS by reference (more reliable than EAN).
        
        Args:
            referencia: Product reference to search for
            original_request: Original Django request for auth
            
        Returns:
            Product data from WMS or None if not found
        """
        try:
            logger.info(f"Searching product in WMS by reference: {referencia}")
            
            # Search by reference parameter
            search_response = self.wms.get(
                self.PRODUCT_ENDPOINT,
                original_request=original_request,
                params={'referencia': referencia}
            )
            
            if search_response.status_code == 200:
                products = search_response.json()
                
                # If products is a list, get the first match
                if isinstance(products, list) and len(products) > 0:
                    product = products[0]
                    logger.info(f"Found product in WMS: {product.get('productoean', 'N/A')}")
                    return product
                elif isinstance(products, dict):
                    # Single product returned
                    logger.info(f"Found product in WMS: {products.get('productoean', 'N/A')}")
                    return products
                else:
                    logger.info(f"No product found with reference: {referencia}")
                    return None
            else:
                logger.warning(f"WMS search failed: {search_response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error searching product by reference {referencia}: {e}")
            return None
    
    def _detect_ean_change(
        self, 
        current_ean: str, 
        wms_product: Optional[Dict[str, Any]]
    ) -> tuple[bool, Optional[str]]:
        """
        Detect if EAN has changed compared to WMS record.
        
        Args:
            current_ean: Current EAN from MercadoLibre
            wms_product: Current product in WMS (if exists)
            
        Returns:
            Tuple of (has_changed: bool, previous_ean: str|None)
        """
        if not wms_product:
            return False, None
            
        previous_ean = wms_product.get('productoean')
        
        if previous_ean and previous_ean != current_ean:
            logger.info(f"EAN change detected: {previous_ean} → {current_ean}")
            return True, previous_ean
        
        return False, previous_ean
    
    def _create_barcode_relationship(
        self,
        previous_ean: str,
        new_ean: str,
        original_request: Any = None
    ) -> Dict[str, Any]:
        """
        Create barcode relationship for EAN change.
        Creates record: {idinternoean: previous_ean, codbarrasasignado: new_ean, cantidad: 1}
        
        Args:
            previous_ean: Previous EAN (becomes idinternoean)
            new_ean: New EAN (becomes codbarrasasignado)
            original_request: Original Django request for auth
            
        Returns:
            Creation result
        """
        try:
            logger.info(f"Creating barcode relationship: {previous_ean} → {new_ean}")
            
            barcode_relationship = {
                "idinternoean": previous_ean,
                "codbarrasasignado": new_ean,
                "cantidad": 1
            }
            
            # Create the relationship
            create_response = self.wms.post(
                self.BARCODE_ENDPOINT,
                original_request=original_request,
                json=barcode_relationship
            )
            
            if create_response.status_code in (200, 201):
                return {
                    'success': True,
                    'message': f'Barcode relationship created: {previous_ean} → {new_ean}',
                    'action': 'relationship_created',
                    'previous_ean': previous_ean,
                    'new_ean': new_ean
                }
            elif create_response.status_code == 400 and 'already exists' in create_response.text.lower():
                return {
                    'success': True,
                    'message': f'Barcode relationship already exists: {previous_ean} → {new_ean}',
                    'action': 'relationship_exists',
                    'previous_ean': previous_ean,
                    'new_ean': new_ean
                }
            else:
                return {
                    'success': False,
                    'message': f'Failed to create barcode relationship: {create_response.status_code}',
                    'error': create_response.text[:200] if create_response.text else 'No details',
                    'previous_ean': previous_ean,
                    'new_ean': new_ean
                }
                
        except Exception as e:
            logger.exception(f"Error creating barcode relationship {previous_ean} → {new_ean}")
            return {
                'success': False,
                'message': f'Error creating barcode relationship: {str(e)}',
                'previous_ean': previous_ean,
                'new_ean': new_ean
            }
    
    def _update_product_in_wms(
        self, 
        wms_product: Dict[str, Any], 
        original_request: Any = None
    ) -> Dict[str, Any]:
        """
        Update product in WMS using reference-based search instead of EAN.
        Sends complete data to WMS for automatic field updates.
        """
        try:
            product_ean = wms_product.get('productoean')
            product_reference = wms_product.get('referencia')
            
            if not product_reference:
                return {
                    'success': False,
                    'message': 'Product reference is required for WMS update',
                    'action': 'error'
                }
            
            logger.info(f"Updating product with reference: {product_reference}, EAN: {product_ean}")
            
            # Step 1: Check if product exists in WMS by reference
            existing_product = self._get_product_from_wms_by_reference(
                product_reference, 
                original_request
            )
            
            # Step 2: Prepare complete update data (WMS handles field updates automatically)
            update_data = {
                k: v for k, v in wms_product.items() if v is not None
            }
            
            # Step 3: Detect EAN change and determine if update is needed
            ean_changed = False
            previous_ean = None
            needs_update = True  # Default to true for safety
            
            if existing_product:
                previous_ean = existing_product.get('productoean')
                ean_changed = previous_ean and previous_ean != product_ean
                
                if ean_changed:
                    logger.info(f"EAN change detected: {previous_ean} → {product_ean}")
                    needs_update = True  # Always update when EAN changes
                else:
                    # No EAN change - check if other fields changed
                    logger.info("No EAN change detected - checking if product needs updating...")
                    update_analysis = self._needs_product_update(existing_product, update_data)
                    needs_update = update_analysis['needs_update']
                    
                    if needs_update:
                        logger.info(f"Product needs update: {update_analysis['reason']}")
                        for change in update_analysis['changes']:
                            logger.info(f"  - {change['field']}: '{change['old_value']}' → '{change['new_value']}'")
                    else:
                        logger.info("Product is already synchronized - no update needed")
                        return {
                            'success': True,
                            'message': 'Product already synchronized, no updates needed',
                            'action': 'already_synchronized',
                            'reference': product_reference,
                            'ean': product_ean,
                            'previous_ean': previous_ean,
                            'ean_changed': False,
                            'needs_update': False,
                            'synchronized': True,
                            'existing_product': existing_product
                        }
                
                # Include the existing product ID for proper update
                if 'id' in existing_product:
                    update_data['id'] = existing_product['id']

            # Step 4: Update product only if needed
            if existing_product and needs_update:
                # Product exists and needs update
                logger.info(f"Product needs update - updating via PUT (EAN changed: {ean_changed})")
                
                update_params = {}
                if 'id' in existing_product:
                    update_params['id'] = existing_product['id']
                
                update_response = self.wms.put(
                    self.PRODUCT_ENDPOINT,
                    original_request=original_request,
                    params=update_params,
                    json=update_data
                )
                
                if update_response.status_code in (200, 201):
                    return {
                        'success': True,
                        'message': 'Product updated successfully via reference search',
                        'action': 'updated',
                        'reference': product_reference,
                        'ean': product_ean,
                        'previous_ean': previous_ean,
                        'ean_changed': ean_changed,
                        'needs_update': True,
                        'synchronized': False,
                        'existing_product': existing_product
                    }
                elif update_response.status_code == 400:
                    error_text = update_response.text.lower()
                    
                    if 'already exists' in error_text:
                        return {
                            'success': True,
                            'message': 'Product already exists and is up to date',
                            'action': 'exists',
                            'reference': product_reference,
                            'ean': product_ean,
                            'previous_ean': previous_ean,
                            'ean_changed': ean_changed,
                            'needs_update': False,
                            'synchronized': True,
                            'existing_product': existing_product
                        }
                    else:
                        logger.error(f"Product update failed with 400: {update_response.text}")
                        return {
                            'success': False,
                            'message': f'Product update failed: {update_response.text[:200] if update_response.text else "Unknown error"}',
                            'error': update_response.text[:200] if update_response.text else 'No details',
                            'action': 'update_failed',
                            'reference': product_reference,
                            'ean': product_ean,
                            'previous_ean': previous_ean,
                            'ean_changed': ean_changed,
                            'needs_update': True,
                            'existing_product': existing_product
                        }
                else:
                    return {
                        'success': False,
                        'message': f'Product update failed: {update_response.status_code}',
                        'error': update_response.text[:200] if update_response.text else 'No details',
                        'action': 'update_failed',
                        'reference': product_reference,
                        'ean': product_ean,
                        'previous_ean': previous_ean,
                        'ean_changed': ean_changed,
                        'needs_update': True
                    }
            
            else:
                # Product doesn't exist - create it
                logger.info("Product not found in WMS - creating via POST")
                create_response = self.wms.post(
                    self.PRODUCT_ENDPOINT,
                    original_request=original_request,
                    json=update_data
                )
                
                if create_response.status_code in (200, 201):
                    return {
                        'success': True,
                        'message': 'Product created successfully (not found in WMS)',
                        'action': 'created',
                        'reference': product_reference,
                        'ean': product_ean,
                        'existing_product': None
                    }
                elif create_response.status_code == 400 and 'already exists' in create_response.text.lower():
                    return {
                        'success': True,
                        'message': 'Product already exists in WMS (creation detected existing)',
                        'action': 'exists',
                        'reference': product_reference,
                        'ean': product_ean,
                        'existing_product': None
                    }
                else:
                    return {
                        'success': False,
                        'message': f'Product creation failed: {create_response.status_code}',
                        'error': create_response.text[:200] if create_response.text else 'No details',
                        'action': 'failed',
                        'reference': product_reference,
                        'ean': product_ean
                    }
                
        except Exception as e:
            logger.exception("Error in WMS product operation")
            return {
                'success': False,
                'message': f'WMS operation error: {str(e)}',
                'error': str(e),
                'action': 'error'
            }

    def _build_operation_result(self, success, status, message, action=None, **extra_data):
        """Build a standardized operation result"""
        result = {
            'success': success,
            'status': status,
            'message': message
        }
        if action:
            result['action'] = action
        result.update(extra_data)
        return result

    def _build_final_response(self, product_id, product_ean, product_result, barcode_result):
        """Build the final standardized response"""
        # Determine overall success and status
        product_success = product_result.get('success', False)
        barcode_success = barcode_result.get('success', False)
        
        # Determine operation types for better messaging
        product_action = product_result.get('action', 'unknown')
        barcode_action = barcode_result.get('action', 'unknown')
        
        # Overall success logic - Product is primary, barcode is secondary
        if product_success and barcode_success:
            overall_success = True
            overall_status = "complete_success"
            summary = f"Product {product_action} and barcode {barcode_action} successfully"
        elif product_success and not barcode_success:
            overall_success = True  # Product is the primary operation
            overall_status = "partial_success"
            barcode_error_details = barcode_result.get('error_details', '')
            if 'already exists' in barcode_error_details.lower():
                summary = f"Product {product_action} successfully. Barcode already exists in system"
            else:
                summary = f"Product {product_action} successfully, but barcode operation encountered issues"
        elif not product_success and barcode_success:
            overall_success = False
            overall_status = "partial_failure"
            summary = f"Barcode {barcode_action} successfully, but product operation failed"
        else:
            overall_success = False
            overall_status = "complete_failure"
            summary = "Both product and barcode operations failed"

        # Determine what changed
        product_changed = product_action in ['updated', 'created']
        ean_changed = product_result.get('ean_changed', False)
        relationships_updated = barcode_action in ['relationship_created', 'updated']
        new_barcode_created = barcode_action == 'created'

        # Build changes summary
        changes_summary = {
            'product_changed': product_changed,
            'ean_changed': ean_changed,
            'relationships_updated': relationships_updated,
            'new_barcode_created': new_barcode_created
        }

        # Determine sync status
        fully_synchronized = (
            product_success and 
            barcode_success and 
            product_result.get('synchronized', False)
        )

        # Separate success from warnings for better clarity
        warnings = []
        if not barcode_success and barcode_result.get('error_details'):
            error_details = barcode_result.get('error_details', '')
            if 'already exists' in error_details.lower() or '400' in error_details:
                warnings.append(f"Barcode operation: {barcode_result.get('message', 'Operation had issues')}")

        response = {
            'overall_success': overall_success,
            'overall_status': overall_status,
            'summary': summary,
            'product_id': product_id,
            'product_ean': product_ean,
            'product_operation': {
                'success': product_success,
                'status': product_action,
                'message': product_result.get('message', ''),
                'details': {k: v for k, v in product_result.items() 
                           if k not in ['success', 'message', 'action']}
            },
            'barcode_operation': {
                'success': barcode_success,
                'status': barcode_action,
                'message': barcode_result.get('message', ''),
                'details': {k: v for k, v in barcode_result.items() 
                           if k not in ['success', 'message', 'action']}
            },
            'changes_summary': changes_summary,
            'fully_synchronized': fully_synchronized,
            'updated_at': datetime.now().isoformat()
        }

        # Add warnings if any
        if warnings:
            response['warnings'] = warnings

        return response


# Singleton instance
_update_service: Optional[ProductUpdateService] = None


def get_update_service() -> ProductUpdateService:
    """Get or create update service singleton."""
    global _update_service
    if _update_service is None:
        _update_service = ProductUpdateService()
    return _update_service


# Convenience functions for backward compatibility
def update_single_product(product_id: str, original_request: Any = None) -> Dict[str, Any]:
    """Update a single product - convenience function."""
    service = get_update_service()
    return service.update_single_product(product_id, original_request)


def update_single_barcode(meli_item: Dict[str, Any], original_request: Any = None) -> Dict[str, Any]:
    """Update a single barcode - convenience function."""
    service = get_update_service()
    return service.update_single_barcode(meli_item, original_request)


# Legacy functions for backward compatibility (deprecated)
def get_product_by_id(product_id):
    """DEPRECATED: Use update_single_product instead."""
    logger.warning("get_product_by_id is deprecated, use update_single_product instead")
    service = get_update_service()
    return service._get_product_detail(product_id)


def map_product_to_wms_format(meli_item):
    """DEPRECATED: Use update_single_product instead."""
    logger.warning("map_product_to_wms_format is deprecated, use update_single_product instead")
    service = get_update_service()
    return service._map_product_to_wms(meli_item)


def update_product_in_wms(wms_product, auth_headers=None):
    """DEPRECATED: Use update_single_product instead."""
    logger.warning("update_product_in_wms is deprecated, use update_single_product instead")
    # This would need to be converted to use the new service
    # For now, return error to force migration
    return {"success": False, "message": "This function is deprecated. Use update_single_product instead."}
def update_product_from_meli_to_wms(product_id, auth_headers=None):
    """
    DEPRECATED: Use update_single_product instead.
    
    Args:
        product_id (str): ID del producto en MercadoLibre
        auth_headers (dict): Headers de autenticación
        
    Returns:
        dict: Resultado de la operación
    """
    logger.warning("update_product_from_meli_to_wms is deprecated, use update_single_product instead")
    return {"success": False, "message": "This function is deprecated. Use update_single_product instead."}
