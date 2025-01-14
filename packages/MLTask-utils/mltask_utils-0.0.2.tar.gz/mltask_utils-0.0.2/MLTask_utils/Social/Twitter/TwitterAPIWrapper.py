from requests_oauthlib import OAuth1Session
import os
import json
from pprint import pprint
import time
from Social.Twitter.TwitterAuthenticator import get_credentials

consumer_key = os.environ.get("TWITTER_CONSUMER_KEY")
consumer_secret = os.environ.get("TWITTER_CONSUMER_SECRET_KEY")


def get_twitter_user_id(access_token, access_token_secret):
    # Twitter API credentials
    oauth = get_credentials(access_token, access_token_secret)
    fields = "created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,verified_type,withheld"

    params = {"user.fields": fields}
    response = oauth.get("https://api.twitter.com/2/users/me", params=params)

    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )

    print("Response code: {}".format(response.status_code))

    json_response = response.json()
    print(json.dumps(json_response, indent=4, sort_keys=True))
