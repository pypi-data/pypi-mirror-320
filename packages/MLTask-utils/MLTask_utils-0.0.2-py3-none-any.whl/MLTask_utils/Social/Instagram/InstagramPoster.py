import time
from pprint import pprint
import requests
import os
from typing import Literal
from MLTask_utils.AWS.S3Utils import upload_to_s3_and_get_public_url

from urllib.parse import quote


def get_url_key_from_media_type(
    media_type: Literal["IMAGE", "VIDEO",
                        "REELS", "STORIES_IMAGE", "STORIES_VIDEO"]
):
    if media_type == "IMAGE":
        return "image_url"

    if media_type == "VIDEO":
        return "video_url"

    if media_type == "REELS":
        return "video_url"

    if media_type == "STORIES_IMAGE":
        return "image_url"

    if media_type == "STORIES_VIDEO":
        return "video_url"

    return "image_url"


def get_media_key_value_from_media_type(
    media_type: Literal["IMAGE", "VIDEO",
                        "REELS", "STORIES_IMAGE", "STORIES_VIDEO"]
):
    if media_type == "VIDEO":
        return "media_type=VIDEO"
    if media_type == "REELS":
        return "media_type=REELS"
    if media_type == "STORIES_VIDEO" or media_type == "STORIES_IMAGE":
        return "media_type=STORIES"
    return None


def create_image_container(
    user_access_token,
    ig_user_id,
    file_path,
    caption,
    media_type: Literal[
        "IMAGE", "VIDEO", "REELS", "STORIES_IMAGE", "STORIES_VIDEO"
    ] = "IMAGE",
    cover_image_path=None,
):
    public_upload_url = upload_to_s3_and_get_public_url(
        os.environ["AWS_ACCESS_KEY_ID"],
        os.environ["AWS_SECRET_ACCESS_KEY"],
        os.environ["AWS_STORAGE_DTASK_STORAGE_BUCKETNAME"],
        file_path,
    )

    container_create_post_url = f"https: // graph.facebook.com/v19.0/{ig_user_id}/media?{
        get_url_key_from_media_type(media_type)} = {public_upload_url} & caption = {quote(caption)}"

    if cover_image_path is not None:
        cover_image_url = upload_to_s3_and_get_public_url(
            os.environ["AWS_ACCESS_KEY_ID"],
            os.environ["AWS_SECRET_ACCESS_KEY"],
            os.environ["AWS_STORAGE_DTASK_STORAGE_BUCKETNAME"],
            cover_image_path,
        )
        container_create_post_url += f"&cover_url={cover_image_url}"

    media_type_key_value = get_media_key_value_from_media_type(media_type)
    if media_type_key_value != None:
        container_create_post_url += f"&{media_type_key_value}"

    payload = {"access_token": user_access_token}
    response = requests.post(container_create_post_url, data=payload)
    if response.status_code == 200:
        response_json = response.json()
        print("====image upload====")
        pprint(response_json)

        id = response_json.get("id")
        # message = response_json.get('message')
        return id
    else:
        print("Error:", response.status_code)
        print("Response:", response.text)


# https://developers.facebook.com/docs/instagram-api/reference/ig-user/media#query-string-parameters
def publish_to_container(user_access_token, ig_user_id, container_id):
    container_publish_post_url = f"https: // graph.facebook.com/v19.0/{
        ig_user_id}/media_publish?creation_id = {container_id} & share_to_feed = true"

    payload = {"access_token": user_access_token}
    response = requests.post(container_publish_post_url, data=payload)
    if response.status_code == 200:
        response_json = response.json()
        print("====image post====")
        pprint(response_json)

        id = response_json.get("id")
        # message = response_json.get('message')
        return id
    else:
        print("Error:", response.status_code)
        print("Response:", response.text)


def check_upload_status(container_id, user_access_token):
    container_publish_post_url = f"https: // graph.facebook.com/v19.0/{
        container_id}?access_token = {user_access_token} & fields = status_code, status"
    response = requests.get(container_publish_post_url)
    if response.status_code == 200:
        response_json = response.json()
        print("====instagram upload status====")
        pprint(response_json)
        status_code = response_json.get("status_code")
        # message = response_json.get('message')
        return status_code == "FINISHED"
    else:
        print("Error:", response.status_code)
        print("Response:", response.text)


def poll_for_completion(container_id, user_access_token):
    time.sleep(5)
    for i in range(20):  # about 10 minutes timeout which is frankly rediculous
        upload_status = check_upload_status(container_id, user_access_token)
        if upload_status == True:
            break
        time.sleep(30)


def post_image_to_instagram(user_access_token, ig_user_id, file_path, caption):
    container_id = create_image_container(
        user_access_token, ig_user_id, file_path, caption, "IMAGE"
    )
    poll_for_completion(container_id, user_access_token)
    post_id = publish_to_container(user_access_token, ig_user_id, container_id)
    return post_id


def post_video_to_instagram(user_access_token, ig_user_id, file_path, caption):
    container_id = create_image_container(
        user_access_token, ig_user_id, file_path, caption, "VIDEO"
    )
    poll_for_completion(container_id, user_access_token)
    post_id = publish_to_container(user_access_token, ig_user_id, container_id)
    return post_id


def post_reel_to_instagram(
    user_access_token, ig_user_id, file_path, caption, cover_image_path=None
):
    container_id = create_image_container(
        user_access_token, ig_user_id, file_path, caption, "REELS", cover_image_path
    )
    poll_for_completion(container_id, user_access_token)
    post_id = publish_to_container(user_access_token, ig_user_id, container_id)
    return post_id


def post_video_story_to_instagram(user_access_token, ig_user_id, file_path, caption):
    container_id = create_image_container(
        user_access_token, ig_user_id, file_path, caption, "STORIES_VIDEO"
    )
    poll_for_completion(container_id, user_access_token)
    post_id = publish_to_container(user_access_token, ig_user_id, container_id)
    return post_id


def post_image_story_to_instagram(user_access_token, ig_user_id, file_path, caption):
    container_id = create_image_container(
        user_access_token, ig_user_id, file_path, caption, "STORIES_IMAGE"
    )
    poll_for_completion(container_id, user_access_token)
    post_id = publish_to_container(user_access_token, ig_user_id, container_id)
    return post_id
