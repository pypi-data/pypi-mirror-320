from instagrapi import Client


def post_image(image_file_path, caption, username, password):
    # print(image_file_path)
    cl = Client()
    cl.login(username, password)

    media = cl.photo_upload(
        image_file_path,
        caption,
        # extra_data={
        #     "custom_accessibility_caption": "alt text example",
        #     "like_and_view_counts_disabled": 1,
        #     "disable_comments": 1,
        # }
    )
    print(media)


def post_reel(reel_file_path, thumbnail_file_path, caption, username, password):
    cl = Client()
    cl.login(username, password)

    media = cl.clip_upload(
        reel_file_path,
        caption,
        thumbnail_file_path,
        extra_data={
            # "custom_accessibility_caption": "alt text example",
            # "like_and_view_counts_disabled": 1,
            # "disable_comments": 1,
        }
    )
    print(media)
