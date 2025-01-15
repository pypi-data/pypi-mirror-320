"""
Data models for transcript generation.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


class VideoInfo(BaseModel):
    """Video information model."""
    video_id: str
    title: str
    channel_name: str
    duration: float
    language: Optional[str] = None
    upload_date: Optional[str] = None
    view_count: Optional[int] = None
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    thumbnail_url: Optional[str] = None
    is_private: bool = False
    available_captions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TranscriptSegment(BaseModel):
    """Model for a single transcript segment with timestamp."""
    start_time: float = Field(..., description="Start time in seconds")
    end_time: float = Field(..., description="End time in seconds")
    text: str = Field(..., description="Transcript text")
    speaker: Optional[str] = Field(None, description="Speaker identifier")
    confidence: float = Field(default=1.0, description="Confidence score for this segment")
    
    @property
    def duration(self) -> float:
        """Calculate segment duration."""
        return self.end_time - self.start_time
    
    @validator('end_time')
    def end_time_must_be_after_start(cls, v, values):
        """Validate that end_time is after start_time."""
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v


class TranscriptMetadata(BaseModel):
    """Enhanced metadata model."""
    source_language: str
    target_language: Optional[str] = None
    model_name: str
    processing_time: float
    chunks_processed: int
    total_duration: float
    word_count: int
    speaker_count: Optional[int] = None
    confidence_score: float
    generated_at: datetime = Field(default_factory=datetime.now)
    enhanced: bool = False
    format_version: str = "2.0"
    custom_metadata: Dict[str, Any] = Field(default_factory=dict)


class VideoMetadata(BaseModel):
    """Enhanced video metadata model."""
    video_id: str
    title: str
    channel_name: str
    duration: float
    language: Optional[str]
    upload_date: Optional[str]
    view_count: Optional[int]
    description: Optional[str]
    tags: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    thumbnail_url: Optional[str]
    is_private: bool = False
    available_captions: List[str] = Field(default_factory=list)


class TranscriptOutput(BaseModel):
    """Enhanced transcript output model."""
    video_metadata: VideoMetadata
    transcript_metadata: TranscriptMetadata
    segments: List[TranscriptSegment]
    raw_transcript: Optional[str] = None
    enhanced_transcript: Optional[str] = None
    error_logs: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    @property
    def full_transcript(self) -> str:
        """Get full transcript text."""
        return " ".join(segment.text for segment in self.segments)
    
    def to_srt(self) -> str:
        """Convert transcript to SRT format."""
        srt_lines = []
        for i, segment in enumerate(self.segments, 1):
            start = self._format_timestamp(segment.start_time)
            end = self._format_timestamp(segment.end_time)
            speaker = f"[{segment.speaker}] " if segment.speaker else ""
            
            srt_lines.extend([
                str(i),
                f"{start} --> {end}",
                f"{speaker}{segment.text}",
                ""
            ])
        return "\n".join(srt_lines)
    
    def to_vtt(self) -> str:
        """Convert transcript to VTT format."""
        vtt_lines = ["WEBVTT\n"]
        for segment in self.segments:
            start = self._format_timestamp(segment.start_time, vtt=True)
            end = self._format_timestamp(segment.end_time, vtt=True)
            speaker = f"<v {segment.speaker}>" if segment.speaker else ""
            
            vtt_lines.extend([
                f"{start} --> {end}",
                f"{speaker}{segment.text}",
                ""
            ])
        return "\n".join(vtt_lines)
    
    @staticmethod
    def _format_timestamp(seconds: float, vtt: bool = False) -> str:
        """Format timestamp for subtitle files."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        if vtt:
            return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
        else:
            return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace(".", ",")