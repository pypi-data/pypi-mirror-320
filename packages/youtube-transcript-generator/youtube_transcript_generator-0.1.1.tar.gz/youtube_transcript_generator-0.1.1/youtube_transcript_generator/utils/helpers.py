# helpers.py
"""
Helper utilities for YouTube Transcript Generator.
"""
import asyncio
import json
from pathlib import Path
import re
from typing import Any, Dict, Optional
from datetime import datetime
import hashlib
import aiohttp
from ..config import get_settings
from ..logger import logger


async def fetch_with_retry(url: str, retries: int = 3) -> Optional[str]:
    """
    Fetch URL content with retry logic.
    
    Args:
        url (str): URL to fetch
        retries (int): Number of retry attempts
        
    Returns:
        Optional[str]: Response content if successful, None otherwise
    """
    async with aiohttp.ClientSession() as session:
        for attempt in range(retries):
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
                    elif response.status == 429:  # Rate limit
                        wait_time = int(response.headers.get('Retry-After', 60))
                        logger.warning(f"Rate limited. Waiting {wait_time} seconds...")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"HTTP {response.status}: {await response.text()}")
            except Exception as e:
                logger.error(f"Fetch attempt {attempt + 1} failed: {str(e)}")
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    return None


def format_timestamp(seconds: float) -> str:
    """
    Format seconds into timestamp string.
    
    Args:
        seconds (float): Time in seconds
        
    Returns:
        str: Formatted timestamp (HH:MM:SS.mmm)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"


def cache_result(key: str, data: Any, expires: int = 3600) -> None:
    """
    Cache data with expiration.
    
    Args:
        key (str): Cache key
        data (Any): Data to cache
        expires (int): Cache expiration in seconds
    """
    settings = get_settings()
    cache_dir = Path(settings.CACHE_DIR)
    cache_dir.mkdir(exist_ok=True)
    
    cache_file = cache_dir / f"{hashlib.md5(key.encode()).hexdigest()}.json"
    cache_data = {
        'data': data,
        'expires': datetime.now().timestamp() + expires
    }
    
    with cache_file.open('w') as f:
        json.dump(cache_data, f)


def get_cached_result(key: str) -> Optional[Any]:
    """
    Retrieve cached data if not expired.
    
    Args:
        key (str): Cache key
        
    Returns:
        Optional[Any]: Cached data if valid, None otherwise
    """
    settings = get_settings()
    cache_dir = Path(settings.CACHE_DIR)
    cache_file = cache_dir / f"{hashlib.md5(key.encode()).hexdigest()}.json"
    
    if cache_file.exists():
        try:
            with cache_file.open('r') as f:
                cache_data = json.load(f)
                
            if cache_data['expires'] > datetime.now().timestamp():
                return cache_data['data']
            else:
                cache_file.unlink()
        except Exception as e:
            logger.error(f"Cache read error: {str(e)}")
            
    return None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe filesystem operations.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    # Limit length
    filename = filename[:255]
    return filename