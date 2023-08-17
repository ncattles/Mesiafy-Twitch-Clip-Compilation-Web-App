import os
from dotenv import load_dotenv
from flask import Flask, session, redirect, request, url_for, render_template
from flask_oauthlib.client import OAuth
import requests
import json
from werkzeug.urls import url_quote, url_unquote, url_encode

app = Flask(__name__)
app.secret_key = "development"

# Load environment variables from the .env file
load_dotenv()

oauth = OAuth()

twitch = oauth.remote_app('twitch',
    base_url='https://api.twitch.tv/helix/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://id.twitch.tv/oauth2/token',
    authorize_url='https://id.twitch.tv/oauth2/authorize',
    consumer_key=os.getenv('TWITCH_CLIENT_ID'),
    consumer_secret=os.getenv('TWITCH_CLIENT_SECRET'),
    request_token_params={'scope': ['user:read:email']}
)

# Route to initiate the Twitch OAuth flow using Flask-OAuthlib
@app.route('/login')
def login():
    return twitch.authorize(callback=url_for('twitch_authorized', _external=True))

# Route to handle the Twitch OAuth callback using Flask-OAuthlib
@app.route('/twitch_authorized')
def twitch_authorized():
    resp = twitch.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error'],
            request.args['error_description']
        )
    session['access_token'] = (resp['access_token'], '')
    print(session['access_token'])  # Print to verify access token
    return redirect('/')

# Function to get broadcaster ID using channel name
def get_broadcaster_id(channel_name):
    twitch_client_id = os.getenv('TWITCH_CLIENT_ID')
    api_url = f'https://api.twitch.tv/helix/users?login={channel_name}'
    
    headers = {
        'Client-ID': twitch_client_id,
        'Authorization': f'Bearer {session["access_token"][0]}'  # Use the stored access token
    }
    
    response = requests.get(api_url, headers=headers)
    data = response.json().get('data', [])
    print(response.json())  # Print to verify data
    if data:
        return data[0]['id']
    else:
        print(response.json())
        return None

# Route to fetch and display clips using Flask-OAuthlib
@app.route('/')
def fetch_clips():
    try:
        if 'access_token' not in session:
            return redirect('/login')

        channel_name = 'NNastii'
        broadcaster_id = get_broadcaster_id(channel_name)

        if not broadcaster_id:
            return "Error: Could not find broadcaster ID"

        api_url = f'https://api.twitch.tv/helix/clips?broadcaster_id={broadcaster_id}&first=10'

        access_token = session['access_token'][0]

        headers = {
            'Client-ID': os.getenv('TWITCH_CLIENT_ID'),
            'Authorization': f'Bearer {access_token}',
        }

        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            clips_data = response.json().get('data', [])
            return render_template('index.html', clips=clips_data)
        else:
            error_message = response.json().get('message')
            return f"Error: Unable to fetch clips. Status Code: {response.status_code}\nResponse Content: {error_message}"

    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(debug=True)
