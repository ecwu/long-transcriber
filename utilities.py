import logging
import sys
import os
from pathlib import Path
from tqdm import tqdm

def configure_logging():
    """Configure and return a logger instance."""
    logger = logging.getLogger('audio_processor')
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def validate_audio_file(file_path: str) -> None:
    """
    Validate that the audio file exists and has a supported extension.
    
    Args:
        file_path (str): Path to the audio file
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file extension is not supported
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")
        
    supported_extensions = {'.mp3', '.wav', '.m4a', '.ogg', '.flac'}
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext not in supported_extensions:
        raise ValueError(
            f"Unsupported audio format: {file_ext}\n"
            f"Supported formats: {', '.join(supported_extensions)}"
        )

class TqdmToLogger:
    """
    Output stream for TQDM which will output to logger module instead of
    the StdOut.
    """
    def __init__(self, logger, level=logging.INFO):
        self.logger = logger
        self.level = level
        self._last_print = ""

    def write(self, buf):
        self._last_print = buf.strip('\r\n\t ')

    def flush(self):
        if self._last_print and not self._last_print.startswith("\x1b[A"):
            self.logger.log(self.level, self._last_print)
