"""
Main transcript generator module.
"""
from typing import Optional, Any
import asyncio
from pydantic import BaseModel
from loguru import logger

from ..config import get_settings
from ..exceptions import TranscriptionError
from .youtube_client import YouTubeClient
from ..core.models import VideoInfo
from ..ai.gemini_processor import GeminiProcessor
from ..ai.base_processor import TranscriptRequest, TranscriptResponse


class TranscriptionOptions(BaseModel):
    """Transcription options model."""
    target_language: Optional[str] = None
    enhance_formatting: bool = True
    include_timestamps: bool = False
    detect_speakers: bool = False
    custom_formatting: Optional[dict[str, Any]] = None


class TranscriptionResult(BaseModel):
    """Transcription result model."""
    video_info: VideoInfo
    transcript: str
    enhanced_transcript: Optional[str] = None
    metadata: dict[str, Any]
    processing_time: float
    confidence_score: float


class TranscriptGenerator:
    """Main transcript generator class."""
    
    def __init__(self):
        """Initialize transcript generator."""
        self.settings = get_settings()
        self.youtube_client = YouTubeClient()
        self.ai_processor = GeminiProcessor()
    
    async def generate_transcript(
        self,
        video_url: str,
        options: Optional[TranscriptionOptions] = None
    ) -> TranscriptionResult:
        """
        Generate transcript for a YouTube video.
        
        Args:
            video_url (str): YouTube video URL
            options (TranscriptionOptions, optional): Transcription options
            
        Returns:
            TranscriptionResult: Generated transcript and metadata
            
        Raises:
            TranscriptionError: If transcription fails
        """
        try:
            options = options or TranscriptionOptions()
            
            # Get video information
            video_info = await self.youtube_client.get_video_info(video_url)
            logger.info(f"Processing video: {video_info.title}")
            
            # Download captions
            source_language = video_info.language or 'en'
            try:
                raw_captions = await self.youtube_client._download_captions(
                    video_info.video_id,
                    language=source_language
                )
                # Process with AI
                request = TranscriptRequest(
                    content=raw_captions,
                    source_language=source_language,
                    target_language=options.target_language,
                    format_options={
                        'enhance_formatting': options.enhance_formatting,
                        'include_timestamps': options.include_timestamps,
                        'detect_speakers': options.detect_speakers,
                        'custom_formatting': options.custom_formatting or {}
                    }
                )
                
                response = await self.ai_processor.process_transcript(request)
                
                # Enhance transcript if needed
                enhanced_transcript = None
                if options.enhance_formatting:
                    enhanced_transcript = await self._enhance_transcript(
                        response.transcript,
                        video_info,
                        options
                    )
                
                return TranscriptionResult(
                    video_info=video_info,
                    transcript=response.transcript,
                    enhanced_transcript=enhanced_transcript,
                    metadata={
                        **response.metadata,
                        'options': options.model_dump(),
                        'source_language': source_language
                    },
                    processing_time=response.processing_time,
                    confidence_score=response.confidence_score
                )
            except Exception as e:
                logger.error(f"Failed to download captions: {e}")
            
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            raise TranscriptionError(f"Failed to generate transcript: {str(e)}")
    
    async def _enhance_transcript(
        self,
        transcript: str,
        video_info: VideoInfo,
        options: TranscriptionOptions
    ) -> str:
        """
        Enhance transcript with additional features.
        """
        enhancement_options = {
            'format': options.custom_formatting,
            'video_context': {
                'title': video_info.title,
                'author': video_info.channel_name,  # Changed from author to channel_name
                'duration': video_info.duration,
                'metadata': video_info.model_dump()  # Changed to use model_dump() for all metadata
            }
        }
        
        return await self.ai_processor.enhance_transcript(
            transcript,
            enhancement_options
        )