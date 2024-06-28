from flask import Flask, render_template, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import time
import threading

app = Flask(__name__)
client = WebClient(token='xoxe.xoxp-1-Mi0yLTI4NzY4MzE1Mzc5MjItNjYyMjE2NTAxMDMzOC03MzQ2OTc3ODczMTg2LTczNDQ2MTMyMTU2MDYtNWVkN2FlMmRkMGI5MTRlN2JhNDcyYjMyZWI4NzA0MzdkM2JmMGI4MzlhOWQ3M2Q4M2IxNTNiYWJhOGZjZmE1Mw')

# Cache to store user list and channel memberships
user_cache = None
channel_cache = None
channel_lock = threading.Lock()

def get_users():
    global user_cache
    if user_cache is not None:
        return user_cache

    try:
        response = client.users_list()
        users = response['members']
        user_list = [{
            'username': user['name'],
            'display_name': user['profile'].get('real_name', 'N/A'),
            'id': user.get('id', 'N/A')
        } for user in users]
        user_list.sort(key=lambda x: x['username'])
        user_cache = user_list
        return user_list
    except SlackApiError as e:
        print(f"Error fetching users: {e.response['error']}")
        return []

def get_user_id(username):
    users = get_users()
    for user in users:
        if user['username'] == username:
            return user['id']
    return None

def fetch_channel_members(channel):
    try:
        members_response = client.conversations_members(channel=channel['id'])
        with channel_lock:
            channel_cache[channel['name']] = set(members_response['members'])
    except SlackApiError as e:
        print(f"Error fetching members for channel {channel['name']}: {e.response['error']}")

def get_all_channels():
    global channel_cache
    if channel_cache is not None:
        return channel_cache

    try:
        response = client.conversations_list(types='public_channel,private_channel')
        channels = response['channels']
        channel_cache = {}

        threads = []
        for channel in channels:
            thread = threading.Thread(target=fetch_channel_members, args=(channel,))
            thread.start()
            threads.append(thread)
            time.sleep(0.1)  # Slight delay to avoid rate limiting

        for thread in threads:
            thread.join()

        return channel_cache
    except SlackApiError as e:
        print(f"Error fetching channels: {e.response['error']}")
        return {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/users', methods=['GET'])
def users():
    users = get_users()
    return jsonify(users)

@app.route('/mutual_channels', methods=['POST'])
def mutual_channels():
    data = request.json
    username1 = data['username1']
    username2 = data['username2']
    
    user_id_1 = get_user_id(username1)
    user_id_2 = get_user_id(username2)
    
    mutual_channels = []
    if user_id_1 and user_id_2:
        all_channels = get_all_channels()
        user1_channels = {channel for channel in all_channels if user_id_1 in all_channels[channel]}
        user2_channels = {channel for channel in all_channels if user_id_2 in all_channels[channel]}
        mutual_channels = list(user1_channels.intersection(user2_channels))
    
    return jsonify(list(mutual_channels))

if __name__ == '__main__':
    app.run(debug=True)
