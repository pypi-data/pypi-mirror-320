from typing import Annotated, List, Dict, Any, Literal
from MLTask_utils.Utils.FileUtils import get_file_extension
from MLTask_utils.Social.Twitter.TwitterAuthenticator import get_credentials
from MLTask_utils.Social.Twitter.TwitterAPIWrapper import get_twitter_user_id
from MLTask_utils.Utils.MovieUtils import convert_mp4_to_mov
import os
from pprint import pprint
import time
import json


def post_tweet_video_or_gif(
    access_token: Annotated[str, "the user access token"],
    access_token_secret: Annotated[str, "the user access token secret"],
    tweet_dict: Annotated[
        Dict[str, Any],
        "a dictionary made up of 3 keys text, video_or_gif_path, and optinally in_reply_to_tweet_id",
    ],
):
    oauth = get_credentials(access_token, access_token_secret)
    twitter_user_id = get_twitter_user_id(access_token, access_token_secret)
    video_or_gif_path = tweet_dict["video_or_gif_path"]
    # Initialize video upload
    init_url = "https://upload.twitter.com/1.1/media/upload.json"
    extension = get_file_extension(video_or_gif_path)
    print("extension == " + extension)
    if extension == ".mp4":
        video_or_gif_path = convert_mp4_to_mov(video_or_gif_path)

    if extension == ".gif":
        media_type = "image/gif"
        media_category = "tweet_gif"
    elif extension == ".mp4":
        media_type = "video/mp4"
        media_category = "tweet_video"
    elif extension == ".mov":
        media_type = "video/mov"
        media_category = "tweet_video"
    else:
        media_type = "video/mp4"
        media_category = "tweet_video"

    init_params = {
        "command": "INIT",
        "additional_owners": twitter_user_id,
        "media_category": media_category,
        "media_type": media_type,
        "total_bytes": os.path.getsize(video_or_gif_path),
    }
    init_response = oauth.post(init_url, data=init_params)
    init_response_json = init_response.json()
    print(init_response_json)
    media_id_string = init_response_json["media_id_string"]

    # Append video chunks
    append_url = "https://upload.twitter.com/1.1/media/upload.json"
    segment_id = 0
    chunk_size = 4 * 1024 * 1024  # 4MB
    with open(video_or_gif_path, "rb") as video_file:
        while True:
            chunk = video_file.read(chunk_size)
            if not chunk:
                break

            append_params = {
                "command": "APPEND",
                "additional_owners": twitter_user_id,
                "media_category": media_category,
                "media_id": media_id_string,
                "segment_index": segment_id,
            }
            append_files = {"media": chunk}
            append_response = oauth.post(
                append_url, data=append_params, files=append_files
            )

            # Check if video upload was successful
            print(append_response.status_code)
            if append_response.status_code == 204:
                print(f"Video chunk {segment_id} uploaded successfully")
            else:
                print(
                    f"Failed to upload chunk {segment_id} with error. Error: {
                        finalize_response.text}"
                )

            segment_id += 1

    # Finalize video upload
    finalize_url = "https://upload.twitter.com/1.1/media/upload.json"
    finalize_params = {
        "command": "FINALIZE",
        "additional_owners": twitter_user_id,
        "media_category": media_category,
        "media_id": media_id_string,
    }
    finalize_response = oauth.post(finalize_url, data=finalize_params)
    upload_finalized_json = finalize_response.json()
    media_id_string = upload_finalized_json["media_id_string"]
    check_after = upload_finalized_json["processing_info"]["check_after_secs"]
    time.sleep(check_after)
    for i in range(100):
        poll_response = oauth.get(
            f"https: // upload.twitter.com/1.1/media/upload.json?command=STATUS & media_id={
                media_id_string}"
        )
        poll_respons_json = poll_response.json()
        poll_processing_info = poll_respons_json["processing_info"]

        if "error" in poll_processing_info:
            pprint(poll_processing_info["error"])
            break
        progress_percent = poll_processing_info["progress_percent"]
        print(f"#{i}/100 progress {progress_percent}%")
        poll_state = poll_processing_info["state"]
        if poll_state == "succeeded":
            break
        check_after = poll_processing_info["check_after_secs"]
        time.sleep(check_after)

    if finalize_response.status_code == 201 or finalize_response.status_code == 200:
        print("Video uploaded successfully.")
    else:
        print(
            f"potential failure: code={
                finalize_response.status_code} to upload video. Error: {finalize_response.text}"
        )

    tweet_text = tweet_dict["text"]
    # TODO remove when you get the blue check mark
    tweet_text = tweet_text[:270]
    payload = {"text": tweet_text, "media": {"media_ids": [media_id_string]}}

    if "in_reply_to_tweet_id" in tweet_dict:
        payload["reply"] = {
            "in_reply_to_tweet_id": tweet_dict["in_reply_to_tweet_id"]}

    response = oauth.post(
        "https://api.twitter.com/2/tweets",
        json=payload,
    )

    if response.status_code != 201 and response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )

    print("Response code: {}".format(response.status_code))

    # Saving the response as JSON
    json_response = response.json()
    print(json.dumps(json_response, indent=4, sort_keys=True))
    return json_response


def post_tweet(
    access_token: Annotated[str, "the user access token"],
    access_token_secret: Annotated[str, "the user access token secret"],
    tweet: Annotated[
        Dict[str, Any],
        "the data of the tweet made up of 3 keys text, image_path, and in_reply_to_tweet_id",
    ],
):
    oauth = get_credentials(access_token, access_token_secret)
    # print(tweet)
    # Making the request
    payload = {}
    if "text" in tweet:
        print("tEXT = ")
        print(tweet["text"])
        # TODO remove when you get the blue check mark
        tweet_text = tweet["text"][:280]
        payload["text"] = tweet_text

    if "image_path" in tweet:
        upload_url = f"https://upload.twitter.com/1.1/media/upload.json?media_category=tweet_image"
        image_data = open(tweet["image_path"], "rb")
        files = {"media": image_data}
        media_response = oauth.post(upload_url, files=files)
        media_id_string = media_response.json()["media_id_string"]
        payload["media"] = {"media_ids": [media_id_string]}

    if "in_reply_to_tweet_id" in tweet:
        if "reply" not in payload:
            payload["reply"] = {}
        payload["reply"]["in_reply_to_tweet_id"] = tweet["in_reply_to_tweet_id"]
    pprint(payload)
    response = oauth.post("https://api.twitter.com/2/tweets", json=payload)

    if response.status_code != 201:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    # Saving the response as JSON
    json_response = response.json()
    # print(json.dumps(json_response, indent=4, sort_keys=True))
    return json_response["data"]


def post_tweet_thread(
    access_token: Annotated[str, "the user access token"],
    access_token_secret: Annotated[str, "the user access token secret"],
    tweets: Annotated[
        List[Dict[str, Any]],
        "a list of dictionaries, for every entry the dictionary should have 3 keys: text for the tweet text, image_path for the tweet image, and in_reply_to_tweet_id if you were replying to a tweet",
    ],
):
    posted_tweets = []
    for tweet in tweets:
        if posted_tweets:
            tweet["in_reply_to_tweet_id"] = posted_tweets[-1]["id"]
        posted_tweet_data = post_tweet(
            access_token, access_token_secret, tweet)
        posted_tweets.append(posted_tweet_data)
