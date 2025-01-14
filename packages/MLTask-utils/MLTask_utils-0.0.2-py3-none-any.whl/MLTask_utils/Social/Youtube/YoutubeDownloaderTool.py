from pprint import pprint
from typing import Annotated, List
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.http import MediaIoBaseDownload
from MLTask_utils.Social.Youtube.YoutubeManager import get_youtube_api_client
import io
import uuid
from yt_dlp import YoutubeDL


def download_video(url, output_path="./out/youtube", format='best'):
    """
    Download a YouTube video using yt-dlp

    Args:
        url (str): YouTube video URL
        output_path (str, optional): Directory to save the video. Defaults to current directory.
        format (str, optional): Video format/quality. Defaults to 'best'.

    Returns:
        dict: Information about the downloaded video
    """
    # Configure yt-dlp options
    ydl_opts = {
        'format': format,  # You can specify quality like '137+140' for 1080p+audio
        'outtmpl': '%(title)s.%(ext)s',  # Output template
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'no_warnings': False,
        'quiet': False,
        'extract_flat': False,
    }

    # If output path is specified, add it to options
    if output_path:
        ydl_opts['outtmpl'] = f'{output_path}/%(title)s.%(ext)s'

    try:
        # Create YoutubeDL object with options
        with YoutubeDL(ydl_opts) as ydl:
            # Download the video and get info
            info = ydl.extract_info(url, download=True)
            return info

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


# def download_video(youtube_url, output_path='Social/youtube', filename='yt_downloaded.mp4'):
#     """
#     Download a video from YouTube using its URL.

#     Parameters:
#         youtube_url (str): The URL of the YouTube video.
#         output_path (str): The directory path to save the downloaded video.
#             Defaults to 'Social/youtube'.
#         filename (str): The name of the downloaded video file.
#             Defaults to 'yt_downloaded.mp4'.

#     Returns:
#         str: The path of the downloaded video file.

#     Raises:
#         ValueError: If the provided YouTube URL is invalid.
#         IOError: If an error occurs while downloading the video.
#         OSError: If the output path does not exist or is inaccessible.

#     Usage:
#         download_video('https://www.youtube.com/watch?v=VIDEO_ID', output_path='videos', filename='my_video.mp4')
#     """
#     yt = YouTube(youtube_url)
#     yt.streams.get_highest_resolution().download(
#         output_path=output_path, filename=filename)
#     return f"{output_path}/{filename}"


def download_youtube_audio(
    youtube_url: Annotated[str, "Youtube URL"],
    out_directory_path: Annotated[
        str, "the output directory name that contains the audio file"
    ] = "./out/youtube/audio",
    filename: Annotated[
        str, "downloaded youtube video filename without extension"
    ] = str(uuid.uuid4()),
) -> str:
    youtube = YouTube(youtube_url)
    video = youtube.streams.get_audio_only()
    return video.download(filename=f"{filename}.mp3", output_path=out_directory_path)


def download_youtube_transcript(video_id):
    # yt = YouTube(f"http://youtube.com/watch?v={video_id}")
    # yt.bypass_age_gate()
    # pprint(yt.captions.get_by_language_code("a.en").generate_srt_captions())
    # trash doesnt work
    res = YouTubeTranscriptApi.get_transcript(video_id)
    transcript = ""
    for entry in res:
        transcript += entry["text"] + " "

    return (res, transcript)
    # # arry of dict with 3 keys duration start and text
    # pprint(res)


def fetch_caption(video_id, user_oauth_token, user_oauth_refresh_token):
    youtube = get_youtube_api_client(
        user_oauth_token, user_oauth_refresh_token)

    request = youtube.captions().list(
        part="snippet",
        videoId=video_id
    )
    response = request.execute()

    ret_caption_id = ""
    for caption in response['items']:
        # AUieDaYi1qTUcJejkALXEiG_mZ13qTXuEAUbTq18uK41AA7gya8
        caption_id = caption['id']
        ret_caption_id = caption_id
        snippet = caption['snippet']
        language = snippet['language']
        print(language, caption_id)

    return ret_caption_id


def download_caption(caption_id, user_oauth_token, user_oauth_refresh_token):
    # potentially useless
    # throws 403 (forbidden) when used on videos that the authenticated users didn't upload....
    youtube = get_youtube_api_client(
        user_oauth_token, user_oauth_refresh_token)

    request = youtube.captions().download(
        id=caption_id
    )
    fh = io.FileIO("Social/youtube/caption.txt", "wb")

    download = MediaIoBaseDownload(fh, request)
    complete = False
    while not complete:
        status, complete = download.next_chunk()
