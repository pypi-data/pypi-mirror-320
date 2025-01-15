"""
Command-line interface for YouTube Transcript Generator.
"""
import asyncio
from typing import Optional
import typer
from rich.console import Console
from rich.progress import Progress
from rich import print as rprint

from ..core.transcript_generator import TranscriptGenerator, TranscriptionOptions
from ..config import get_settings

app = typer.Typer(
    name="yt-transcript",
    help="Generate enhanced transcripts from YouTube videos using AI"
)
console = Console()


@app.command()
def generate(
    video_url: str = typer.Argument(..., help="YouTube video URL"),
    output: str = typer.Option("transcript.txt", "--output", "-o", help="Output file path"),
    target_language: Optional[str] = typer.Option(None, "--language", "-l", help="Target language code"),
    enhance: bool = typer.Option(True, "--enhance/--no-enhance", help="Enable/disable transcript enhancement"),
    timestamps: bool = typer.Option(False, "--timestamps", "-t", help="Include timestamps"),
    speakers: bool = typer.Option(False, "--speakers", "-s", help="Detect and label speakers"),
    format: Optional[str] = typer.Option(None, "--format", "-f", help="Output format (txt, srt, json)")
):
    """Generate transcript from YouTube video."""
    try:
        settings = get_settings()
        generator = TranscriptGenerator()
        
        options = TranscriptionOptions(
            target_language=target_language,
            enhance_formatting=enhance,
            include_timestamps=timestamps,
            detect_speakers=speakers,
            custom_formatting={'output_format': format} if format else None
        )
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Generating transcript...", total=100)
            
            # Run async generator in sync context
            result = asyncio.run(generator.generate_transcript(video_url, options))
            
            progress.update(task, completed=100)
        
        # Output results
        transcript = result.enhanced_transcript if result.enhanced_transcript else result.transcript
        
        with open(output, 'w', encoding='utf-8') as f:
            f.write(transcript)
        
        # Print summary
        rprint("\n[green]✓[/green] Transcript generated successfully!")
        rprint(f"\n[bold]Video Information:[/bold]")
        rprint(f"  Title: {result.video_info.title}")
        rprint(f"  Duration: {result.video_info.duration} seconds")
        rprint(f"  Author: {result.video_info.author}")
        
        rprint(f"\n[bold]Processing Information:[/bold]")
        rprint(f"  Confidence Score: {result.confidence_score:.2f}")
        rprint(f"  Processing Time: {result.processing_time:.2f} seconds")
        rprint(f"  Output File: {output}")
        
    except Exception as e:
        rprint(f"\n[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def version():
    """Show version information."""
    from importlib.metadata import version
    try:
        ver = version("youtube_transcript_generator")
        rprint(f"YouTube Transcript Generator v{ver}")
    except:
        rprint("Version information not available")


def main():
    """Main entry point."""
    app()