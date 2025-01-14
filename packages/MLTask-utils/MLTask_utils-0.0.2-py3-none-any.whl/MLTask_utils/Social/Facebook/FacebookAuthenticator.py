from pprint import pprint
import requests
import random
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
    random_string = ''.join(random.choices(characters, k=length))

    # Extract a substring starting from the 3rd character (index 2)
    csrf_state = random_string[2:]

    return csrf_state
  
  
def get_business_login_url(app_id, redirect_uri, scopes=[]):
  ret = f'https://www.facebook.com/v19.0/dialog/oauth?client_id={app_id}&display={"page"}&redirect_uri={redirect_uri}&response_type=token'
  if len(scopes) != 0:
    ret += "&scope=" + ",".join(scopes)
  return ret


def get_user_login_url(app_id, redirect_uri, scopes=[]):
  ret = f'https://www.facebook.com/v19.0/dialog/oauth?client_id={app_id}&redirect_uri={redirect_uri}&state={generate_csrf_state()}'
  if len(scopes) != 0:
    ret += "&scope=" + ",".join(scopes)
  return ret

def ask_for_permission_url(app_id, redirect_uri, scopes):
  return f'https://www.facebook.com/v19.0/dialog/oauth?client_id={app_id}&auth_type=rerequest&redirect_uri={redirect_uri}&scopes={",".join(scopes)}'

def exchange_code_for_access_token(code, app_id, redirect_uri, app_secret):
  url = f'https://graph.facebook.com/v19.0/oauth/access_token?client_id={app_id}&redirect_uri={redirect_uri}&client_secret={app_secret}&code={code}'
  response = requests.get(url)
  if response.status_code == 200:
      # Parse the response JSON
      response_json = response.json()
      # Access specific keys in the response
      access_token = response_json.get('access_token')
      expires_in = response_json.get('expires_in')
      token_type = response_json.get('token_type')
      return access_token
  else:
      print("Error:", response.status_code)
      print("Response:", response.text)
   
def get_long_lived_access_token(app_id, app_secret, access_token):
    url = f'https://graph.facebook.com/v19.0/oauth/access_token?grant_type=fb_exchange_token&client_id={app_id}&client_secret={app_secret}&fb_exchange_token={access_token}'
    response = requests.get(url)
    if response.status_code == 200:
        # Parse the response JSON
        response_json = response.json()
        # Access specific keys in the response
        long_access_token = response_json.get('access_token')
        expires_in = response_json.get('expires_in')
        token_type = response_json.get('token_type')
        return (long_access_token, expires_in)
    else:
        print("Error:", response.status_code)
        print("Response:", response.text)
     
def get_user_id(access_token):
  params = {'access_token': access_token}
  response = requests.get('https://graph.facebook.com/v19.0/me', params=params)
  
  if response.status_code == 200:
      response_json = response.json()
      pprint(response_json)
      # Access specific keys in the response
      id = response_json.get('id')
      return id
  else:
      print("Error:", response.status_code)
      print("Response:", response.text)
  
  
def get_user_permissions(access_token):
  params = {'access_token': access_token}
  response = requests.get('https://graph.facebook.com/v19.0/me/permissions', params=params)
  if response.status_code == 200:
    response_json = response.json()
    pprint(response_json)
  else:
      print("Error:", response.status_code)
      print("Response:", response.text)
  
def get_page_acess_tokens(access_token):
    url = f"https://graph.facebook.com/me/accounts?access_token={access_token}" 
    response = requests.get(url)
    if response.status_code == 200:
      response_json = response.json()
      data = response_json.get("data")
      pages_data = []
      for entry in data:
        pages_data.append({
          "id": entry.get("id"),
          "name": entry.get("name"),
          "access_token": entry.get("access_token"),
        })
        
      return pages_data
    else:
        print("Error:", response.status_code)
        print("Response:", response.text)

def get_connected_instagram_id(page_access_token):
  
  url = f"https://graph.facebook.com/v19.0/me?fields=connected_instagram_account&access_token={page_access_token}" 
  response = requests.get(url)
  if response.status_code == 200:
    response_json = response.json()
    return response_json.get("connected_instagram_account").get("id")
  else:
      print("Error:", response.status_code)
      print("Response:", response.text)
   