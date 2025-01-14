import librosa
# import matplotlib.pyplot as plt
import numpy as np
from moviepy import VideoFileClip
from pprint import pprint
import scipy.signal
from pydub import AudioSegment

import subprocess
import os
import shlex


def split_mp3(input_file, chunk_size_mb):
    """
    Splits an MP3 file into smaller chunks of at most the specified file size.

    Args:
        input_file (str): Path to the input MP3 file.
        chunk_size_mb (int): Maximum file size in megabytes for each chunk.

    Returns:
        None

    Raises:
        FileNotFoundError: If the input_file does not exist.
    """
    # Load the MP3 file
    audio = AudioSegment.from_mp3(input_file)

    # Get the duration of the audio in milliseconds
    audio_duration = len(audio)

    # Calculate the chunk size in milliseconds
    chunk_size_ms = chunk_size_mb * 1024 * 1024 * 8 / audio.frame_rate

    # Calculate the total number of chunks
    total_chunks = int(audio_duration / chunk_size_ms) + 1

    # Create a directory to store the output chunks
    output_dir = os.path.splitext(input_file)[0]
    os.makedirs(output_dir, exist_ok=True)

    # Split the audio into chunks
    for i in range(total_chunks):
        start_time = i * chunk_size_ms
        end_time = min((i + 1) * chunk_size_ms, audio_duration)

        chunk = audio[start_time:end_time]

        # Generate the output filename
        output_file = os.path.join(output_dir, f"chunk{i+1}.mp3")

        # Export the chunk as an MP3 file
        chunk.export(output_file, format="mp3")

        print(f"Chunk {i+1} created: {output_file}")


def split_mp3_by_size(input_file_name, size_limit_in_bytes="24000000"):
    ffmpeg_args = "-c:v libx264 -crf 23 -c:a copy -vf scale=960:-1"
    # output_format = "mp3"
    output_format = ""

    script_path = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the Bash script in the same directory
    bash_script_path = os.path.join(
        script_path, 'split_audio_file_based_on_size.sh')

    command = f"{bash_script_path} {shlex.quote(input_file_name)} {
        size_limit_in_bytes} '{ffmpeg_args}' {output_format}"
    print("sending command")
    print(command)
    result = subprocess.run(command, shell=True, check=True,
                            capture_output=True, text=True)

    generated_chunks = result.stdout.splitlines()
    print(generated_chunks)
    return generated_chunks

# def split_mp3_by_minutes(input_file_name, chunk_size_in_minutes):
#     input_file_format = get_file_extension(input_file_name)
#     print(f" input_file_format = {input_file_format}")
#     audio = AudioSegment.from_file(input_file_name, format=input_file_format)

#     chunk_size_bytes = chunk_size_in_minutes * 60 * 1000
#     total_chunks = math.ceil(len(audio) / chunk_size_bytes)
#     output_dir = f'{os.path.splitext(input_file_name)[0]}_chunks'
#     os.makedirs(output_dir, exist_ok=True)
#     file_paths = []
#     print("about to start chunking")
#     for i in range(total_chunks):
#         start = i * chunk_size_bytes
#         end = (i + 1) * chunk_size_bytes
#         chunk = audio[start:end]
#         output_file = os.path.join(output_dir, f"chunk_{i + 1}.mp3")
#         print("about to export chunk")
#         chunk.export(output_file, format="mp3")
#         print("chuni exported moving on....")
#         file_paths.append(output_file)
#         # print(f"Chunk {i + 1}/{total_chunks} created: {output_file}")
#     print("all done here, returning all chunks")
#     return file_paths


def cleanup_array(arr, threshold):
    """
    Cleans up an array by removing elements that are closer than the specified threshold.

    Args:
        arr (list): The input array.
        threshold (float): The minimum difference allowed between consecutive elements.

    Returns:
        list: The cleaned array.

    Note:
        - The cleaned array is initialized with the first element of the input array.
        - Subsequent elements are added to the cleaned array only if they have a difference greater than or equal to the threshold from the previous element.
    """
    # Initialize the cleaned array with the first element
    cleaned_arr = [arr[0]]
    for i in range(1, len(arr)):
        if arr[i] - cleaned_arr[-1] >= threshold:
            cleaned_arr.append(arr[i])

    return cleaned_arr


