"""
youtube_client.py
Enhanced YouTube client with robust error handling and advanced features.
"""
from datetime import datetime, timedelta
import json
import re
import asyncio
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
import aiohttp
import yt_dlp
from loguru import logger
from urllib.parse import parse_qs, urlparse

from ..config import get_settings
from ..exceptions import (
    VideoProcessingError,
    ValidationError,
    RateLimitError,
    NetworkError
)
from .models import VideoInfo, TranscriptSegment


class YouTubeClient:
    """Enhanced YouTube client with robust error handling."""
    
    def __init__(self):
        """Initialize YouTube client."""
        self.settings = get_settings()
        self.cache_dir = Path(self.settings.CACHE_DIR)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Configure yt-dlp
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitlesformat': 'vtt',
            'skip_download': True,
            'cachedir': str(self.cache_dir),
            'retries': 3,
            'fragment_retries': 3,
            'extractor_retries': 3,
            'socket_timeout': 30,
        }

    async def get_video_info(self, url: str) -> VideoInfo:
        """
        Get comprehensive video information.
        
        Args:
            url: YouTube video URL
            
        Returns:
            VideoInfo: Detailed video information
            
        Raises:
            VideoNotFoundError: If video doesn't exist
            VideoPrivateError: If video is private
            ValidationError: If URL is invalid
            NetworkError: If network issues occur
        """
        try:
            video_id = self._extract_video_id(url)
            if not video_id:
                raise ValidationError("Invalid YouTube URL")
            
            # Try to get cached info first
            cached_info = self._get_cached_info(video_id)
            if cached_info:
                return cached_info
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                try:
                    info = await asyncio.get_event_loop().run_in_executor(
                        None, ydl.extract_info, url, False
                    )
                except yt_dlp.utils.DownloadError as e:
                    if "Private video" in str(e):
                        raise NetworkError("This video is private")
                    elif "not exist" in str(e):
                        raise NetworkError("Video not found")
                    else:
                        raise NetworkError(f"Failed to fetch video info: {str(e)}")
                
                # Validate video duration
                if info['duration'] > self.settings.MAX_VIDEO_LENGTH:
                    raise ValidationError(
                        f"Video exceeds maximum length of {self.settings.MAX_VIDEO_LENGTH} seconds"
                    )
                
                metadata = VideoInfo(
                    video_id=video_id,
                    title=info['title'],
                    channel_name=info.get('uploader', ''),
                    duration=float(info['duration']),
                    language=info.get('language'),
                    upload_date=info.get('upload_date'),
                    view_count=info.get('view_count'),
                    description=info.get('description', ''),
                    tags=info.get('tags', []),
                    categories=info.get('categories', []),
                    thumbnail_url=info.get('thumbnail'),
                    is_private=False,
                    available_captions=self._get_available_captions(info)
                )
                
                # Cache the metadata
                self._cache_info(video_id, metadata)
                
                return metadata
                
        except Exception as e:
            logger.error(f"Error processing video {url}: {str(e)}")
            if isinstance(e, (ValidationError,)):
                raise
            raise VideoProcessingError(f"Failed to process video: {str(e)}")

    async def get_transcript_segments(
        self,
        video_id: str,
        language: str = 'en'
    ) -> List[TranscriptSegment]:
        """
        Get transcript segments with timestamps.
        
        Args:
            video_id: YouTube video ID
            language: Desired caption language
            
        Returns:
            List[TranscriptSegment]: List of transcript segments
        """
        try:
            captions = await self._download_captions(video_id, language)
            segments = self._parse_vtt_to_segments(captions)
            return self._merge_short_segments(segments)
        except Exception as e:
            logger.error(f"Error getting transcript segments: {str(e)}")
            raise VideoProcessingError(f"Failed to get transcript segments: {str(e)}")

    async def _download_captions(self, video_id: str, language: str) -> str:
        """Download and extract captions."""
        url = f"https://youtube.com/watch?v={video_id}"
        
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = await asyncio.get_event_loop().run_in_executor(
                    None, ydl.extract_info, url, False
                )
                
                # Try manual captions first, then auto-generated
                subtitles = info.get('subtitles', {})
                auto_captions = info.get('automatic_captions', {})
                
                if language in subtitles:
                    caption_info = subtitles[language]
                elif language in auto_captions:
                    caption_info = auto_captions[language]
                else:
                    raise ValueError(f"No captions available for language: {language}")
                
                # Get VTT format if available
                vtt_caption = next(
                    (c for c in caption_info if c['ext'] == 'vtt'),
                    caption_info[0]
                )
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(vtt_caption['url']) as response:
                        if response.status == 200:
                            return await response.text()
                        else:
                            raise NetworkError(
                                f"Failed to download captions: HTTP {response.status}"
                            )
                            
        except Exception as e:
            logger.error(f"Error downloading captions: {str(e)}")
            raise VideoProcessingError(f"Failed to download captions: {str(e)}")

    def _parse_vtt_to_segments(self, vtt_content: str) -> List[TranscriptSegment]:
        """Parse VTT content into transcript segments."""
        segments = []
        current_segment = None
        
        for line in vtt_content.split('\n'):
            line = line.strip()
            
            # Skip WebVTT header and empty lines
            if not line or line == 'WEBVTT':
                continue
            
            # Parse timestamp line
            timestamp_match = re.match(
                r'(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})',
                line
            )
            if timestamp_match:
                if current_segment:
                    segments.append(current_segment)
                
                start = self._timestamp_to_seconds(timestamp_match.group(1))
                end = self._timestamp_to_seconds(timestamp_match.group(2))
                
                current_segment = TranscriptSegment(
                    start_time=start,
                    end_time=end,
                    text="",
                    confidence=1.0
                )
                continue
            
            # Add text to current segment
            if current_segment and line:
                current_segment.text += f" {line}" if current_segment.text else line
        
        # Add last segment
        if current_segment:
            segments.append(current_segment)
        
        return segments

    def _merge_short_segments(
        self,
        segments: List[TranscriptSegment],
        min_duration: float = 1.0
    ) -> List[TranscriptSegment]:
        """Merge segments that are too short."""
        if not segments:
            return segments
        
        merged = []
        current = segments[0]
        
        for next_seg in segments[1:]:
            if current.duration < min_duration:
                # Merge with next segment
                current = TranscriptSegment(
                    start_time=current.start_time,
                    end_time=next_seg.end_time,
                    text=f"{current.text} {next_seg.text}",
                    confidence=min(current.confidence, next_seg.confidence)
                )
            else:
                merged.append(current)
                current = next_seg
        
        merged.append(current)
        return merged

    @staticmethod
    def _timestamp_to_seconds(timestamp: str) -> float:
        """Convert timestamp to seconds."""
        h, m, s = timestamp.split(':')
        return float(h) * 3600 + float(m) * 60 + float(s)

    @staticmethod
    def _extract_video_id(url: str) -> Optional[str]:
        """Extract video ID from various YouTube URL formats."""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:shorts\/)([0-9A-Za-z_-]{11})',
            r'^([0-9A-Za-z_-]{11})$'
        ]
        
        # Try parsing URL first
        parsed_url = urlparse(url)
        if parsed_url.netloc in ('youtube.com', 'www.youtube.com', 'youtu.be'):
            # Extract video ID from query parameters
            if parsed_url.netloc in ('youtube.com', 'www.youtube.com'):
                query_params = parse_qs(parsed_url.query)
                if 'v' in query_params:
                    return query_params['v'][0]

            # Try regex patterns
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)

        return None
    
    def _get_cached_info(self, video_id: str) -> Optional[VideoInfo]:
        """Get cached video metadata if available and not expired."""
        cache_file = self.cache_dir / f"video_info_{video_id}.json"
        
        if not cache_file.exists():
            return None
            
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                
            # Check if cache is expired (24 hours)
            cached_time = datetime.fromisoformat(cache_data['cached_at'])
            if datetime.now() - cached_time > timedelta(hours=24):
                cache_file.unlink()
                return None
                
            return VideoInfo(**cache_data['metadata'])
            
        except Exception as e:
            logger.warning(f"Error reading cache: {str(e)}")
            if cache_file.exists():
                cache_file.unlink()
            return None

    def _cache_info(self, video_id: str, metadata: VideoInfo) -> None:
        """Cache video metadata."""
        try:
            cache_file = self.cache_dir / f"video_info_{video_id}.json"
            cache_data = {
                'cached_at': datetime.now().isoformat(),
                'metadata': metadata.model_dump()
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.warning(f"Error caching video info: {str(e)}")

    def _get_available_captions(self, info: Dict[str, Any]) -> List[str]:
        """Get list of available caption languages."""
        available = set()
        
        # Manual captions
        if 'subtitles' in info:
            available.update(info['subtitles'].keys())
            
        # Auto-generated captions
        if 'automatic_captions' in info:
            available.update(info['automatic_captions'].keys())
            
        return sorted(list(available))

    async def _fetch_with_retry(
        self,
        url: str,
        retries: int = 3,
        backoff_factor: float = 1.5
    ) -> str:
        """Fetch URL content with exponential backoff retry."""
        last_exception = None
        
        for attempt in range(retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            return await response.text()
                        elif response.status == 429:  # Rate limit
                            retry_after = int(response.headers.get('Retry-After', 60))
                            raise RateLimitError(
                                f"Rate limited. Retry after {retry_after} seconds"
                            )
                        else:
                            raise NetworkError(
                                f"HTTP {response.status}: {await response.text()}"
                            )
                            
            except Exception as e:
                last_exception = e
                if isinstance(e, RateLimitError):
                    raise
                    
                # Calculate backoff time
                backoff = backoff_factor * (2 ** attempt)
                logger.warning(
                    f"Attempt {attempt + 1} failed, retrying in {backoff:.1f}s: {str(e)}"
                )
                await asyncio.sleep(backoff)
        
        raise NetworkError(f"All retry attempts failed: {str(last_exception)}")

    async def cleanup_cache(self, max_age_days: int = 7) -> None:
        """Clean up old cache files."""
        try:
            current_time = datetime.now()
            
            for cache_file in self.cache_dir.glob("video_info_*.json"):
                try:
                    # Check file age
                    file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                    if current_time - file_time > timedelta(days=max_age_days):
                        cache_file.unlink()
                        logger.debug(f"Removed old cache file: {cache_file.name}")
                        
                except Exception as e:
                    logger.warning(f"Error cleaning cache file {cache_file}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error during cache cleanup: {str(e)}")

    async def get_video_chapters(self, video_id: str) -> List[Dict[str, Any]]:
        """Get video chapters if available."""
        try:
            url = f"https://youtube.com/watch?v={video_id}"
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = await asyncio.get_event_loop().run_in_executor(
                    None, ydl.extract_info, url, False
                )
                
                chapters = info.get('chapters', [])
                if not chapters:
                    return []
                    
                return [
                    {
                        'title': chapter['title'],
                        'start_time': chapter['start_time'],
                        'end_time': chapter['end_time']
                    }
                    for chapter in chapters
                ]
                
        except Exception as e:
            logger.warning(f"Error getting video chapters: {str(e)}")
            return []

    def _validate_language_code(self, language: str) -> bool:
        """Validate language code format."""
        return bool(re.match(r'^[a-z]{2}(-[A-Z]{2})?$', language))

    def _get_segment_speaker(self, text: str) -> Tuple[str, Optional[str]]:
        """Extract speaker from segment text if present."""
        speaker_match = re.match(r'^\s*\[([^\]]+)\]:\s*(.+)$', text)
        if speaker_match:
            return speaker_match.group(2).strip(), speaker_match.group(1).strip()
        return text.strip(), None