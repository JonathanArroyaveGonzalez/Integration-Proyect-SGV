from django.urls import re_path

from wmsAdapterV2.views.Inventory import inventory
from wmsAdapterV2.views.Inventory_Adjustment import inventory_adjustment
from wmsAdapterV2.views.Product import art
from wmsAdapterV2.views.ProductionOrder import production_order
from wmsAdapterV2.views.PurchaseOrder import purchase_order
from wmsAdapterV2.views.SaleOrder import sale_order
from wmsAdapterV2.views.Customer import clt
from wmsAdapterV2.views.Supplier import prv

wms_endpoints_v2 = [
    re_path(r'^art$', art),  # type: ignore
    re_path(r'^clt$', clt),  # type: ignore
    re_path(r'^prv$', prv),  # type: ignore
    re_path(r'^sale_order$', sale_order),  # type: ignore
    re_path(r'^purchase_order$', purchase_order),  # type: ignore
    re_path(r'^production_order$', production_order),  # type: ignore
    re_path(r'^inventory$', inventory),  # type: ignore
    re_path(r'^inventory_adjustment$', inventory_adjustment),  # type: ignore
]
