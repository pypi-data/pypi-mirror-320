import os
from pprint import pprint
import requests


def intialize_video_upload(page_id, access_token):
    url = f"https://graph.facebook.com/v19.0/{page_id}/video_stories"
    data = {"upload_phase": "start"}
    params = {"access_token": access_token}
    response = requests.post(url, params=params, json=data)
    if response.status_code == 200:
        response_json = response.json()
        print("====video init====")
        pprint(response_json)

        upload_url = response_json.get("upload_url")
        video_id = response_json.get("video_id")
        return (upload_url, video_id)
    else:
        print("Error:", response.status_code)
        print("Response:", response.text)


def upload_video_to_video_id(video_id, filepath, access_token):
    file_size = os.path.getsize(filepath)
    print(file_size)
    params = {"access_token": access_token}
    url = f"https://rupload.facebook.com/video-upload/v19.0/{video_id}"
    headers = {
        "offset": "0",
        "file_size": str(file_size),
        # alt if uploading from url
        # "file_url: "https://some.cdn.url/video.mp4"
    }
    # files = {"file": open(filepath, "rb")}
    data = open(filepath, "rb")

    response = requests.post(url, headers=headers, data=data, params=params)
    if response.status_code == 200:
        response_json = response.json()
        print("====video upload====")
        pprint(response_json)

        success = response_json.get("success")
        message = response_json.get("message")
        return (success, message)
    else:
        print("Error:", response.status_code)
        print("Response:", response.text)


def publish_video_story(page_id, video_id, access_token):
    url = f"https://graph.facebook.com/v19.0/{page_id}/video_stories"

    params = {
        "video_id": video_id,
        "upload_phase": "finish",
        "access_token": access_token,
    }

    response = requests.post(url, params=params)
    if response.status_code == 200:
        response_json = response.json()
        print("====video publish====")
        pprint(response_json)

        success = response_json.get("success")
        message = response_json.get("message")
        return (success, message)
    else:
        print("Error:", response.status_code)
        print("Response:", response.text)


def get_video_upload_status(video_id, access_token):
    url = f"https://graph.facebook.com/v19.0/{video_id}"

    params = {"fields": "status", "access_token": access_token}

    response = requests.get(url, params=params)
    if response.status_code == 200:
        response_json = response.json()
        pprint(response_json)

        status = response_json.get("status")
        copyright_check_status = status.get("copyright_check_status")
        processing_phase = status.get("processing_phase")
        processing_progress = status.get("processing_progress")
        publishing_phase = status.get("publishing_phase")
        publishing_phase_status = publishing_phase.get("publish_status")

        uploading_phase = status.get("uploading_phase")
        uploading_phase_status = uploading_phase.get("status")
        return publishing_phase_status == "published"
        # return (success, message)
    else:
        print("Error:", response.status_code)
        print("Response:", response.text)


# https://developers.facebook.com/docs/page-stories-api#step-1--upload-a-photo
def post_facebook_story_video(page_id, filepath, access_token):
    (upload_url, video_id) = intialize_video_upload(page_id, access_token)
    upload_video_to_video_id(video_id, filepath, access_token)
    # time.sleep(3)
    # for i in range(10):
    #     upload_status = get_video_upload_status(video_id, access_token)
    #     if upload_status == True:
    #         break
    #     time.sleep(3)
    return publish_video_story(page_id, video_id, access_token)


def intialize_reels_upload(page_id, access_token):
    url = f"https://graph.facebook.com/v19.0/{page_id}/video_reels"
    data = {"upload_phase": "start", "access_token": access_token}

    response = requests.post(url, json=data)
    if response.status_code == 200:
        response_json = response.json()
        print("====video init====")
        pprint(response_json)

        upload_url = response_json.get("upload_url")
        video_id = response_json.get("video_id")
        return (upload_url, video_id)
    else:
        print("Error:", response.status_code)
        print("Response:", response.text)


def upload_reel_to_video_id(video_id, filepath, access_token):
    file_size = os.path.getsize(filepath)
    print(file_size)

    url = f"https://rupload.facebook.com/video-upload/v19.0/{video_id}"
    headers = {
        "Authorization": f"OAuth {access_token}",
        "offset": "0",
        "file_size": str(file_size),
        # alt if uploading from url
        # "file_url: "https://some.cdn.url/video.mp4"
    }
    # files = {"file": open(filepath, "rb")}
    data = open(filepath, "rb")

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        response_json = response.json()
        print("====video upload====")
        pprint(response_json)

        success = response_json.get("success")
        message = response_json.get("message")
        return (success, message)
    else:
        print("Error:", response.status_code)
        print("Response:", response.text)


def publish_reel_story(page_id, video_id, access_token, caption):
    url = f"https://graph.facebook.com/v19.0/{page_id}/video_reels"

    params = {
        "video_id": video_id,
        "upload_phase": "finish",
        "access_token": access_token,
        "video_state": "PUBLISHED",
        "description": caption,
    }

    response = requests.post(url, params=params)
    if response.status_code == 200:
        response_json = response.json()
        print("====video publish====")
        pprint(response_json)

        success = response_json.get("success")
        message = response_json.get("message")
        return (success, message)
    else:
        print("Error:", response.status_code)
        print("Response:", response.text)


# https://developers.facebook.com/docs/video-api/guides/reels-publishing#step-3--publish-the-reel
def post_facebook_reel_video(caption, page_id, filepath, access_token):
    (upload_url, video_id) = intialize_reels_upload(page_id, access_token)
    upload_reel_to_video_id(video_id, filepath, access_token)
    return publish_reel_story(page_id, video_id, access_token, caption)
