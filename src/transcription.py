import os
import tempfile
from typing import Dict, Any, Optional
import openai


def transcribe_audio(audio_path: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Transcribe audio file using OpenAI's Whisper API.
    
    Args:
        audio_path: Path to the audio file
        config: Application configuration
        
    Returns:
        Dict containing the transcript and metadata
    """
    # Configure OpenAI client
    openai.api_key = config['api']['openai']['api_key']
    
    # Get transcription settings
    transcription_config = config.get('transcription', {})
    language = transcription_config.get('language', 'en')
    speaker_diarization = transcription_config.get('speaker_diarization', True)
    
    print(f"Transcribing audio file: {audio_path}")
    
    try:
        with open(audio_path, "rb") as audio_file:
            # Call OpenAI API for transcription
            response = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                language=language,
                timestamp_granularities=["segment", "word"] if speaker_diarization else ["segment"],
            )
        
        # Process and format the transcript
        segments = response.get('segments', [])
        
        # Format transcript with speaker diarization if enabled
        formatted_transcript = ""
        current_speaker = None
        
        for segment in segments:
            # In a real implementation, we would use a more sophisticated
            # speaker diarization approach. For this example, we'll alternate speakers
            # based on segments as a simple approximation.
            speaker = "Rep" if current_speaker != "Rep" else "Prospect"
            current_speaker = speaker
            
            start_time = segment.get('start', 0)
            text = segment.get('text', '').strip()
            
            # Format as: [MM:SS] Speaker: Text
            minutes = int(start_time) // 60
            seconds = int(start_time) % 60
            timestamp = f"[{minutes:02d}:{seconds:02d}]"
            
            formatted_transcript += f"{timestamp} {speaker}: {text}\n\n"
        
        return {
            "transcript": formatted_transcript,
            "raw_response": response,
            "audio_path": audio_path,
            "language": language,
            "duration": response.get('duration', 0)
        }
        
    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}")


def convert_audio_format(input_path: str, output_format: str = "mp3") -> str:
    """Convert audio to a format compatible with the transcription API.
    
    Args:
        input_path: Path to the input audio file
        output_format: Desired output format (default: mp3)
        
    Returns:
        Path to the converted audio file
    """
    try:
        import ffmpeg
        
        # Create temporary file for output
        temp_dir = tempfile.gettempdir()
        output_filename = f"converted_{os.path.basename(input_path)}.{output_format}"
        output_path = os.path.join(temp_dir, output_filename)
        
        # Convert using ffmpeg
        (ffmpeg
            .input(input_path)
            .output(output_path, acodec='libmp3lame', ar='16000', ac=1)
            .run(quiet=True, overwrite_output=True)
        )
        
        return output_path
        
    except ImportError:
        print("Warning: ffmpeg-python not available. Audio conversion skipped.")
        return input_path
    except Exception as e:
        print(f"Warning: Audio conversion failed: {e}. Using original file.")
        return input_path
