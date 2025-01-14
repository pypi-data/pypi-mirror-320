import os
import uuid
import subprocess


def download_titktok_from_url(
    url, out_directory_path="./out/tiktoks", filename=str(uuid.uuid4())
):
    os.makedirs(out_directory_path, exist_ok=True)
    final_output_video_filepath = os.path.join(out_directory_path, f"{filename}.mp4")

    command = ["yt-dlp", url, "-o", final_output_video_filepath]
    subprocess.run(command, check=True)

    return os.path.abspath(final_output_video_filepath)
