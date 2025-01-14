from typing import Annotated, List, Literal
from googleapiclient.http import MediaFileUpload
from .YoutubeManager import (
    get_youtube_api_client,
    fetch_popular_tags,
)
from MLTask_utils.Utils.ImageUtils import reduce_image_size
from MLTask_utils.Utils.ArrayUtils import get_first_middle_and_last_item

YOUTUBE_TITLE_MAX_LENGTH = 100
YOUTUBE_CAPTION_MAX_LENGTH = 5000
YOUTUBE_TAGS_LENGTH = 500


def are_tags_valid(tags):
    tags_string = ",".join(tags)
    space_needed_for_commas = 2 * len(tags)
    return len(tags_string) + space_needed_for_commas < YOUTUBE_TAGS_LENGTH


def upload_video_to_youtube(
    title: Annotated[str, "title of the youtube video"],
    description: Annotated[str, "the description of the youtube video"],
    tags: Annotated[List[str], "the list of tags to use in the youtube video"],
    video_file_path: Annotated[str, "local video filepath to upload to youtube"],
    thumbnail_file_path: Annotated[
        str, "the filepath of the thumbnail to use in the youtube video"
    ],
    user_oauth_token: Annotated[str, "the user oauth token"],
    user_oauth_refresh_token: Annotated[str, "the user oauth refresh token"],
    isShorts: Annotated[
        bool, "whether it's a youtube short or a regular long form video"
    ] = True,
    notifySubscribers: Annotated[
        bool, "wheter to notify your subscribers of a viedo or not"
    ] = False,
    is_public: Annotated[
        bool, "the privacy level for the video, True for public, False for private"
    ] = False,
    madeForKids: Annotated[bool, "is this video made for kids"] = False,
    category_name: Annotated[
        Literal[
            "Film & Animation",
            "Autos & Vehicles",
            "Music",
            "Pets & Animals",
            "Sports",
            "Travel & Events",
            "Gaming",
            "People & Blogs",
            "Comedy",
            "Entertainment",
            "News & Politics",
            "Howto & Style",
            "Education",
            "Science & Technology",
            "Nonprofits & Activism",
        ],
        "the category of the youtube video",
    ] = "Pets & Animals",
) -> None:

    best_world_tags = fetch_popular_tags(
        user_oauth_token, user_oauth_refresh_token)
    print(best_world_tags)
    tags = get_first_middle_and_last_item(best_world_tags) + tags.split(',')

    reduce_image_size(thumbnail_file_path, 2 * 1024 * 1024)
    youtube = get_youtube_api_client(
        user_oauth_token, user_oauth_refresh_token)
    SHORTS_LABEL_AND_SPACE_CHAR_LENGTH = 8
    video_title = f"{title[:YOUTUBE_TITLE_MAX_LENGTH -
                           SHORTS_LABEL_AND_SPACE_CHAR_LENGTH]} {'#shorts' if isShorts == True else ''}"

    while are_tags_valid(tags) == False:
        tags.pop()

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "categoryId": categories[category_name],
                "description": description[:YOUTUBE_CAPTION_MAX_LENGTH],
                "title": video_title,
                "tags": tags,
            },
            "status": {
                "privacyStatus": "public" if is_public == True else "private",
                # 'publishAt': upload_date_time,
                "selfDeclaredMadeForKids": madeForKids,
            },
            "notifySubscribers": notifySubscribers,
        },
        media_body=MediaFileUpload(video_file_path),
        # media_body=MediaFileUpload(open(video_file_path, 'rb').read())
    )
    response = request.execute()
    youtube.thumbnails().set(
        videoId=response.get("id"), media_body=MediaFileUpload(thumbnail_file_path)
    ).execute()
    print(response)


# https://developers.google.com/youtube/v3/docs/videoCategories/list
categories = {
    "Film & Animation": "1",
    "Autos & Vehicles": "2",
    "Music": "10",
    "Pets & Animals": "15",
    "Sports": "17",
    "Travel & Events": "19",
    "Gaming": "20",
    "People & Blogs": "22",
    "Comedy": "23",
    "Entertainment": "24",
    "News & Politics": "25",
    "Howto & Style": "26",
    "Education": "27",
    "Science & Technology": "28",
    "Nonprofits & Activism": "29",
}
