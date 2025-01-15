"""
Enhanced base interface for AI processors with comprehensive models.
"""
from abc import ABC, abstractmethod
from typing import Optional, Any, Dict, List
from datetime import datetime
from pydantic import BaseModel, Field, validator


class ProcessingMetrics(BaseModel):
    """Model for AI processing metrics."""
    tokens_processed: int = Field(description="Number of tokens processed")
    processing_time: float = Field(description="Processing time in seconds")
    model_name: str = Field(description="Name of the AI model used")
    timestamp: datetime = Field(default_factory=datetime.now)
    custom_metrics: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('processing_time')
    def validate_processing_time(cls, v):
        """Validate processing time is positive."""
        if v < 0:
            raise ValueError("Processing time must be positive")
        return v


class QualityMetrics(BaseModel):
    """Model for transcript quality metrics."""
    confidence_score: float = Field(ge=0.0, le=1.0, description="Overall confidence")
    grammar_score: float = Field(ge=0.0, le=1.0, description="Grammar quality")
    coherence_score: float = Field(ge=0.0, le=1.0, description="Text coherence")
    custom_scores: Dict[str, float] = Field(default_factory=dict)  # Changed to dict of floats


class FormatOptions(BaseModel):
    """Model for transcript formatting options."""
    include_timestamps: bool = Field(default=False)
    include_speakers: bool = Field(default=False)
    paragraph_breaks: bool = Field(default=True)
    remove_filler_words: bool = Field(default=True)
    format_numbers: bool = Field(default=True)
    capitalize_sentences: bool = Field(default=True)
    custom_options: Dict[str, Any] = Field(default_factory=dict)


class TranscriptRequest(BaseModel):
    """Enhanced model for transcript processing request."""
    content: str = Field(description="Input text content")
    source_language: str = Field(description="Source language code")
    target_language: Optional[str] = Field(default=None, description="Target language code")
    style: Optional[str] = Field(default=None, description="Processing style")
    format_options: FormatOptions = Field(default_factory=FormatOptions)
    preserve_timestamps: bool = Field(default=True)
    detect_speakers: bool = Field(default=False)
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    
    @validator('content')
    def validate_content(cls, v):
        """Validate content is not empty."""
        if not v.strip():
            raise ValueError("Content cannot be empty")
        return v
    
    @validator('source_language', 'target_language')
    def validate_language_code(cls, v):
        """Validate language code format."""
        if v and not isinstance(v, str):
            raise ValueError("Language code must be a string")
        if v and not v.strip():
            raise ValueError("Language code cannot be empty")
        return v


class TranscriptResponse(BaseModel):
    """Enhanced model for transcript processing response."""
    transcript: str = Field(description="Processed transcript text")
    metadata: Dict[str, Any] = Field(description="Processing metadata")
    confidence_score: float = Field(ge=0.0, le=1.0)
    processing_time: float = Field(gt=0.0)
    quality_metrics: QualityMetrics = Field(default_factory=QualityMetrics)
    processing_metrics: ProcessingMetrics
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    
    @validator('transcript')
    def validate_transcript(cls, v):
        """Validate transcript is not empty."""
        if not v.strip():
            raise ValueError("Transcript cannot be empty")
        return v


class EnhancementOptions(BaseModel):
    """Model for transcript enhancement options."""
    format_type: str = Field(default="standard")
    preserve_timestamps: bool = Field(default=True)
    detect_speakers: bool = Field(default=False)
    clean_filler_words: bool = Field(default=True)
    enhance_punctuation: bool = Field(default=True)
    custom_options: Dict[str, Any] = Field(default_factory=dict)


class BaseAIProcessor(ABC):
    """Enhanced abstract base class for AI processors."""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the AI processor."""
        pass
    
    @abstractmethod
    async def process_transcript(
        self,
        request: TranscriptRequest
    ) -> TranscriptResponse:
        """
        Process the transcript using AI.
        
        Args:
            request: Transcript processing request
            
        Returns:
            TranscriptResponse: Processed transcript with metadata
        """
        pass
    
    @abstractmethod
    async def enhance_transcript(
        self,
        transcript: str,
        options: Dict[str, Any]
    ) -> str:
        """
        Enhance the transcript with additional features.
        
        Args:
            transcript: Original transcript text
            options: Enhancement options
            
        Returns:
            str: Enhanced transcript
        """
        pass
    
    @abstractmethod
    async def validate_output(
        self,
        response: TranscriptResponse
    ) -> bool:
        """
        Validate the AI output.
        
        Args:
            response: Generated transcript response
            
        Returns:
            bool: True if valid, False otherwise
        """
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup any resources."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the processor is healthy and ready.
        
        Returns:
            bool: True if healthy, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_supported_languages(self) -> List[str]:
        """
        Get list of supported languages.
        
        Returns:
            List[str]: List of supported language codes
        """
        pass