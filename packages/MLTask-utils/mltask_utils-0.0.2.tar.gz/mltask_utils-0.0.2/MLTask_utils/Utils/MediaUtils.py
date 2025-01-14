from moviepy import VideoFileClip, AudioFileClip


def get_media_duration_seconds(file_path):
    try:
        print("creating clip 1")
        clip = AudioFileClip(file_path)
        print("getting duration")
        duration = clip.duration

        print(f"dration = {duration}")
        clip.close()
        return duration
    except Exception as e:
        print("Error loading video file:", str(e))
        return None
