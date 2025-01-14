from typing import Annotated, List, Dict, Any
import whisper
import uuid
import os
from MLTask_utils.Utils.SRTUtils import format_srt_entry
import whisperx
import torch
from typing import Optional, Dict, Any
import yt_dlp


# def get_diarized_transcript(audio_path: str, model_size: str = "tiny") -> Dict[str, Any]:
#     """
#     Generate a diarized transcript using WhisperX

#     Args:
#         audio_path: Path to the audio file
#         model_size: Size of the Whisper model ('tiny', 'base', 'small', 'medium')

#     Returns:
#         Dict containing the diarized transcript
#     """
#     try:
#         device = "cpu"
#         torch.set_default_tensor_type(
#             torch.FloatTensor)  # Force CPU tensor type
#         print(f"Using device: {device}")

#         # Load ASR model with explicit compute_type
#         model = whisperx.load_model(
#             model_size,
#             device,
#             compute_type="int8",  # Use int8 quantization for CPU
#             asr_options={"beam_size": 1}  # Reduce memory usage
#         )

#         # Transcribe audio
#         result = model.transcribe(
#             audio_path,
#             batch_size=1  # Smaller batch size for CPU
#         )

#         # Align whisper output
#         model_a, metadata = whisperx.load_align_model(
#             language_code=result["language"],
#             device=device
#         )
#         result = whisperx.align(
#             result["segments"],
#             model_a,
#             metadata,
#             audio_path,
#             device,
#             return_char_alignments=False
#         )

#         # Load diarization pipeline
#         diarize_model = whisperx.DiarizationPipeline(
#             use_auth_token=None,
#             device=device
#         )

#         # Get diarization result
#         diarize_segments = diarize_model(
#             audio_path,
#             min_speakers=1,
#             max_speakers=2
#         )

#         # Assign speaker labels
#         result = whisperx.assign_word_speakers(diarize_segments, result)

#         return result

#     except Exception as e:
#         print(f"Error during transcription/diarization: {str(e)}")
#         print(f"Full error details: {str(e.__class__.__name__)}")
#         return None


def download_audio(url: str, output_dir: str = "./") -> Optional[str]:
    """
    Download audio from a YouTube video using yt-dlp

    Args:
        url: YouTube video URL
        output_dir: Directory to save the audio file

    Returns:
        str: Path to the downloaded audio file
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            audio_path = os.path.join(output_dir, f"{info['title']}.wav")
            return audio_path
    except Exception as e:
        print(f"Error downloading audio: {str(e)}")
        return None


def transcribe_video(
    filepath: Annotated[str, "path of the video file"],
    out_directory_path: Annotated[
        str, "the output directory name that contains the transcript"
    ] = "./out/transcripts",
    output_transcript_srt: Annotated[
        str, "generated srt filename without extension"
    ] = str(uuid.uuid4()),
) -> Annotated[
    List[str],
    "a list wit exactly 2 entries the first is the local full filepath, and the second is the full transcript text",
]:
    try:
        audio = whisper.load_audio(filepath)
        model = whisper.load_model("tiny")
        result = model.transcribe(audio, word_timestamps=True)
        # Initialize variables for transcript
        transcript = []
        # Iterate through the segments in the result
        count = 0
        final_transcript = ""
        for segment in result["segments"]:
            current_transcript = segment["text"].strip()
            final_transcript += current_transcript + "\n"

            for word in segment["words"]:
                count += 1
                transcript.append(
                    # format_srt_entry(count, segment["start"], segment["end"], current_transcript)
                    format_srt_entry(
                        count, word["start"], word["end"], word["word"])
                )
        srt_text = "\n\n".join(transcript)

        os.makedirs(out_directory_path, exist_ok=True)
        final_output_video_filepath = os.path.join(
            out_directory_path, f"{output_transcript_srt}.srt"
        )

        with open(final_output_video_filepath, "w") as srt_file:
            srt_file.write(srt_text)

        return (os.path.abspath(final_output_video_filepath), final_transcript)

    except FileNotFoundError:
        print("The specified audio file could not be found.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return None
