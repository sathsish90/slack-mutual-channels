from flask import Flask, render_template, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import time

app = Flask(__name__)
client = WebClient(token='SlackToken')


# Cache to store user list and channel memberships
user_cache = None
channel_cache = None

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

def get_all_channels():
    global channel_cache
    if channel_cache is not None:
        return channel_cache

    try:
        response = client.conversations_list(types='public_channel,private_channel')
        channels = response['channels']
        channel_list = [{'name': channel['name'], 'id': channel['id']} for channel in channels]
        channel_cache = channel_list
        return channel_list
    except SlackApiError as e:
        print(f"Error fetching channels: {e.response['error']}")
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/users', methods=['GET'])
def users():
    users = get_users()
    return jsonify(users)

@app.route('/channels', methods=['GET'])
def channels():
    channels = get_all_channels()
    return jsonify(channels)

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
        user1_channels = {channel['name'] for channel in all_channels if user_id_1 in client.conversations_members(channel=channel['id']).get('members', [])}
        user2_channels = {channel['name'] for channel in all_channels if user_id_2 in client.conversations_members(channel=channel['id']).get('members', [])}
        mutual_channels = list(user1_channels.intersection(user2_channels))
    
    return jsonify(mutual_channels)

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    keyword = data['keyword']
    results = []
    all_channels = get_all_channels()

    for channel in all_channels:
        try:
            messages = client.conversations_history(channel=channel['id']).get('messages', [])
            for message in messages:
                if keyword.lower() in message.get('text', '').lower():
                    user_info = client.users_info(user=message['user'])
                    results.append({
                        'text': message['text'],
                        'channel': channel['name'],
                        'user': user_info['user']['name']
                    })
        except SlackApiError as e:
            print(f"Error fetching messages for channel {channel['name']}: {e.response['error']}")
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
