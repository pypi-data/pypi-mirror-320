from pinterest.client import PinterestSDKClient
from pinterest.organic.pins import Pin
from pinterest.organic.boards import Board

import os
import base64
import requests
from pprint import pprint


# Refresh Token for Client 2
# pinterest_refresh_token_2 = <refresh token 2>
# pinterest_app_id_2 = <app id 2>
# pinterest_app_secret_2 = <app secret 2>

# client_2 = PinterestSDKClient.create_client_with_refresh_token(
#     refresh_token=pinterest_access_token_2,
#     app_id=pinterest_app_id_2,
#     app_secret=pinterest_app_secret_2,
# )

PINTEREST_CLIENT_ID = os.environ['PINTEREST_CLIENT_ID']
PINTEREST_CLIENT_SECRET = os.environ['PINTEREST_CLIENT_SECRET']
PINTEREST_REDIRECT_URI = os.environ['PINTEREST_REDIRECT_URI']
YOUR_OPTIONAL_STRING = "from_python_recipie"


def initiateOAUTH():

    authorization_url = f'https://www.pinterest.com/oauth/?client_id={PINTEREST_CLIENT_ID}&redirect_uri={PINTEREST_REDIRECT_URI}&response_type=code&scope=boards:read,pins:read,boards:write,pins:write&state={YOUR_OPTIONAL_STRING}'
    print(authorization_url)


# https://www.example.com/oauth/pinterest/oauth_response/?code={CODE}
def get_access_token(code):
    credentials = f"{PINTEREST_CLIENT_ID}:{PINTEREST_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    url = "https://api.pinterest.com/v5/oauth/token"

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://localhost/"
    }

    response = requests.post(url, headers=headers, data=data)
    response_json = response.json()
    pprint(response_json)
    access_token = response_json['access_token']
    print('access_token = {access_token}')


def get_client(access_token="pina_AEAWXMYWAAWXQAIAGAAGYDYVJVRTNCIBACGSPKZFKNRHJBYBWVVW2XGDT6XDSV3BL44FLXE7RYT57QRWG75JIV5EXQU65DIA"):
    # Access Token for Client 1
    pinterest_access_token_1 = access_token
    client_1 = PinterestSDKClient.create_client_with_token(
        access_token=pinterest_access_token_1,
    )
    return client_1


def get_boards():
    client = get_client()
    boards, bookmarks = Board.get_all(client=client)
    for board in boards:
        print(board.id)
        print(board.name)
        print(board.description)
        print('----------')


# def get_board_from_id(board_id):
#     client = get_client()
#     board_get = Board(board_id=board_id, client=client)
#     pprint(board_get)

# untested
# theoretically it all works but we need production access to post to production
# not messing with that at the moment
def create_pin(board_id):
    client = get_client()
    # Board information can be fetched from profile page or from create/list board method here:
    # https://developers.pinterest.com/docs/api/v5/#operation/boards/list

    pin_create = Pin.create(
        client=client,
        board_id=board_id,
        title="My Pin",
        description="Pin Description",
        media_source={
            "source_type": "image_url",
            "content_type": "image/jpeg",
            "data": "string",
            'url': 'https://i.pinimg.com/564x/28/75/e9/2875e94f8055227e72d514b837adb271.jpg'
        }
    )
    print("Pin Id: %s, Pin Title:%s" % (pin_create.id, pin_create.title))
