#!/usr/bin/env python3

import os
import asyncio
import argparse
from pathlib import Path

from audio_processor import AudioProcessor, SilenceParams
from transcription_service import TranscriptionService
from output_formatter import OutputFormatter
from utilities import validate_audio_file, configure_logging

logger = configure_logging()

async def process_dry_run(input_file: str, output_file: str, silence_params: SilenceParams):
    """Process audio file in dry run mode - only detect and extract speech."""
    processor = AudioProcessor(silence_params)
    
    # Load and process audio
    audio = processor.load_audio(input_file)
    segments, ranges, analysis = processor.detect_speech_segments(audio)
    
    # Create speech-only audio
    speech_audio = processor.create_speech_only_audio(segments)
    
    # Save results
    base_path = os.path.splitext(output_file)[0]
    speech_only_path = f"{base_path}_speech_only.wav"
    speech_audio.export(speech_only_path, format='wav', parameters=["-ac", "1"])  # Export as mono WAV
    
    # Generate analysis report
    formatter = OutputFormatter(output_file)
    formatter.generate_analysis_report(analysis, speech_only_path)
    
    logger.info("✅ Dry run completed!")
    logger.info(f"Speech-only audio saved to: {speech_only_path}")

async def process_transcription(input_file: str, output_file: str, silence_params: SilenceParams):
    """Process audio file for transcription using all components."""
    processor = AudioProcessor(silence_params)
    transcriber = TranscriptionService()
    formatter = OutputFormatter(output_file)
    
    try:
        # Load and process audio
        audio = processor.load_audio(input_file)
        segments, ranges, analysis = processor.detect_speech_segments(audio)
        
        # Create speech-only audio
        speech_audio = processor.create_speech_only_audio(segments)
        base_path = os.path.splitext(output_file)[0]
        speech_only_path = f"{base_path}_speech_only.wav"
        speech_audio.export(speech_only_path, format='wav', parameters=["-ac", "1"])
        
        # Transcribe segments
        results = await transcriber.batch_transcribe(segments, ranges)
        
        # Save all output formats
        formatter.save_all_formats(results, analysis, speech_only_path)
        
        logger.info("✅ Transcription completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}")
        raise

async def main():
    parser = argparse.ArgumentParser(description='Transcribe audio files using silence detection and OpenAI API')
    parser.add_argument('input_file', help='Path to the input audio file')
    parser.add_argument('output_file', help='Base path for output files')
    parser.add_argument('--silence-thresh', type=int, default=-45,
                      help='Silence threshold in dB (lower = more aggressive)')
    parser.add_argument('--min-silence', type=int, default=400,
                      help='Minimum silence length in ms (higher = fewer segments)')
    parser.add_argument('--keep-silence', type=int, default=300,
                      help='Amount of silence to keep at segment boundaries in ms')
    parser.add_argument('--dry-run', action='store_true',
                      help='Only detect speech and save speech-only audio')
    
    args = parser.parse_args()
    
    try:
        validate_audio_file(args.input_file)
        
        if not args.dry_run and not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        silence_params = SilenceParams(
            silence_thresh=args.silence_thresh,
            min_silence_len=args.min_silence,
            keep_silence=args.keep_silence
        )
        
        if args.dry_run:
            await process_dry_run(args.input_file, args.output_file, silence_params)
        else:
            await process_transcription(args.input_file, args.output_file, silence_params)
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
