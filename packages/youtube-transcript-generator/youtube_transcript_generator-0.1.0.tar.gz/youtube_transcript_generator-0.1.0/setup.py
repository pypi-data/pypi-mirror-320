# setup.py
from setuptools import setup, find_packages

setup(
    name="youtube-transcript-generator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "google-generativeai>=0.3.0",
        "yt-dlp>=2024.1.1",
        "pydantic>=2.6.0",
        "pydantic-settings>=2.1.0",
        "loguru>=0.7.2",
        "typer[all]>=0.9.0",
        "rich>=13.7.0",
        "aiohttp>=3.9.1",
        "python-dotenv>=1.0.0",
        "asyncio>=3.4.3",
    ],
    entry_points={
        "console_scripts": [
            "yt-transcript=youtube_transcript_generator.cli.main:main",
        ],
    },
    python_requires=">=3.11",
)