from flask import Flask, render_template
import requests
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from the .env file
load_dotenv()

# Route to fetch and display clips
@app.route('/')
def fetch_clips():
    try:
        channel_name = 'NNastii'
        api_url = f'https://api.twitch.tv/helix/clips?broadcaster_name={channel_name}&first=10'

        # Access the Twitch API Client ID and access token from environment variables
        twitch_client_id = os.getenv('TWITCH_CLIENT_ID')
        
        access_token = os.getenv('TWITCH_ACCESS_TOKEN')
        
        headers = {
            'Client-ID': twitch_client_id,
            'Authorization': f'Bearer {access_token}',
        }

        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            clips_data = response.json().get('data', [])
            return render_template('clips.html', clips=clips_data)
        else:
            return f"Error: Unable to fetch clips. Status Code: {response.status_code}\nResponse Content: {response.content}"

    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(ssl_context="adhoc")