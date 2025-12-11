"""
Caching Service
Implements prediction caching to reduce redundant ML inference
"""
from diskcache import Cache
from typing import Optional, Any
from datetime import datetime, timedelta
from loguru import logger
import json
from pathlib import Path


class PredictionCache:
    """Cache for ML predictions"""
    
    def __init__(self, cache_dir: str = "cache", ttl_hours: int = 24):
        """
        Initialize cache
        
        Args:
            cache_dir: Directory for cache storage
            ttl_hours: Time-to-live for cache entries in hours
        """
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        self.cache = Cache(cache_dir)
        self.ttl = ttl_hours * 3600  # Convert to seconds
        logger.info(f"Initialized cache with TTL={ttl_hours}h at {cache_dir}")
    
    def get_prediction(self, ticker: str, period: str) -> Optional[dict]:
        """
        Get cached prediction
        
        Args:
            ticker: Stock ticker
            period: Prediction period ('week', 'month', 'year')
            
        Returns:
            Cached prediction dict or None
        """
        key = self._make_key(ticker, period)
        
        try:
            cached = self.cache.get(key)
            
            if cached:
                logger.info(f"Cache HIT for {ticker}/{period}")
                return cached
            else:
                logger.info(f"Cache MISS for {ticker}/{period}")
                return None
                
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set_prediction(self, ticker: str, period: str, prediction: dict):
        """
        Cache a prediction
        
        Args:
            ticker: Stock ticker
            period: Prediction period
            prediction: Prediction data to cache
        """
        key = self._make_key(ticker, period)
        
        try:
            # Add timestamp
            prediction['cached_at'] = datetime.now().isoformat()
            
            # Set with TTL
            self.cache.set(key, prediction, expire=self.ttl)
            logger.info(f"Cached prediction for {ticker}/{period} (TTL={self.ttl}s)")
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    def invalidate_ticker(self, ticker: str):
        """
        Invalidate all predictions for a ticker
        
        Args:
            ticker: Stock ticker
        """
        try:
            for period in ['week', 'month', 'year']:
                key = self._make_key(ticker, period)
                self.cache.delete(key)
            
            logger.info(f"Invalidated cache for {ticker}")
            
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
    
    def invalidate_all(self):
        """Clear entire cache"""
        try:
            self.cache.clear()
            logger.info("Cleared entire cache")
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
    
    def get_stats(self) -> dict:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        try:
            return {
                'size': len(self.cache),
                'volume': self.cache.volume(),
                'ttl_hours': self.ttl / 3600
            }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {}
    
    @staticmethod
    def _make_key(ticker: str, period: str) -> str:
        """Generate cache key"""
        return f"prediction:{ticker}:{period}"


# Global cache instance
_cache_instance: Optional[PredictionCache] = None


def get_cache() -> PredictionCache:
    """Get or create global cache instance"""
    global _cache_instance
    
    if _cache_instance is None:
        _cache_instance = PredictionCache()
    
    return _cache_instance
