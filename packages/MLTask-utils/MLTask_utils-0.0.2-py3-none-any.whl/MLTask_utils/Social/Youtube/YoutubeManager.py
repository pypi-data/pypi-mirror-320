import google.oauth2.credentials
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload
from .YoutubeAuthenticator import get_creds


def get_youtube_api_client(user_oauth_token, user_oauth_refresh_token):
    api_service_name = "youtube"
    api_version = "v3"
    return googleapiclient.discovery.build(
        api_service_name,
        api_version,
        credentials=google.oauth2.credentials.Credentials(
            **get_creds(user_oauth_token, user_oauth_refresh_token)
        ),
    )


def post_to_live_chat(
    live_chat_id, message_text, user_oauth_token, user_oauth_refresh_token
):
    youtube = get_youtube_api_client(
        user_oauth_token, user_oauth_refresh_token)
    request = youtube.liveChatMessages().insert(
        part="snippet",
        body={
            "snippet": {
                "liveChatId": live_chat_id,
                "type": "textMessageEvent",
                "textMessageDetails": {"messageText": message_text},
            }
        },
    )
    response = request.execute()


def fetchPopularVids(user_oauth_token, user_oauth_refresh_token):
    youtube = get_youtube_api_client(
        user_oauth_token, user_oauth_refresh_token)
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics", chart="mostPopular", regionCode="US"
    )
    return request.execute()


def fetch_popular_tags(user_oauth_token, user_oauth_refresh_token):
    popular_vids = fetchPopularVids(user_oauth_token, user_oauth_refresh_token)
    unique_strings = set()
    accumulated_tags = []
    for item in popular_vids["items"]:
        snippet = item["snippet"]
        if "tags" in snippet:
            tags = snippet["tags"]
            for tag in tags:
                if tag not in unique_strings:
                    accumulated_tags.append(tag)
                    unique_strings.add(tag)

    final_tags = sorted(accumulated_tags)
    # print(final_tags)
    # print('[%s]' % ', '.join(map(str, final_tags)))
    return final_tags
