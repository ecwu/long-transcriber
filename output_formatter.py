#!/usr/bin/env python3

import os
import json
from datetime import datetime
from typing import List, Dict, Any
from audio_processor import AudioAnalysis
from utilities import configure_logging

logger = configure_logging()

class OutputFormatter:
    def __init__(self, base_output_path: str):
        """Initialize formatter with base output path."""
        self.base_path = os.path.splitext(base_output_path)[0]
        
    def generate_analysis_report(self, analysis: AudioAnalysis, speech_only_path: str):
        """Generate a text report of the audio analysis."""
        report_path = f"{self.base_path}_analysis.txt"
        
        with open(report_path, 'w') as f:
            f.write("Audio Analysis Report\n")
            f.write("===================\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("Duration Statistics:\n")
            f.write(f"- Total Duration: {analysis.total_duration/1000:.2f} seconds\n")
            f.write(f"- Speech Duration: {analysis.speech_duration/1000:.2f} seconds\n")
            f.write(f"- Silence Duration: {analysis.silence_duration/1000:.2f} seconds\n")
            f.write(f"- Speech Percentage: {analysis.speech_percentage:.1f}%\n\n")
            
            f.write("Segment Information:\n")
            f.write(f"- Total Segments: {analysis.segment_count}\n")
            f.write(f"- Speech-only Audio: {speech_only_path}\n")
        
        logger.info(f"Analysis report saved to: {report_path}")
    
    def save_all_formats(self, transcription_results: List[Dict[str, Any]], 
                        analysis: AudioAnalysis, speech_only_path: str):
        """Save transcription results in multiple formats."""
        # Generate analysis report
        self.generate_analysis_report(analysis, speech_only_path)
        
        # Save JSON format
        json_path = f"{self.base_path}.json"
        with open(json_path, 'w') as f:
            json.dump({
                'analysis': {
                    'total_duration': analysis.total_duration,
                    'speech_duration': analysis.speech_duration,
                    'silence_duration': analysis.silence_duration,
                    'speech_percentage': analysis.speech_percentage,
                    'segment_count': analysis.segment_count
                },
                'segments': transcription_results
            }, f, indent=2)
        logger.info(f"JSON output saved to: {json_path}")
        
        # Save plain text format
        text_path = f"{self.base_path}.txt"
        with open(text_path, 'w') as f:
            for segment in transcription_results:
                start_time = segment['start'] / 1000  # Convert to seconds
                end_time = segment['end'] / 1000
                f.write(f"[{start_time:.2f}s - {end_time:.2f}s] {segment['text']}\n")
        logger.info(f"Text output saved to: {text_path}")
