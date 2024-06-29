# Slack Mutual Channels

This code helps an employee in a Slack workspace to list all fellow colleagues, list all channels created in the workspace, and find mutual channels between two employees which is not available in the slack on a single click.

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


### Step 3: Set Up & Run the Flask Application
1. Ensure your virtual environment is activated.
2. Run the Flask application:
    ```bash
    python app.py
    ```
3. Open your browser and navigate to `http://127.0.0.1:5000/`.

### Screenshots
Mutual Channels in Slack: ![Screenshot 2024-06-29 050901](https://github.com/sathsish90/slack-mutual-channels/assets/31122297/cd108d13-ae15-4d77-ae0f-9cac702e6e6d)
List of Users: ![Screenshot 2024-06-29 045342](https://github.com/sathsish90/slack-mutual-channels/assets/31122297/b19942bb-1643-4131-a117-6fd7185ce677)
List of Channels: ![Screenshot 2024-06-29 045315](https://github.com/sathsish90/slack-mutual-channels/assets/31122297/6bd9dfa4-e488-448b-af42-22aaa48f9f3d)

### Notes
- Ensure you replace `'your-slack-token-here'` with your actual Slack token.
- Make sure to handle the rate limits set by Slack API by implementing appropriate delay and caching mechanisms as demonstrated in the code.

This project demonstrates how to interact with the Slack API to fetch user and channel information, and how to create a dynamic and responsive web application using Flask and jQuery. Follow the steps carefully to set up and run the application on your local machine.
