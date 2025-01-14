from moviepy import VideoFileClip, TextClip, ColorClip, concatenate_videoclips
from moviepy.video.fx import loop
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip


def insert_white_screens(timestamps, input_video_path, output_video_path, flash_duration=0.1):
    """
    Inserts white screens into a video at specified timestamps.

    Args:
        timestamps (list): A list of timestamps (in seconds) where white screens should be inserted.
        input_video_path (str): Path to the input video file.
        output_video_path (str): Path to save the output video file.
        flash_duration (float, optional): Duration (in seconds) of the white screen flash. 
            Defaults to 0.1 seconds.

    Returns:
        str: Path of the output video file.

    Raises:
        OSError: If the input video file cannot be loaded.
        OSError: If the output video file cannot be written.

    Note:
        - This function uses the moviepy library to process the video.
        - The timestamps list should be in ascending order.
        - The output video file will be encoded using the libx264 codec and the audio will be encoded using the AAC codec.
    """
    # Load the input video
    video = VideoFileClip(input_video_path)

    clips = []
    previous_time = 0

    # Iterate through the timestamps and insert white screens
    for timestamp in timestamps:
        # Calculate the duration between the current and previous timestamps
        duration = timestamp - previous_time

        # Add the original video clip
        clips.append(video.subclip(previous_time, timestamp - flash_duration))

        # Create a white screen clip with the same duration and overlay it on the original clip
        white_screen = ColorClip(
            (video.w, video.h), duration=duration, color=[255, 255, 255])
        # Remove audio from the white screen clip
        white_screen = white_screen.set_audio(None)
        # Set the duration of the white screen clip
        white_screen = white_screen.set_duration(flash_duration)

        # Overlay the white screen clip on the original clip
        overlay_clip = CompositeVideoClip(
            [video.subclip(timestamp - flash_duration, timestamp), white_screen])

        # Add the overlay clip
        clips.append(overlay_clip)

        # Update the previous timestamp
        previous_time = timestamp

    # Add the remaining part of the video after the last timestamp
    clips.append(video.subclip(previous_time))

    # Concatenate all the clips together
    final_video = concatenate_videoclips(clips)

    # Write the final video to the output path
    final_video.write_videofile(
        output_video_path, codec='libx264', audio_codec='aac')
    return output_video_path
