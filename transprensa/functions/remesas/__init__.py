"""
Paquete consolidado de funciones para procesar remesas con Transprensa.
Todas las funciones exportadas usan camelCase.
"""

from .remesa import (
    buildRemesasFromOrders,
    enrichOrderWithProductDetails,
    parseRequestPayload,
    downloadPdfBase64,
    saveGuideToDatabase,
    processPdfDownloadsAndSaves,
    extractPdfUrlsFromResponse,
)
from .transprensa_client import (
    getInternalService,
    collectOrdersFromIds,
    createRemesasInTransprensa,
    printRemesasInTransprensa,
    extractCreatedRemesas,
)

__all__ = [
    # Construcción y enriquecimiento de payloads
    "buildRemesasFromOrders",
    "enrichOrderWithProductDetails",
    "parseRequestPayload",
    # Cliente Transprensa
    "getInternalService",
    "collectOrdersFromIds",
    "createRemesasInTransprensa",
    "printRemesasInTransprensa",
    "extractCreatedRemesas",
    # Manejo de PDFs
    "downloadPdfBase64",
    "saveGuideToDatabase",
    "processPdfDownloadsAndSaves",
    "extractPdfUrlsFromResponse",
]