def beat_42(audio_path, minPeak=7.5, time_between_threshold=0):
  # https://github.com/librosa/librosa/issues/1065
    """
    Detects beats in an audio file using the BEAT 42 algorithm.

    Args:
        audio_path (str): Path to the audio file.
        threshold (float, optional): RMS threshold for peak detection. Defaults to 0.1.
        time_between_threshold (float, optional): Minimum time between consecutive beats. Defaults to 0.

    Returns:
        list: Array of beat times.

    Note:
        - This function uses the librosa and scipy libraries for audio processing.
        - The hop_length is set to 512.
        - The beats are detected using the RMS values and peak detection.
        - The output is an array of beat times, cleaned up using the `cleanup_array` function with the specified `time_between_threshold`.
    """
    hop_length = 512
    y, sr = librosa.load(audio_path, sr=None)

    onset_env = librosa.onset.onset_strength(y=y, sr=sr,
                                             hop_length=hop_length,
                                             aggregate=np.median)
    onset_env[onset_env < minPeak] = 0
    peaks = librosa.util.peak_pick(
        onset_env, pre_max=4, post_max=4, pre_avg=4, post_avg=6, delta=2.1, wait=10)

    timestamps = librosa.frames_to_time(peaks, sr=sr, hop_length=hop_length)
    cleaned = np.floor(timestamps * 100) / 100
    # cleaned = cleaned[1:-1]
    cleaned = cleanup_array(cleaned, time_between_threshold)
    return cleaned


def beat_69(audio_path, threshold=0.1, time_between_threshold=0):
  # https://github.com/librosa/librosa/issues/1065
    """
    Detects beats in an audio file using the BEAT 69 algorithm.

    Args:
        audio_path (str): Path to the audio file.
        threshold (float, optional): RMS threshold for peak detection. Defaults to 0.1.
        time_between_threshold (float, optional): Minimum time between consecutive beats. Defaults to 0.

    Returns:
        list: Array of beat times.

    Note:
        - This function uses the librosa and scipy libraries for audio processing.
        - The hop_length is set to 512.
        - The beats are detected using the RMS values and peak detection.
        - The output is an array of beat times, cleaned up using the `cleanup_array` function with the specified `time_between_threshold`.
    """
    hop_length = 512

    y, sr = librosa.load(audio_path, sr=None)
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0, :]
    peak_locs = scipy.signal.find_peaks(rms, height=threshold)[0]
    # peak_heights = rms[peak_locs]

    times = librosa.times_like(rms, hop_length=hop_length, sr=sr)
    return cleanup_array(times[peak_locs], time_between_threshold)


def get_timestamp_of_amplitude(audio_path, high_filter=0.9, low_filter=-0.9):
    # Load the audio file
    y, sr = librosa.load(audio_path)

    # Calculate the duration of the audio in seconds
    duration = librosa.get_duration(y=y, sr=sr)

    # Calculate the time values for x-axis
    times = np.linspace(0, duration, len(y))

    # Find the indices where amplitude is greater than the threshold
    indices = np.where((y > high_filter) | (y < low_filter))[0]

    times_high_amplitude = times[indices]
    return times_high_amplitude

    # # Plot the amplitude waveform
    # plt.figure(figsize=(14, 5))
    # plt.plot(times, y)
    # plt.axhline(y=high_filter, color='red', linestyle='--', linewidth=1.5)  # Add red horizontal line at the threshold
    # plt.axhline(y=low_filter, color='red', linestyle='--', linewidth=1.5)  # Add red horizontal line at the threshold
    # plt.scatter(times[indices], y[indices], color='red', s=30, label=f'high Amplitude > {high_filter}')  # Add circles for values > threshold
    # plt.scatter(times[indices], y[indices], color='red', s=30, label=f'low Amplitude > {low_filter}')  # Add circles for values > threshold

    # plt.title('Amplitude Waveform')
    # plt.xlabel('Time (seconds)')
    # plt.ylabel('Amplitude')

    # count = len(indices)
    # plt.text(0.05, 0.95, f"Count: {count}", transform=plt.gca().transAxes, fontsize=12,
    #         verticalalignment='top', bbox=dict(facecolor='white', alpha=0.8))

    # plt.legend()
    # plt.show()
