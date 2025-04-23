#!/usr/bin/env python3

from pydub import AudioSegment
from pydub.silence import split_on_silence, detect_nonsilent
import tempfile
import os
from dataclasses import dataclass
from typing import List, Tuple
from utilities import configure_logging

logger = configure_logging()

@dataclass
class SilenceParams:
    silence_thresh: int = -45
    min_silence_len: int = 400
    keep_silence: int = 300

@dataclass
class AudioAnalysis:
    total_duration: float
    speech_duration: float
    silence_duration: float
    speech_percentage: float
    segment_count: int

class AudioProcessor:
    def __init__(self, silence_params: SilenceParams = None):
        """
        Initialize the audio processor with silence detection parameters.
        
        Args:
            silence_params (SilenceParams): Parameters for silence detection
        """
        self.params = silence_params or SilenceParams()
        
    def load_audio(self, file_path: str) -> AudioSegment:
        """Load an audio file and return AudioSegment object."""
        logger.info(f"Loading audio file: {file_path}")
        audio = AudioSegment.from_file(file_path)
        logger.info(f"File duration: {len(audio)/1000:.2f} seconds")
        return audio

    def detect_speech_segments(self, audio: AudioSegment) -> Tuple[List[AudioSegment], List[Tuple[int, int]], AudioAnalysis]:
        """Split audio into segments based on silence detection."""
        logger.info("Detecting speech segments")
        
        # Detect non-silent ranges
        nonsilent_ranges = detect_nonsilent(
            audio,
            min_silence_len=self.params.min_silence_len,
            silence_thresh=self.params.silence_thresh,
        )
        
        # Calculate audio analysis
        total_duration = len(audio)
        total_speech = sum(end - start for start, end in nonsilent_ranges)
        total_silence = total_duration - total_speech
        
        analysis = AudioAnalysis(
            total_duration=total_duration,
            speech_duration=total_speech,
            silence_duration=total_silence,
            speech_percentage=(total_speech/total_duration)*100,
            segment_count=len(nonsilent_ranges)
        )
        
        logger.info(f"Found {len(nonsilent_ranges)} speech segments")
        logger.info(f"Speech percentage: {analysis.speech_percentage:.1f}%")
        
        # Split on silence
        segments = split_on_silence(
            audio,
            silence_thresh=self.params.silence_thresh,
            min_silence_len=self.params.min_silence_len,
            keep_silence=self.params.keep_silence
        )
        
        return segments, nonsilent_ranges, analysis

    def create_speech_only_audio(self, segments: List[AudioSegment]) -> AudioSegment:
        """Create concatenated audio of just speech segments."""
        logger.info("Creating speech-only audio")
        
        if not segments:
            logger.warning("No speech segments found!")
            return AudioSegment.empty()
            
        # Concatenate speech segments
        speech_audio = segments[0]
        for segment in segments[1:]:
            speech_audio = speech_audio + segment
            
        return speech_audio

    def export_segment(self, segment: AudioSegment) -> str:
        """Export an audio segment to a temporary file."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        segment.export(temp_file.name, format='wav', parameters=["-ac", "1"])  # Export as mono WAV
        return temp_file.name

    def cleanup_temp_file(self, file_path: str):
        """Clean up a temporary file."""
        try:
            os.unlink(file_path)
        except Exception as e:
            logger.error(f"Error cleaning up temporary file {file_path}: {e}")
