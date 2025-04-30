#!/usr/bin/env python3

import argparse
import yaml
import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

from src.transcription import transcribe_audio
from src.analysis import analyze_transcript
from src.discovery_sheet import generate_discovery_sheet
from src.apollo import get_apollo_recording
from src.export import export_discovery_sheet


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading config from {config_path}: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Customer Discovery Meeting Minutes Agent - Generate customer discovery sheets from call recordings")
    
    # Input sources
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--recording', type=str, help='Path to a local audio recording file')
    input_group.add_argument('--apollo-call-id', type=str, help='Apollo.io call ID to process')
    input_group.add_argument('--batch', action='store_true', help='Process multiple recordings in batch mode')
    
    # Batch processing options
    parser.add_argument('--apollo-date-range', type=str, help='Date range for batch processing (format: YYYY-MM-DD,YYYY-MM-DD)')
    parser.add_argument('--input-dir', type=str, help='Directory containing audio files for batch processing')
    
    # Output options
    parser.add_argument('--output', type=str, help='Output file path for the discovery sheet')
    parser.add_argument('--output-dir', type=str, help='Output directory for batch processing')
    parser.add_argument('--format', type=str, choices=['markdown', 'csv', 'json', 'pdf'], help='Output format (default: from config)')
    
    # Configuration
    parser.add_argument('--config', type=str, default='config.yml', help='Path to configuration file')
    parser.add_argument('--template', type=str, help='Path to custom template file')
    
    # API Keys (override config)
    parser.add_argument('--openai-api-key', type=str, help='OpenAI API key (overrides config)')
    parser.add_argument('--apollo-api-key', type=str, help='Apollo API key (overrides config)')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with command line args if provided
    if args.openai_api_key:
        config['api']['openai']['api_key'] = args.openai_api_key
    if args.apollo_api_key:
        config['api']['apollo']['api_key'] = args.apollo_api_key
    
    # Set output format
    output_format = args.format or config['export']['default_format']
    
    # Process single recording
    if args.recording or args.apollo_call_id:
        process_single_recording(args, config, output_format)
    
    # Process batch
    elif args.batch:
        process_batch(args, config, output_format)


def process_single_recording(args, config, output_format):
    """Process a single recording and generate a discovery sheet."""
    try:
        # Get the audio file path - either local or from Apollo
        audio_path = None
        if args.recording:
            audio_path = args.recording
            print(f"Processing local recording: {audio_path}")
        elif args.apollo_call_id:
            print(f"Fetching Apollo.io recording with ID: {args.apollo_call_id}")
            audio_path = get_apollo_recording(args.apollo_call_id, config)
        
        # Validate output path
        if not args.output:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"discovery_sheet_{timestamp}.{output_format}"
            output_path = os.path.join(config['export']['output_dir'], output_file)
        else:
            output_path = args.output
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Process the recording
        print("Transcribing audio...")
        transcript = transcribe_audio(audio_path, config)
        
        print("Analyzing transcript...")
        analysis = analyze_transcript(transcript, config)
        
        print("Generating discovery sheet...")
        discovery_sheet = generate_discovery_sheet(analysis, config)
        
        print(f"Exporting discovery sheet to {output_path}...")
        export_discovery_sheet(discovery_sheet, output_path, output_format, config)
        
        print("✅ Discovery sheet generated successfully!")
        return output_path
    
    except Exception as e:
        print(f"Error processing recording: {e}")
        return None


def process_batch(args, config, output_format):
    """Process multiple recordings in batch mode."""
    if not args.output_dir:
        output_dir = config['export']['output_dir']
    else:
        output_dir = args.output_dir
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    results = []
    
    if args.apollo_date_range:
        # Process Apollo recordings in date range
        start_date, end_date = args.apollo_date_range.split(',')
        print(f"Fetching Apollo.io recordings from {start_date} to {end_date}...")
        # Implementation of batch Apollo processing would go here
        # For each recording, call process_single_recording
    
    elif args.input_dir:
        # Process local recordings in directory
        print(f"Processing recordings in directory: {args.input_dir}")
        for filename in os.listdir(args.input_dir):
            if filename.endswith(('.mp3', '.wav', '.m4a', '.opus')):
                file_path = os.path.join(args.input_dir, filename)
                base_name = os.path.splitext(filename)[0]
                output_path = os.path.join(output_dir, f"{base_name}.{output_format}")
                
                # Create args for this file
                file_args = argparse.Namespace(
                    recording=file_path,
                    apollo_call_id=None,
                    output=output_path,
                    **{k: v for k, v in vars(args).items() if k not in ['recording', 'apollo_call_id', 'output']}
                )
                
                result = process_single_recording(file_args, config, output_format)
                if result:
                    results.append(result)
    
    print(f"✅ Batch processing complete. Generated {len(results)} discovery sheets in {output_dir}")


if __name__ == "__main__":
    main()
