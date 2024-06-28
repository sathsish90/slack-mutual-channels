# Slack Mutual Channels

This project helps an employee in a Slack workspace to list all fellow colleagues, list all channels created in the workspace, and find mutual channels between two employees.

## Features
- List all users in the Slack workspace.
- Find mutual channels between two specified users.
- Autocomplete feature for usernames in the mutual channels search form.
- Dynamic and responsive UI.

## Prerequisites
- Python 3.x
- Flask
- Slack API token with necessary permissions

## Getting Started

### Step 1: Create a Slack App and Get Your Slack Token
1. Go to the [Slack API: Applications](https://api.slack.com/apps) page.
2. Click on "Create New App".
3. Choose "From scratch" and give your app a name and select the workspace.
4. Navigate to "OAuth & Permissions" in the left sidebar.
5. Under "Scopes", add the following OAuth scopes:
    - `users:read`
    - `users:read.email`
    - `channels:read`
    - `groups:read`
    - `mpim:read`
    - `im:read`
6. Install the app to your workspace. You will get the OAuth access token (starts with `xoxp-`).

### Step 2: Set Up Your Local Environment
1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/slack-mutual-channels.git
    cd slack-mutual-channels
    ```

2. Create a virtual environment:
    ```bash
    python -m venv venv
    ```

3. Activate the virtual environment:
    - On Windows:
      ```bash
      venv\Scripts\activate
      ```
    - On macOS/Linux:
      ```bash
      source venv/bin/activate
      ```

4. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

### Step 3: Set Up the Flask Application
1. Create a file named `app.py` in the project directory with the following content:

    ```python
    from flask import Flask, render_template, request, jsonify
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    import time

    app = Flask(__name__)
    client = WebClient(token='your-slack-token-here')

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
            channel_members = {}
            for channel in channels:
                try:
                    members_response = client.conversations_members(channel=channel['id'])
                    channel_members[channel['name']] = set(members_response['members'])
                    time.sleep(1)  # Delay to avoid rate limiting
                except SlackApiError as e:
                    print(f"Error fetching members for channel {channel['name']}: {e.response['error']}")
            channel_cache = channel_members
            return channel_members
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
            user1_channels = {channel for channel, members in all_channels.items() if user_id_1 in members}
            user2_channels = {channel for channel, members in all_channels.items() if user_id_2 in members}
            mutual_channels = list(user1_channels.intersection(user2_channels))

        return jsonify(mutual_channels)

    if __name__ == '__main__':
        app.run(debug=True)
    ```

2. Create the `templates` directory and add an `index.html` file with the following content:

    ```html
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Slack App</title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
        <link rel="stylesheet" href="https://cdn.datatables.net/1.11.3/css/jquery.dataTables.min.css">
        <link rel="stylesheet" href="{{ url_for('static', filename='jquery-ui.css') }}">
    </head>
    <body>
        <div class="container">
            <h1>Slack App</h1>
            <div class="button-container">
                <button id="userListBtn" class="btn">User List</button>
                <button id="mutualChannelsBtn" class="btn">Mutual Channels</button>
            </div>
            <div id="userListSection" class="section">
                <h2>User List</h2>
                <table id="userListTable" class="display">
                    <thead>
                        <tr>
                            <th>Username</th>
                            <th>Display Name</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- Data will be populated here by JavaScript -->
                    </tbody>
                </table>
            </div>
            <div id="mutualChannelsSection" class="section">
                <div class="form-container">
                    <form id="mutualChannelsForm">
                        <div class="form-group">
                            <label for="username1">Username 1:</label>
                            <input type="text" id="username1" name="username1" required>
                        </div>
                        <div class="form-group">
                            <label for="username2">Username 2:</label>
                            <input type="text" id="username2" name="username2" required>
                        </div>
                        <button type="submit">Submit</button>
                    </form>
                </div>
                <h2>Mutual Channels</h2>
                <table id="mutualChannelsTable" class="display">
                    <thead>
                        <tr>
                            <th>SNO</th>
                            <th>Username 1</th>
                            <th>Username 2</th>
                            <th>Mutual Channels</th>
                            <th>Edit</th>
                            <th>Delete</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- Data will be populated here by JavaScript -->
                    </tbody>
                </table>
            </div>
        </div>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script src="https://cdn.datatables.net/1.11.3/js/jquery.dataTables.min.js"></script>
        <script src="{{ url_for('static', filename='jquery-ui.js') }}"></script>
        <script src="{{ url_for('static', filename='script.js') }}"></script>
    </body>
    </html>
    ```

3. Create the `static` directory and add the following files:

    - `style.css`:

        ```css
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }

        .container {
            width: 70%;
            margin: 0 auto;
            background: #fff;
            padding: 20px;
            margin-top: 50px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }

        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 20px;
        }

        .button-container {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 20px;
        }

        .btn {
            display: inline-block;
            padding: 10px 20px;
            background: #007bff;
            color: #fff;
            text-decoration: none;
            border-radius: 4px;
            font-size: 16px;
            border: none;
            cursor: pointer;
        }

        .btn:hover {
            background: #0056b3;
        }

        .section {
            display: none;
        }

        .table-container {
            margin-top: 20px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        thead {
            background-color: #007bff;
            color: #fff;
        }

        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }

        tbody tr:nth-child(even) {
            background-color: #f9f9f9;
        }

        tbody tr:hover {
            background-color: #f1f1f1;
        }

        th {
            background-color: #007bff;
            color: white;
        }

        .form-container {
            margin-bottom: 20px;
        }

        .form-group {
            margin-bottom: 15px;
        }

        label {
            display: block;
            margin-bottom: 5px;
            color: #333;
        }

        input[type="text"] {
            width: 100%;
            padding: 8px;
            box-sizing: border-box;
            border: 1px solid #ccc;
            border-radius: 4px;
        }

        button[type="submit"] {
            display: block;
            width: 100%;
            padding: 10px;
            background: #007bff;
            color: #fff;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 10px;
        }

        button[type="submit"]:hover {
            background: #0056b3;
        }
        ```

    - `script.js`:

        ```javascript
        $(document).ready(function () {
            var mutualChannelsTable = $('#mutualChannelsTable').DataTable();
            var userListTable = $('#userListTable').DataTable();

            function fetchUsers() {
                $.ajax({
                    url: '/users',
                    type: 'GET',
                    success: function (users) {
                        userListTable.clear().draw();  // Clear existing rows
                        users.forEach(function (user) {
                            userListTable.row.add([
                                user.username,
                                user.display_name
                            ]).draw(false);
                        });
                    },
                    error: function (xhr, status, error) {
                        console.error('Error fetching users:', error);
                    }
                });
            }

            $('#userListBtn').on('click', function () {
                $('.section').hide();
                $('#userListSection').show();
                fetchUsers();
            });

            $('#mutualChannelsBtn').on('click', function () {
                $('.section').hide();
                $('#mutualChannelsSection').show();
            });

            $('#mutualChannelsForm').on('submit', function (e) {
                e.preventDefault();
                var username1 = $('#username1').val();
                var username2 = $('#username2').val();

                $.ajax({
                    url: '/mutual_channels',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ username1: username1, username2: username2 }),
                    success: function (mutualChannels) {
                        mutualChannelsTable.row.add([
                            mutualChannelsTable.rows().count() + 1,
                            username1,
                            username2,
                            mutualChannels.join(', '),
                            '<button class="edit-btn">Edit</button>',
                            '<button class="delete-btn">Delete</button>'
                        ]).draw(false);
                    },
                    error: function (xhr, status, error) {
                        console.error('Error fetching mutual channels:', error);
                    }
                });
            });

            $('#mutualChannelsTable tbody').on('click', '.delete-btn', function () {
                mutualChannelsTable.row($(this).parents('tr')).remove().draw();
            });

            $('#mutualChannelsTable tbody').on('click', '.edit-btn', function () {
                var row = mutualChannelsTable.row($(this).parents('tr'));
                var data = row.data();
                $('#username1').val(data[1]);
                $('#username2').val(data[2]);
                row.remove().draw();
            });

            $.ajax({
                url: '/users',
                type: 'GET',
                success: function (users) {
                    var usernames = users.map(function (user) { return user.username; });

                    $('#username1').autocomplete({
                        source: usernames
                    });

                    $('#username2').autocomplete({
                        source: usernames
                    });
                },
                error: function (xhr, status, error) {
                    console.error('Error fetching users for autocomplete:', error);
                }
            });
        });
        ```

    - `jquery-ui.css` and `jquery-ui.js`: Download these files from the jQuery UI website and place them in the `static` directory.

### Step 4: Run the Flask Application
1. Ensure your virtual environment is activated.
2. Run the Flask application:
    ```bash
    python app.py
    ```

3. Open your browser and navigate to `http://127.0.0.1:5000/`.

### Notes
- Ensure you replace `'your-slack-token-here'` with your actual Slack token.
- Make sure to handle the rate limits set by Slack API by implementing appropriate delay and caching mechanisms as demonstrated in the code.

## Conclusion
This project demonstrates how to interact with the Slack API to fetch user and channel information, and how to create a dynamic and responsive web application using Flask and jQuery. Follow the steps carefully to set up and run the application on your local machine.
