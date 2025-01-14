from moviepy import VideoFileClip, ColorClip, TextClip, concatenate_videoclips
from moviepy.video import fx

from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip


from MLTask_utils.Utils.MoviePyUtils import shake

# reference usage
# timestamps = beat_69(beatr_filename, 0.5, 0.2)
#     gif_data = [
#         {
#             "timestamp": timestamp,
#             "gif_path": f"Social/youtube/gifs/sample {1 + i%21}.gif",
#         }
#         for i, timestamp in enumerate(timestamps)
#     ]
#     output_path = insert_gif_screens(gif_data, beatr_filename, "output.mp4")


def insert_gif_screens(gif_inputs, input_video_path, output_video_path):
    """
    Inserts GIF screens into a video at specified timestamps.

    Args:
        gif_inputs (list): A list of dictionaries, each containing 'timestamp', and 'gif_path'
        input_video_path (str): Path to the input video file.
        output_video_path (str): Path to save the output video file.

    Returns:
        str: Path of the output video file.

    Raises:
        OSError: If the input video file cannot be loaded.
        OSError: If the output video file cannot be written.

    Note:
        - This function uses the moviepy library to process the video.
        - The timestamps in the gif_inputs list should be in ascending order.
        - The output video file will be encoded using the libx264 codec and the audio will be encoded using the AAC codec.
    """
    video = VideoFileClip(input_video_path)

    clips = []
    # clips.append(video)
    background_screen = ColorClip(
        (512, 512), duration=video.duration, color=[0, 0, 0])

    background_screen = background_screen.set_audio(video.audio)

    clips.append(background_screen)

    intro_clip = TextClip("Animate Diff", fontsize=70, color="red",
                          bg_color="transparent", size=(512, 512))
    intro_clip = intro_clip.set_duration(3)

    clips.append(intro_clip)

    # Iterate through the timestamps and insert white screens
    input_lengths = len(gif_inputs)
    for i, gif_input in enumerate(gif_inputs):

        timestamp = gif_input['timestamp']
        gif_path = gif_input['gif_path']
        gif_clip = VideoFileClip(gif_path)

        gif_duration = gif_clip.duration

        next_timestep = gif_inputs[i + 1]['timestamp'] if i + \
            1 < input_lengths else 99999999

        if timestamp + gif_duration > next_timestep:
            gif_duration = next_timestep - timestamp

        gif_clip = gif_clip.set_pos('center').set_start(
            timestamp).set_duration(gif_duration)
        clips.append(gif_clip)

        shaken_video = fx.SlideIn(gif_clip, 0.02, 'left').set_pos(lambda t: shake(t, (0, 0))).set_start(
            timestamp).set_duration(0.1)

        clips.append(shaken_video)

    # Add the remaining part of the video after the last timestamp

    # Concatenate all the clips together
    final_video = CompositeVideoClip(clips)

    # Write the final video to the output path
    final_video.write_videofile(
        output_video_path, codec='libx264', audio_codec='aac')
    # final_video.write_videofile(
    #     output_video_path, codec='libx264', audio_codec='aac', bitrate='5000k', preset='slow')
    return output_video_path
