import random
import os
import requests
from pprint import pprint
import string


def generate_csrf_state(length=32):
    """Generates a random CSRF state string.

    Args:
        length: The desired length of the CSRF state string (default: 32).

    Returns:
        A random alphanumeric string of the specified length.
    """

    # Generate random characters using string.digits and string.ascii_lowercase
    characters = string.digits + string.ascii_lowercase

    # Use random.choices to generate random characters with replacement
    random_string = "".join(random.choices(characters, k=length))

    # Extract a substring starting from the 3rd character (index 2)
    csrf_state = random_string[2:]

    return csrf_state


def get_tiktok_signin_url():
    csrfState = generate_csrf_state()
    url = "https://www.tiktok.com/v2/auth/authorize"

    client_key = os.environ["TIKTOK_CLIENT_KEY"]
    redirect_uri = os.environ["TIKTOK_REDIRECT_URI"]

    url += f"?client_key={client_key}"
    url += "&scope=user.info.basic,video.list,video.publish,video.upload"
    url += "&response_type=code"
    url += f"&redirect_uri={redirect_uri}"
    url += "&state=" + csrfState
    print(url)
    return url


# sample response after authorization
# https://mltask.com/oauth/tiktok/login_callback?code=bR9CttKKClVchU59ZBrgbCnxlZ2TM-fWFE1qo3ZlIxKOpqPsg6uqrdikjt7KennsK-frRezqOszkdhVc5S59uoqLH3WqX3ByCcPB0iCEzCryJvdm5eqd3Wv0Niz2QwMt0DJ3nJEOZynjd9zK956yem8PUngJclBnYnc4i-Pn5sg5FyIaEz2tfrA_wis-812Opsn5o72JWkiERQK_xSyPVg%2A3%216376.u1&scopes=user.info.basic%2Cvideo.list%2Cvideo.publish%2Cvideo.upload&state=7xowxl1t237crlzi8xt6rg9pspo5g5


# https://developers.tiktok.com/doc/oauth-user-access-token-management
def get_access_token_from_auth_code(auth_code):
    url = "https://open.tiktokapis.com/v2/oauth/token/"
    client_key = os.environ["TIKTOK_CLIENT_KEY"]
    client_secret = os.environ["TIKTOK_CLIENT_SECRET"]
    redirect_uri = os.environ["TIKTOK_REDIRECT_URI"]

    payload = {
        "client_key": f"{client_key}",
        "client_secret": f"{client_secret}",
        "code": auth_code.encode("utf-8"),
        "grant_type": "authorization_code",
        "redirect_uri": f"{redirect_uri}",
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache",
    }

    response = requests.post(url, data=payload, headers=headers)
    if response.status_code == 200:
        # Parse the response JSON
        response_json = response.json()
        print("******")
        pprint(response_json)
        print("******")
        # Access specific keys in the response
        access_token = response_json.get("access_token")
        expires_in = response_json.get("expires_in")
        refresh_expires_in = response_json.get("refresh_expires_in")
        refresh_token = response_json.get("refresh_token")
        scope = response_json.get("scope")
        token_type = response_json.get("token_type")

        # Print or use the parsed data as needed
        print("Access Token:", access_token)
        print("Expires In:", expires_in)
        print("refresh_expires_in:", refresh_expires_in)
        print("refresh_token:", refresh_token)
        print("scope:", scope)
        print("Token Type:", token_type)
        return (access_token, expires_in, refresh_token, refresh_expires_in)
    else:
        print("Error:", response.status_code)
        print("Response:", response.text)


# sample response
# {'access_token': 'act.5uryPfUa5oWsWoLRAI7y8a5ElkACNfvuAgUKXNBPblcdD80bW5bSB79n6o5E!6375.u1',
#  'expires_in': 86400,
#  'open_id': '-000NAdxlHusXRGvLc05cl15y3jnkJg4utC5',
#  'refresh_expires_in': 31536000,
#  'refresh_token': 'rft.KJBXhCs01CHFaauq1Qi5haK6ZItJSO0nfbRLylgmHij4bFZHZJL7rw0aUsta!6369.u1',
#  'scope': 'user.info.basic,video.list,video.publish,video.upload',
#  'token_type': 'Bearer'}


def refresh_token(refresh_token):
    url = "https://open.tiktokapis.com/v2/oauth/token/"
    client_key = os.environ["TIKTOK_CLIENT_KEY"]
    client_secret = os.environ["TIKTOK_CLIENT_SECRET"]

    payload = {
        "client_key": f"{client_key}",
        "client_secret": f"{client_secret}",
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache",
    }

    response = requests.post(url, data=payload, headers=headers)
    if response.status_code == 200:
        # Parse the response JSON
        response_json = response.json()
        print("******")
        pprint(response_json)
        print("******")
        # Access specific keys in the response
        access_token = response_json.get("access_token")
        expires_in = response_json.get("expires_in")
        refresh_expires_in = response_json.get("refresh_expires_in")
        refresh_token = response_json.get("refresh_token")
        scope = response_json.get("scope")
        token_type = response_json.get("token_type")

        # Print or use the parsed data as needed
        print("Access Token:", access_token)
        print("Expires In:", expires_in)
        print("refresh_expires_in:", refresh_expires_in)
        print("refresh_token:", refresh_token)
        print("scope:", scope)
        print("Token Type:", token_type)
        return (access_token, expires_in, refresh_token, refresh_expires_in)
    else:
        print("Error:", response.status_code)
        print("Response:", response.text)
