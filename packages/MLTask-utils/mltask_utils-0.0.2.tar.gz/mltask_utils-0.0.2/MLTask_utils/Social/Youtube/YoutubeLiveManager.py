from MLTask_utils.Social.Youtube.YoutubeManager import get_youtube_api_client


def fetch_live_video_comments(live_chat_id, user_oauth_token, user_oauth_refresh_token, max_results=500, profile_image_size=88):
    """
    Fetches live chat comments for a given live_chat_id.

    Args:
        live_chat_id (str): The ID retrieved from fetchVideoDetails, representing the video ID found in the address bar.
        max_results (int): The maximum number of comments to retrieve, ranging from 200 to 2000. Default is 500.
        profile_image_size (int): The size of the profile image (16 to 720). Default is 88.

    Returns:
        dict: A dictionary containing information about live chat messages.
            'kind' (str): Identifies the API resource's type.
            'etag' (str): The Etag of this resource.
            'nextPageToken' (str): Token for retrieving the next page in the result set.
            'pollingIntervalMillis' (int): Time, in milliseconds, before polling again for new messages.
            'offlineAt' (datetime): Date and time when the live stream went offline (if applicable).
            'pageInfo' (dict): Paging information for the result set.
                'totalResults' (int): Total number of results in the set.
                'resultsPerPage' (int): Number of results in the API response.
            'items' (list): List of live chat messages, each item being a liveChatMessage resource.
    """

    youtube = get_youtube_api_client(
        user_oauth_token, user_oauth_refresh_token)

    request = youtube.liveChatMessages().list(
        liveChatId=live_chat_id,
        part="snippet,authorDetails",
        maxResults=max_results,
        profileImageSize=profile_image_size
    )

    response = request.execute()
    return response


def fetchVideoDetails(video_id, user_oauth_token, user_oauth_refresh_token):
    # https://developers-dot-devsite-v2-prod.appspot.com/youtube/v3/docs/videos/list
    youtube = get_youtube_api_client(
        user_oauth_token, user_oauth_refresh_token)

    request = youtube.videos().list(
        part="snippet,contentDetails,statistics,liveStreamingDetails",
        id=video_id
    )
    response = request.execute()
    # pprint(response)
    # this is how to get the chat id
    # response["items"][0]["liveStreamingDetails"]["activeLiveChatId"]
    items = response["items"]
    live_chat_id = items[0]["liveStreamingDetails"]["activeLiveChatId"]
    return (items, live_chat_id)
