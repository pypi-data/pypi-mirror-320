from typing import Optional, Any, Dict
import asyncio
from web3 import AsyncWeb3, AsyncHTTPProvider
from .base_client import BaseClient

class Web3Client(BaseClient):
    """Client for interacting with Web3, wrapping the original Web3 package functionality"""
    
    def __init__(self, config_path: str = "config.yml", use_proxy: bool = False):
        super().__init__('web3', config_path=config_path, use_proxy=use_proxy)
        self._web3: Optional[AsyncWeb3] = None
        
    @property
    def web3(self) -> AsyncWeb3:
        """Get or create Web3 instance"""
        if self._web3 is None:
            self._web3 = AsyncWeb3(AsyncHTTPProvider(self.config['api']['web3']['base_url']))
        return self._web3
    
    def __getattr__(self, name: str) -> Any:
        """Forward any undefined attributes to the underlying Web3 instance"""
        return getattr(self.web3, name)
    
    def is_connected(self) -> bool:
        """Check if connected to node"""
        return self.web3.is_connected()
        
    async def close(self):
        """Close Web3 provider connection"""
        if self._web3 is not None:
            if hasattr(self._web3.provider, 'close'):
                await self._web3.provider.close()
            self._web3 = None