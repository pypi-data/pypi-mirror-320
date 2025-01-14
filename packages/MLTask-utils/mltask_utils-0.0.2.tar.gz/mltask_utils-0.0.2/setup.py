from setuptools import setup, find_packages


VERSION = "0.0.2"
DESCRIPTION = "a collection of commonly used tools by MLTask"
LONG_DESCRIPTION = "TBD"

# Setting up
setup(
    name="MLTask_utils",
    version=VERSION,
    author="Mister Joessef",
    author_email="<misterjoessef@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=["requests",
                      "torch",
                      "openai-whisper",
                      "whisperx",
                      "openai",
                      "pillow",
                      "boto3",
                      "instagrapi",
                      "pinterest-api-sdk",
                      "stability-sdk",
                      #   "socketio",
                      "twitchio",
                      "requests_oauthlib",
                      "google_auth_oauthlib",
                      "google-api-python-client",
                      "pytube",
                      "youtube_transcript_api",
                      "qrcode",
                      "gql",
                      "numpy",
                      "pydub",
                      "scipy",
                      "opencv-python",
                      "moviepy",
                      "imageio",
                      "librosa",
                      "yt-dlp[default]"],
    keywords=[
        "mltask",
    ],
)
