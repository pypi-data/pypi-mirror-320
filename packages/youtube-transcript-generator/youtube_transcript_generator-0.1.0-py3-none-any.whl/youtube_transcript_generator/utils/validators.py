# validators.py
"""
Validation utilities for YouTube Transcript Generator.
"""
import re
from typing import Optional
from ..exceptions import ValidationError


def validate_youtube_url(url: str) -> bool:
    """
    Validate YouTube URL format.
    
    Args:
        url (str): YouTube URL to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    patterns = [
        r'^https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'^https?://(?:www\.)?youtube\.com/embed/[\w-]+',
        r'^https?://(?:www\.)?youtube\.com/v/[\w-]+',
        r'^https?://(?:www\.)?youtube\.com/shorts/[\w-]+',
        r'^https?://youtu\.be/[\w-]+'
    ]
    
    return any(re.match(pattern, url) for pattern in patterns)


def validate_language_code(language_code: str) -> bool:
    """
    Validate language code format.
    
    Args:
        language_code (str): Language code to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return bool(re.match(r'^[a-z]{2}(-[A-Z]{2})?$', language_code))


def validate_output_format(format: str) -> bool:
    """
    Validate output format.
    
    Args:
        format (str): Output format to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    valid_formats = {'txt', 'srt', 'vtt', 'json', 'md'}
    return format.lower() in valid_formats


def validate_api_key(api_key: str) -> bool:
    """
    Validate API key format.
    
    Args:
        api_key (str): API key to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return bool(re.match(r'^[A-Za-z0-9_-]{20,}$', api_key))