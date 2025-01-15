# README.md
# YouTube Transcript Generator

A powerful, AI-enhanced YouTube transcript generator using Gemini Pro. Generate high-quality transcripts with advanced features like speaker detection, multi-language support, and custom formatting.

## Features

- 🎯 High-accuracy transcription using AI enhancement
- 🌍 Multi-language support with translation capabilities
- 👥 Speaker detection and labeling
- ⏱️ Timestamp preservation and formatting
- 🎨 Custom output formats (TXT, SRT, VTT, JSON, MD)
- 🚀 Async processing for better performance
- 📊 Quality metrics and confidence scoring
- 💾 Caching support for better efficiency
- 🛡️ Comprehensive error handling
- 📝 Detailed logging system

## Installation

```bash
pip install youtube-transcript-generator
```

## Quick Start

```python
from youtube_transcript_generator import TranscriptGenerator

async def main():
    generator = TranscriptGenerator()
    result = await generator.generate_transcript(
        "https://youtube.com/watch?v=your_video_id",
        options=TranscriptionOptions(
            target_language="en",
            enhance_formatting=True
        )
    )
    print(result.transcript)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## CLI Usage

```bash
# Generate transcript
yt-transcript generate https://youtube.com/watch?v=your_video_id -o transcript.txt

# With options
yt-transcript generate https://youtube.com/watch?v=your_video_id \
    --language es \
    --format srt \
    --timestamps \
    --speakers
```

## Configuration

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key
YOUTUBE_API_KEY=your_youtube_api_key  # Optional
DEBUG=False
LOG_LEVEL=INFO
```

## Documentation

Visit our [documentation](docs/README.md) for detailed information.

## Contributing

We welcome contributions! Please see our [contributing guidelines](docs/CONTRIBUTING.md).

## License

MIT License - see [LICENSE](LICENSE) for details.

# API.md
# API Documentation

## Core Components

### TranscriptGenerator

The main class for generating transcripts.

```python
class TranscriptGenerator:
    async def generate_transcript(
        video_url: str,
        options: Optional[TranscriptionOptions] = None
    ) -> TranscriptionResult:
        """Generate transcript for a YouTube video."""
```

### TranscriptionOptions

Configure transcript generation:

```python
class TranscriptionOptions(BaseModel):
    target_language: Optional[str] = None
    enhance_formatting: bool = True
    include_timestamps: bool = False
    detect_speakers: bool = False
    custom_formatting: Optional[dict] = None
```

### VideoInfo

Video information model:

```python
class VideoInfo(BaseModel):
    video_id: str
    title: str
    duration: int
    language: Optional[str]
    captions_available: bool
    url: str
    author: str
    view_count: Optional[int]
    metadata: dict
```

## Error Handling

The library defines several exception classes:

- `TranscriptionError`: Base exception
- `ValidationError`: Input validation errors
- `VideoProcessingError`: Video processing failures
- `AIProcessingError`: AI processing issues

## Examples

### Basic Usage

```python
from youtube_transcript_generator import TranscriptGenerator

generator = TranscriptGenerator()
result = await generator.generate_transcript("https://youtube.com/watch?v=...")
print(result.transcript)
```

### Advanced Usage

```python
options = TranscriptionOptions(
    target_language="es",
    enhance_formatting=True,
    include_timestamps=True,
    detect_speakers=True,
    custom_formatting={"format": "srt"}
)

result = await generator.generate_transcript(
    "https://youtube.com/watch?v=...",
    options=options
)
```

### Enhanced Usage

# As a module
```python
runner = TranscriptRunner()
output_files = await runner.process_video(
    "https://youtube.com/watch?v=VIDEO_ID",
    {
        'save_json': True,
        'save_srt': True,
        'save_vtt': True,
        'save_txt': True,
        'include_timestamps': True
    }
)
```

# As command line tool
```shell
python runner.py "https://youtube.com/watch?v=VIDEO_ID" \
    --formats json,srt,vtt,txt \
    --timestamps \
    --output-dir my_transcripts
```

# CONTRIBUTING.md
# Contributing Guidelines

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a virtual environment
4. Install development dependencies

```bash
pip install -e ".[dev]"
```

## Development Process

1. Create a new branch
2. Make your changes
3. Write/update tests
4. Update documentation
5. Submit a pull request

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings (Google style)
- Keep functions focused and small
- Add comments for complex logic

## Testing

Run tests:

```bash
pytest
```

With coverage:

```bash
pytest --cov=youtube_transcript_generator
```

## Documentation

- Update API documentation for new features
- Add examples for new functionality
- Keep README.md up to date

## Pull Request Process

1. Update CHANGELOG.md
2. Ensure tests pass
3. Update documentation
4. Wait for review

# architecture.md
# Architecture Overview

## Core Components

### TranscriptGenerator

The main orchestrator that:
- Coordinates video processing
- Manages AI enhancement
- Handles output formatting

### YouTubeClient

Responsible for:
- Video information retrieval
- Caption downloading
- Format conversion

### AI Processor

Handles:
- Transcript enhancement
- Language processing
- Quality validation

## Data Flow

1. User Input → Video URL
2. URL → Video Information
3. Video → Raw Captions
4. Captions → AI Processing
5. AI Output → Final Transcript

## Design Principles

1. Modularity
   - Separate concerns
   - Pluggable components
   - Easy extensions

2. Robustness
   - Error handling
   - Retry logic
   - Validation

3. Performance
   - Async operations
   - Caching
   - Rate limiting

4. Maintainability
   - Clear structure
   - Documentation
   - Type safety