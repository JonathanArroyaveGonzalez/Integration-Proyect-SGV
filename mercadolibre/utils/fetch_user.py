"""
fetch_user.py
Generic helper to fetch user data from MercadoLibre.
Can be used for customers, providers, or any other user type.
"""

import logging
from typing import Optional, Dict, Any
from mercadolibre.services.meli_service import get_meli_service, MeliService

logger = logging.getLogger(__name__)


class FetchUser:
    """
    Helper class to fetch user data from MercadoLibre.

    Provides a single static method for fetching users.
    """

    @staticmethod
    def fetch_user(
        user_id: str, meli_client: Optional[MeliService] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch user data from MercadoLibre.

        Args:
            user_id: MercadoLibre user ID (customer or provider).
            meli_client: Optional MeliService instance. Defaults to singleton.

        Returns:
            Dictionary with user data if successful, None otherwise.
        """
        meli = meli_client or get_meli_service()
        try:
            response = meli.get(f"/users/{user_id}")
            if response.status_code == 200:
                return response.json()
            logger.error(f"Failed to fetch user {user_id}: {response.status_code}")
            return None
        except Exception as e:
            logger.exception(f"Error fetching user {user_id}: {e}")
            return None
