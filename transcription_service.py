#!/usr/bin/env python3

import asyncio
from dataclasses import dataclass
from typing import List, Dict, Any
from openai import AsyncOpenAI
from pydub import AudioSegment
from utilities import configure_logging

logger = configure_logging()

@dataclass
class TranscriptionResult:
    start_time: int
    end_time: int
    duration: int
    text: str

class TranscriptionService:
    def __init__(self):
        """
        Initialize the transcription service.
        Uses OPENAI_API_KEY environment variable for authentication.
        """
        self.client = AsyncOpenAI()  # Will automatically use OPENAI_API_KEY environment variable
        
    async def transcribe_segment(self, segment: AudioSegment, start_time: int, segment_id: int) -> TranscriptionResult:
        """
        Transcribe a single audio segment using OpenAI's Whisper API.
        
        Args:
            segment (AudioSegment): The audio segment to transcribe
            start_time (int): Start time of the segment in milliseconds
            segment_id (int): Identifier for the segment
            
        Returns:
            TranscriptionResult: Object containing timing and transcription text
        """
        from audio_processor import AudioProcessor
        processor = AudioProcessor()
        
        try:
            logger.info(f"Processing segment {segment_id} (starts at {start_time/1000:.2f}s)")
            temp_file_path = processor.export_segment(segment)
            
            try:
                with open(temp_file_path, 'rb') as audio_file:
                    logger.info(f"Sending segment {segment_id} to API...")
                    transcription = await self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                    
                    result = TranscriptionResult(
                        start_time=start_time,
                        end_time=start_time + len(segment),
                        duration=len(segment),
                        text=transcription.text
                    )
                    
                    logger.info(f"Segment {segment_id} processed: {len(transcription.text)} chars")
                    return result
                    
            finally:
                processor.cleanup_temp_file(temp_file_path)
                
        except Exception as e:
            logger.error(f"Error processing segment {segment_id}: {str(e)}")
            raise
    
    async def batch_transcribe(self, segments: List[AudioSegment], ranges: List[tuple]) -> List[TranscriptionResult]:
        """
        Transcribe multiple audio segments concurrently.
        
        Args:
            segments (List[AudioSegment]): List of audio segments to transcribe
            ranges (List[tuple]): List of (start, end) time ranges for each segment
            
        Returns:
            List[TranscriptionResult]: List of transcription results in chronological order
        """
        logger.info(f"Starting batch transcription of {len(segments)} segments")
        
        tasks = []
        for i, (segment, (start, _)) in enumerate(zip(segments, ranges)):
            task = self.transcribe_segment(segment, start, i+1)
            tasks.append(task)
        
        # Process all segments concurrently
        results = await asyncio.gather(*tasks)
        
        # Sort by start time to maintain chronological order
        return sorted(results, key=lambda x: x.start_time)
