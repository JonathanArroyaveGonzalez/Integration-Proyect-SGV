"""Data models for MercadoLibre configuration."""

from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class MeliConfig:
    """MercadoLibre configuration model."""
    
    user_account_id: str
    access_token: str
    refresh_token: str
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    redirect_uri: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB operations."""
        return {k: v for k, v in asdict(self).items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MeliConfig':
        """Create instance from dictionary."""
        return cls(
            user_account_id=data.get('user_account_id', ''),
            access_token=data.get('access_token', ''),
            refresh_token=data.get('refresh_token', ''),
            client_id=data.get('client_id'),
            client_secret=data.get('client_secret'),
            redirect_uri=data.get('redirect_uri')
        )
