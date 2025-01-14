import requests
import os
from pprint import pprint
from typing import Literal
# max_chunk_size = 10 * 1024 * 1024  # 10 MB

# def calculate_chunk_info(filepath, max_chunk_size):
#     file_size = os.path.getsize(filepath)
#     total_chunk_count = (file_size + max_chunk_size - 1) // max_chunk_size
#     chunk_size = file_size // total_chunk_count
#     return file_size, chunk_size, total_chunk_count


def get_source_info_for_file(filepath):
    file_size = os.path.getsize(filepath)
    video_size, chunk_size, total_chunk_count = (file_size, file_size, 1)

    return {
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": f"{video_size}",
            "chunk_size": f"{chunk_size}",
            "total_chunk_count": f"{total_chunk_count}"
        }
    }


def initialize_upload(token, filepath):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json; charset=UTF-8'
    }
    data = get_source_info_for_file(filepath)
    # sadly doesnt work... (for now)
    # data["post_info"] = {
    #     "title": "funny cat",
    #     "description": "this will be a #funny photo on your @tiktok #fyp"
    #     # "privacy_level": privacy_level,
    #     # "disable_duet": disable_duet,
    #     # "disable_comment": disable_comment,
    #     # "disable_stitch": disable_stitch,
    #     # "video_cover_timestamp_ms": video_cover_timestamp_ms
    # }
    url = 'https://open.tiktokapis.com/v2/post/publish/inbox/video/init/'

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200 or response.status_code == 201:
        response_json = response.json()
        print("=====tiktok upload init=====")
        pprint(response_json)
        publish_id = response_json.get('data').get('publish_id')
        upload_url = response_json.get('data').get('upload_url')
        return publish_id, upload_url
    else:
        print("Error:", response.status_code, response.text)

        return None, None


def initialize_upload_for_direct(token, filepath,
                                 caption=None,
                                 privacy_level: Literal["PUBLIC_TO_EVERYONE", "MUTUAL_FOLLOW_FRIENDS",
                                                        "FOLLOWER_OF_CREATOR", "SELF_ONLY"] = "PUBLIC_TO_EVERYONE",
                                 disable_duet=False, disable_comment=False, disable_stitch=False,
                                 video_cover_timestamp_ms=0):

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json; charset=UTF-8'
    }
    data = get_source_info_for_file(filepath)
    data["post_info"] = {
        "title": caption,
        "privacy_level": privacy_level,
        "disable_duet": disable_duet,
        "disable_comment": disable_comment,
        "disable_stitch": disable_stitch,
        "video_cover_timestamp_ms": video_cover_timestamp_ms
    }
    url = 'https://open.tiktokapis.com/v2/post/publish/video/init/'
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        response_json = response.json()
        publish_id = response_json.get('data').get('publish_id')
        upload_url = response_json.get('data').get('upload_url')
        return publish_id, upload_url
    else:
        print("Error:", response.status_code)
        pprint(response.text)
        # pprint(response)
        return None, None


def calculate_content_values(file_path, chunk_start, chunk_end, total_byte_length):
    content_length = chunk_end - chunk_start + 1
    content_range = f"bytes {chunk_start}-{chunk_end}/{total_byte_length}"
    return content_length, content_range


def finalize_upload(upload_url, filepath):
    file_size = os.path.getsize(filepath)
    headers = {
        'Content-Range': f'bytes 0-{file_size - 1}/{file_size}',
        'Content-Length': f'{file_size}',
        'Content-Type': 'video/mp4'
    }

    with open(filepath, 'rb') as file:
        data = file.read()

    response = requests.put(upload_url, headers=headers, data=data)
    print("Finished uploading")
    pprint(response)


def upload_video_to_user_draft(token, filepath):
    (publish_id, upload_url) = initialize_upload(token, filepath)
    finalize_upload(upload_url, filepath)


def post_direct_user_video(token, filepath, caption, privacy_level: Literal["PUBLIC_TO_EVERYONE", "MUTUAL_FOLLOW_FRIENDS", "FOLLOWER_OF_CREATOR", "SELF_ONLY"]):
    (publish_id, upload_url) = initialize_upload_for_direct(
        token, filepath, caption, privacy_level)
    finalize_upload(upload_url, filepath)
