import os
from moviepy import vfx
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy import TextClip, ImageClip, AudioFileClip, vfx, ColorClip
from .ImageUtils import get_dominant_color, blur_image
from .FileUtils import get_file_extension
from .MathUtils import lerp
import uuid

import cv2

import os
import subprocess


def convert_mp4_to_mov(
    input_file, output_dir="./out/mov_convertion", output_filename=uuid.uuid4()
):
    os.makedirs(output_dir, exist_ok=True)
    final_output_video_filepath = os.path.join(
        output_dir, f"{output_filename}.mov")

    # clip = VideoFileClip(input_file)
    # clip.write_videofile(final_output_video_filepath, codec='prores')
    # clip.close()

    command = [
        "ffmpeg",
        "-i",
        input_file,
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        final_output_video_filepath,
    ]
    subprocess.run(command, check=True)

    return final_output_video_filepath


def get_frame_as_image(video_path, time):
    # Load the video clip
    video_clip = VideoFileClip(video_path)

    # Get the frame at the specified time
    frame = video_clip.get_frame(time)

    # Convert the frame to BGR format (OpenCV uses BGR)
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    return frame_bgr


def aspect_fit(
    target_width,
    target_height,
    input_file,
    output_dir="/home/autogen/AgentsAndChains",
    output_filename=uuid.uuid4(),
):
    # Load the video clip
    video_clip = VideoFileClip(input_file)

    # Get the original dimensions
    original_width, original_height = video_clip.size

    aspect_ratio_target = target_width / target_height
    aspect_ratio_clip = original_width / original_height
    if aspect_ratio_clip > aspect_ratio_target:
        # Scale based on width
        scaled_width = target_width
        scaled_height = int(target_width / aspect_ratio_clip)
    else:
        # Scale based on height
        scaled_height = target_height
        scaled_width = int(target_height * aspect_ratio_clip)
    print(scaled_width, scaled_height)
    # Resize the video clip

    os.makedirs(output_dir, exist_ok=True)
    final_output_video_filepath = os.path.join(
        output_dir, f"{output_filename}.mp4")

    frame_image = get_frame_as_image(input_file, 1)
    output_image_path = "output_frame_image.jpg"
    cv2.imwrite(output_image_path, frame_image)
    background_blurr = ImageClip(blur_image(
        output_image_path, "blurred.png", 200))

    final_clip = CompositeVideoClip(
        [
            background_blurr.set_duration(video_clip.duration)
            .set_position(lambda t: ("center", "center"))
            .fx(vfx.resize, lambda t: lerp(2, 2.1, t / video_clip.duration)),
            video_clip.fx(
                vfx.resize, width=scaled_width, height=scaled_height
            ).set_position(lambda t: ("center", "center")),
        ],
        size=(target_width, target_height),
    )

    final_clip.set_duration(video_clip.duration)
    final_clip.write_videofile(final_output_video_filepath)

    # Close the video clips
    video_clip.close()
    # resized_clip.close()
    return os.path.abspath(final_output_video_filepath)


def cut_video(input_file, output_dir="/tmp", output_filename=uuid.uuid4()):
    # Load the video clip
    video_clip = VideoFileClip(input_file)
    if video_clip.duration <= 60:
        return input_file
    # Cut the video after 60 seconds
    clipped_video = video_clip.subclip(0, 60)

    # Write the clipped video to a new file

    os.makedirs(output_dir, exist_ok=True)
    final_output_video_filepath = os.path.join(
        output_dir, f"{output_filename}.mp4")

    # mp4

    clipped_video.write_videofile(final_output_video_filepath)

    # Close the video clip
    # video_clip.close()

    return os.path.abspath(final_output_video_filepath)
