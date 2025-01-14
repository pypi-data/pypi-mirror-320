from twitchio import Client
from .TwitchBot import TwitchBot
import requests
import urllib.parse
from pprint import pprint
import os

TWITCH_CLIENT_ID = os.environ['TWITCH_CLIENT_ID']
TWITCH_CLIENT_SECRET = os.environ['TWITCH_CLIENT_SECRET']


def authorize_on_link(redirect_uri="http://localhost:3000"):
    scopes = ["chat:read"]
    scopes_string = ' '.join(scopes)
    encoded_scopes_string = urllib.parse.quote(scopes_string)
    print(encoded_scopes_string)
    authorization_url = f"https://id.twitch.tv/oauth2/authorize?response_type=code&client_id={TWITCH_CLIENT_ID}&redirect_uri={redirect_uri}&scope={encoded_scopes_string}"
    print(authorization_url)


def swap_auth_code_for_token(auth_code, redirect_uri="http://localhost:3000"):
    authorization_url = f"https://id.twitch.tv/oauth2/token"
    payload = {
        'client_id': TWITCH_CLIENT_ID,
        'client_secret': TWITCH_CLIENT_SECRET,
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri
    }
    response = requests.post(authorization_url, json=payload)

    if response.status_code == 200:
        response_json = response.json()
        access_token = response_json['access_token']
        return access_token
    else:
        print("POST request failed with status code:", response.status_code)


def start_listening_to_messages(access_token, channel_id, message_callback):
    access_token = access_token
    initial_channels = [channel_id]
    bot = TwitchBot(access_token, initial_channels)
    client = Client(token=access_token)

    @bot.event()
    async def event_message(message):
        # You can handle the incoming messages here
        user_profile_picture_url = ''
        fetched_users_data = await client.fetch_users(ids=[message.author.id])
        for user in fetched_users_data:
            user_profile_picture_url = user.profile_image
            # print(f'{user.profile_image}')

        # print("***************")
        author_info = {
            'badges': message.author.badges,
            'color': message.author.color,
            'displayName': message.author.display_name,
            'id': message.author.id,
            'isBroadcaster': message.author.is_broadcaster,
            'isModerator': message.author.is_mod,
            'isSubscriber': message.author.is_subscriber,
            'isTurbo': message.author.is_turbo,
            'isVIP': message.author.is_vip,
            'mention': message.author.mention,
            'name': message.author.name,
            'prediction': message.author.prediction,
            'picture': user_profile_picture_url
        }

        message_callback(
            {'author': author_info, 'id': message.id, 'message': {'content': message.content, 'timestamp': message.timestamp}})

    bot.run()


def main():
    # authorize_on_link()
    # access_token = swap_auth_code_for_token('code_to_swap')
    # print(access_token)
    print("MAIN")


if __name__ == "__main__":
    main()
