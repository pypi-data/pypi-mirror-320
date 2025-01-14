import requests
import os
from pprint import pprint
def list_user_videos(token, cursor=None):
    url = "https://open.tiktokapis.com/v2/video/list/?fields=id,cover_image_url,share_url,video_description"
    data = {
        "max_count": 20
    }
    if cursor is not None:
        data["cursor"] = cursor
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json; charset=UTF-8'
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        response_json = response.json()
        # pprint(response_json)
        videos = response_json.get('data').get('videos')
        pagination = {
            "cursor": response_json.get('data').get('cursor'),
            "has_more": response_json.get('data').get('has_more'),
        }
        return videos, pagination
    else:
        print("Error:", response.status_code)
        pprint(response.text)
        # pprint(response)
        return None, None


def get_user_videos(token, video_ids):
    url = "https://open.tiktokapis.com/v2/video/query/?fields=id,cover_image_url,share_url,video_description"
    data = {
        "filters": video_ids,
    }
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json; charset=UTF-8'
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        response_json = response.json()
        pprint(response_json)
        # publish_id = response_json.get('data').get('publish_id')
        # upload_url = response_json.get('data').get('upload_url')
        # return publish_id, upload_url
    else:
        print("Error:", response.status_code)
        pprint(response.text)
        # pprint(response)
        return None, None
