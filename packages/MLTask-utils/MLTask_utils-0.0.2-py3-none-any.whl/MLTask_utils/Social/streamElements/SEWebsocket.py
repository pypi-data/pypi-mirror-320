# socketio dependency conflict with whisperx
# import socketio

# # AccessToken is grabbed from OAuth2 authentication of the account.
# access_token = ""
# # JWT is available here: https://streamelements.com/dashboard/account/channels
# jwt = ""

# sio = socketio.Client()


# @sio.event
# def connect():
#     print('Successfully connected to the websocket')
#     # sio.emit('authenticate', {'method': 'oauth2', 'token': access_token})
#     sio.emit('authenticate', {'method': 'jwt', 'token': jwt})


# @sio.event
# def disconnect():
#     print('Disconnected from websocket')
#     # Reconnect logic can be added here


# @sio.event
# def authenticated(data):
#     channel_id = data['channelId']
#     print(f"Successfully connected to channel {channel_id}")


# @sio.on('unauthorized')
# def unauthorized_error():
#     print('Unauthorized error')


# @sio.on('event:test')
# def on_test_event(data):
#     print(data)
#     # Structure as mentioned in the JavaScript code


# @sio.on('event')
# def on_event(sid, data):
#     print(data)
#     print(sid)
# # Structure as mentioned in the JavaScript code


# @sio.on('event:update')
# def on_event_update(sid, data):
#     print(sid)
#     print(data)
#     # Structure as mentioned in the JavaScript code


# @sio.on('event:reset')
# def on_event_reset(data):
#     print(data)
#     # Structure as mentioned in the JavaScript code


# sio.connect('https://realtime.streamelements.com', transports=['websocket'])

# sio.wait()
