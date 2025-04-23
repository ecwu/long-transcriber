# Long Audio Transcriber

A Python tool that efficiently transcribes long audio files using OpenAI's API. It automatically detects and extracts speech segments, removing silence to optimize API usage. Processes segments asynchronously and provides timestamped output in multiple formats.

## Features

- Smart silence detection to extract only speech segments
- Asynchronous processing for faster transcription
- Multiple output formats (JSON, SRT, TXT) with timestamps
- Dry run mode for speech analysis and silence removal
- Configurable silence detection parameters
- Supports various audio formats (mp3, wav, etc.)

## Installation

1. Clone the repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```
3. Set your OpenAI API key (not required for dry run mode):
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## Usage

### Basic Transcription
```bash
python main.py input_file.mp3 output_file
```

### Dry Run Mode
To analyze speech segments and create a speech-only audio file without transcription:
```bash
python main.py input_file.mp3 output_file --dry-run
```
This will generate:
- A speech-only audio file with silence removed
- A detailed analysis report with timing information
- No API calls are made in this mode

### Custom Silence Detection
```bash
python main.py input_file.mp3 output_file \
    --silence-thresh -45 \
    --min-silence 700 \
    --keep-silence 150
```

### Arguments
- `input_file`: Path to the audio file you want to transcribe
- `output_file`: Base path for output files (will generate multiple formats)
- `--silence-thresh`: Silence threshold in dB (default: -40)
- `--min-silence`: Minimum silence length in milliseconds (default: 500)
- `--keep-silence`: Amount of silence to keep at segment boundaries in milliseconds (default: 100)
- `--dry-run`: Run in analysis mode without transcription

### Output Formats

For transcription mode:
1. **JSON** (`output_file.json`):
   - Detailed format with precise timestamps
   - Includes duration for each segment
   - Useful for post-processing or analysis

2. **SRT** (`output_file.srt`):
   - Standard subtitle format
   - Compatible with video players
   - Perfect for video subtitling

3. **Text** (`output_file.txt`):
   - Human-readable format
   - Includes timestamps for reference
   - Easy to read and edit

For dry run mode:
1. **Speech-only audio** (`output_file_speech_only.ext`):
   - Original audio with silence removed
   - Same format as input file
   - Useful for manual verification

2. **Analysis report** (`output_file_analysis.txt`):
   - Total duration statistics
   - Speech vs. silence ratio
   - Detailed segment timings
   - Compression metrics

## Silence Detection Parameters

- **silence-thresh**: The threshold (in dB) below which the audio is considered silence. Lower values mean more aggressive silence detection.
- **min-silence**: The minimum length of silence (in ms) to be considered a break between speech segments.
- **keep-silence**: The amount of silence (in ms) to keep at the beginning and end of each segment.

## Note

Make sure you have FFmpeg installed on your system as it's required by pydub for audio processing:

- On macOS: `brew install ffmpeg`
- On Ubuntu/Debian: `sudo apt-get install ffmpeg`
- On Windows: Download from [FFmpeg website](https://www.ffmpeg.org/download.html)
