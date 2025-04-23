#!/usr/bin/env python3

import os
from datetime import datetime

def format_timestamp(ms):
    """Convert milliseconds to HH:MM:SS.mmm format."""
    seconds = ms / 1000
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"

def validate_audio_file(file_path):
    """Validate that an audio file exists and is accessible."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file {file_path} does not exist")
    if not os.path.isfile(file_path):
        raise ValueError(f"Path {file_path} is not a file")
    return True

def configure_logging():
    """Configure basic logging settings."""
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)
