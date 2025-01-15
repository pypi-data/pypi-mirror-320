"""
Complete Gemini Pro AI processor implementation.
"""
import time
import asyncio
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from loguru import logger

from .base_processor import (
    BaseAIProcessor,
    TranscriptRequest,
    TranscriptResponse,
    EnhancementOptions,
    ProcessingMetrics,
    QualityMetrics
)
from ..exceptions import AIProcessingError, TokenLimitError
from ..config import get_settings


class GeminiProcessor(BaseAIProcessor):
    """Gemini Pro AI processor implementation."""
    
    def __init__(self):
        """Initialize Gemini Pro processor."""
        self.settings = get_settings()
        self._initialize_model()
        self.MAX_CHUNK_SIZE = 10000  # characters per chunk
        
    def _initialize_model(self) -> None:
        """Initialize Gemini model with error handling."""
        try:
            genai.configure(api_key=self.settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(self.settings.MODEL_NAME)
            self.safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            }
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {str(e)}")
            raise AIProcessingError(f"Model initialization failed: {str(e)}")

    async def initialize(self) -> None:
        """Initialize the AI processor."""
        await self.health_check()

    async def process_transcript(
        self,
        request: TranscriptRequest
    ) -> TranscriptResponse:
        """Process transcript with Gemini Pro."""
        start_time = time.time()
        
        try:
            content = request.content
            chunks = [content[i:i + self.MAX_CHUNK_SIZE] 
                    for i in range(0, len(content), self.MAX_CHUNK_SIZE)]
            
            logger.info(f"Processing transcript in {len(chunks)} chunks")
            
            processed_chunks = []
            chunk_confidences = []
            
            for i, chunk in enumerate(chunks):
                logger.info(f"Processing chunk {i+1}/{len(chunks)}")
                
                prompt = self._create_processing_prompt(
                    chunk,
                    request,
                    chunk_index=i,
                    total_chunks=len(chunks)
                )
                
                try:
                    response = await self.model.generate_content_async(
                        prompt,
                        safety_settings=self.safety_settings,
                        generation_config={
                            "temperature": 0.3,
                            "top_p": 0.8,
                            "top_k": 40
                        }
                    )
                    
                    # Calculate confidence for this chunk
                    chunk_confidence = self._calculate_chunk_confidence(response, chunk)
                    chunk_confidences.append(chunk_confidence)
                    
                    processed_chunks.append(response.text)
                    
                except Exception as e:
                    if "token count" in str(e).lower():
                        if len(chunk) > 5000:
                            subchunks = self._split_into_smaller_chunks(chunk)
                            sub_results, sub_confidences = await self._process_subchunks(subchunks)
                            processed_chunks.extend(sub_results)
                            chunk_confidences.extend(sub_confidences)
                        else:
                            raise TokenLimitError(len(chunk), 30720, self.settings.MODEL_NAME)
                    else:
                        raise AIProcessingError(f"Chunk processing failed: {str(e)}")
            
            # Combine processed chunks
            final_text = self._combine_chunks(processed_chunks)
            
            # Calculate overall metrics
            processing_time = time.time() - start_time
            overall_confidence = sum(chunk_confidences) / len(chunk_confidences)
            
            # Calculate grammar and coherence scores
            grammar_score = self._calculate_grammar_score(final_text)
            coherence_score = self._calculate_coherence_score(final_text, processed_chunks)
            
            processing_metrics = ProcessingMetrics(
                tokens_processed=len(content) // 4,
                processing_time=processing_time,
                model_name=self.settings.MODEL_NAME
            )
            
            quality_metrics = QualityMetrics(
                confidence_score=overall_confidence,
                grammar_score=grammar_score,
                coherence_score=coherence_score,
                custom_scores={
                    'average_chunk_confidence': sum(chunk_confidences) / len(chunk_confidences),
                    'min_chunk_confidence': min(chunk_confidences),
                    'max_chunk_confidence': max(chunk_confidences),
                    'chunks_processed': float(len(chunks))  # Convert to float
                }
            )
            
            return TranscriptResponse(
                transcript=final_text,
                metadata={
                    'chunks_processed': len(chunks),
                    'source_language': request.source_language,
                    'target_language': request.target_language,
                    'processing_options': request.format_options.model_dump()
                },
                confidence_score=overall_confidence,
                processing_time=processing_time,
                quality_metrics=quality_metrics,
                processing_metrics=processing_metrics,
                warnings=[],
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"Error processing transcript: {str(e)}")
            raise AIProcessingError(f"Failed to process transcript: {str(e)}")

    def _calculate_chunk_confidence(self, response, original_chunk: str) -> float:
        """Calculate confidence score for a chunk based on various factors."""
        try:
            # Base confidence starts at 1.0
            confidence = 1.0
            
            # Factor 1: Response length ratio
            length_ratio = len(response.text) / len(original_chunk)
            if length_ratio < 0.5 or length_ratio > 2.0:
                confidence *= 0.8
            
            # Factor 2: Check for common error indicators
            error_indicators = ['error', 'invalid', 'failed', 'unable to']
            if any(indicator in response.text.lower() for indicator in error_indicators):
                confidence *= 0.7
            
            # Factor 3: Text quality checks
            if len(response.text.split()) < 3:  # Too short responses
                confidence *= 0.6
                
            # Factor 4: Response candidateness from Gemini
            if hasattr(response, 'candidates') and response.candidates:
                candidate_score = response.candidates[0].safety_ratings[0].probability
                confidence *= candidate_score
                
            return max(0.1, min(1.0, confidence))  # Ensure between 0.1 and 1.0
            
        except Exception as e:
            logger.warning(f"Error calculating chunk confidence: {str(e)}")
            return 0.7  # Default fallback confidence

    def _calculate_grammar_score(self, text: str) -> float:
        """Calculate grammar score based on text analysis."""
        try:
            # Basic grammar checks
            sentences = text.split('.')
            score = 1.0
            
            # Check for basic grammar indicators
            if not text[0].isupper():
                score *= 0.9
                
            # Check for sentence structure
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and (not sentence[0].isupper() or len(sentence.split()) < 2):
                    score *= 0.95
                    
            # Check for repeated words
            words = text.lower().split()
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
                if word_counts[word] > len(words) / 10:  # More than 10% repetition
                    score *= 0.9
                    
            return max(0.5, min(1.0, score))
            
        except Exception as e:
            logger.warning(f"Error calculating grammar score: {str(e)}")
            return 0.8

    def _calculate_coherence_score(self, final_text: str, chunks: list[str]) -> float:
        """Calculate coherence score based on text flow and chunk transitions."""
        try:
            score = 1.0
            
            # Check transitions between chunks
            for i in range(len(chunks) - 1):
                transition_text = chunks[i][-50:] + chunks[i + 1][:50]
                
                # Check for abrupt transitions
                if '.' in transition_text:
                    sentences = transition_text.split('.')
                    if len(sentences) >= 2 and not any(c in '.!?' for c in sentences[-2]):
                        score *= 0.95
                        
            # Check overall flow
            sentences = final_text.split('.')
            for i in range(len(sentences) - 1):
                if sentences[i].strip() and sentences[i+1].strip():
                    # Check for topic continuity
                    common_words = set(sentences[i].lower().split()) & set(sentences[i+1].lower().split())
                    if not common_words:
                        score *= 0.98
                        
            return max(0.6, min(1.0, score))
            
        except Exception as e:
            logger.warning(f"Error calculating coherence score: {str(e)}")
            return 0.8
    
    async def enhance_transcript(
        self,
        transcript: str,
        options: Dict[str, Any]
    ) -> str:
        """Enhance transcript with additional features."""
        try:
            if len(transcript) > self.MAX_CHUNK_SIZE:
                chunks = [transcript[i:i + self.MAX_CHUNK_SIZE] 
                         for i in range(0, len(transcript), self.MAX_CHUNK_SIZE)]
                enhanced_chunks = []
                
                for chunk in chunks:
                    prompt = self._create_enhancement_prompt(chunk, options)
                    response = await self.model.generate_content_async(prompt)
                    enhanced_chunks.append(response.text)
                
                return self._combine_chunks(enhanced_chunks)
            else:
                prompt = self._create_enhancement_prompt(transcript, options)
                response = await self.model.generate_content_async(prompt)
                return response.text
                
        except Exception as e:
            logger.error(f"Error enhancing transcript: {str(e)}")
            raise AIProcessingError(f"Enhancement failed: {str(e)}")

    async def validate_output(self, response: TranscriptResponse) -> bool:
        """Validate the AI output."""
        if not response.transcript:
            return False
            
        if len(response.transcript.strip()) < 10:
            return False
            
        if response.confidence_score < 0.7:
            return False
            
        return True

    async def cleanup(self) -> None:
        """Cleanup resources."""
        pass  # No cleanup needed for Gemini

    async def health_check(self) -> bool:
        """Check if the processor is healthy and ready."""
        try:
            test_prompt = "Test connection"
            response = await self.model.generate_content_async(test_prompt)
            return bool(response and response.text)
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False

    async def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return self.settings.SUPPORTED_LANGUAGES

    def _create_processing_prompt(
        self,
        content: str,
        request: TranscriptRequest,
        chunk_index: int,
        total_chunks: int
    ) -> str:
        """Create prompt for transcript processing."""
        return f"""
        Process this transcript chunk ({chunk_index + 1} of {total_chunks}):

        Guidelines:
        1. Maintain natural flow and readability
        2. Fix grammar and punctuation
        3. Remove filler words and repetitions
        4. Preserve technical terms and proper names
        5. Maintain timing information if present
        
        Source Language: {request.source_language}
        Target Language: {request.target_language or request.source_language}
        
        Content:
        {content}
        """

    def _create_enhancement_prompt(
        self,
        content: str,
        options: Dict[str, Any]
    ) -> str:
        """Create prompt for transcript enhancement."""
        return f"""
        Enhance this transcript according to the specified options:
        {options}

        Guidelines:
        1. Improve clarity and readability
        2. Format according to specifications
        3. Maintain accuracy of content
        4. Preserve speaker identification if present

        Content:
        {content}
        """

    async def _process_subchunks(
        self,
        subchunks: List[str]
    ) -> List[str]:
        """Process smaller subchunks when main chunk is too large."""
        results = []
        for subchunk in subchunks:
            try:
                response = await self.model.generate_content_async(
                    f"Process this transcript segment:\n{subchunk}"
                )
                results.append(response.text)
            except Exception as e:
                logger.error(f"Error processing subchunk: {str(e)}")
                results.append(subchunk)  # Use original on error
        return results

    def _split_into_smaller_chunks(self, text: str) -> List[str]:
        """Split text into smaller chunks."""
        chunk_size = 5000  # Conservative size
        return [text[i:i + chunk_size] 
                for i in range(0, len(text), chunk_size)]

    def _combine_chunks(self, chunks: List[str]) -> str:
        """Combine processed chunks into final transcript."""
        combined = ' '.join(chunks)
        # Clean up artifacts from chunking
        combined = combined.replace('  ', ' ')
        combined = combined.replace('..', '.')
        combined = combined.replace('. .', '.')
        return combined.strip()