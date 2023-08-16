from flask import Flask, redirect, render_template, request, session, url_for
import requests
import os
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set a secret key for session management

# Load environment variables from the .env file
load_dotenv()

# Route to initiate the Twitch OAuth flow
@app.route('/login')
def login():
    twitch_client_id = os.getenv('TWITCH_CLIENT_ID')
    redirect_uri = 'http://localhost:5000/twitch_callback'
    scope = 'user:read:email'  # Specify the required scopes
    auth_url = f'https://id.twitch.tv/oauth2/authorize?client_id={twitch_client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}'
    return redirect(auth_url)

# Route to handle the Twitch OAuth callback
@app.route('/twitch_callback')
def twitch_callback():
    # Handle the callback from Twitch after the user grants permission
    auth_code = request.args.get('code')

    # Exchange the authorization code for an access token
    access_token = exchange_code_for_token(auth_code)

    # Store the access token in the session
    session['access_token'] = access_token

    return redirect('/')

# Function to exchange authorization code for access token
def exchange_code_for_token(auth_code):
    twitch_client_id = os.getenv('TWITCH_CLIENT_ID')
    twitch_client_secret = os.getenv('TWITCH_CLIENT_SECRET')
    redirect_uri = 'http://localhost:5000/twitch_callback'
    
    token_url = 'https://id.twitch.tv/oauth2/token'
    data = {
        'client_id': twitch_client_id,
        'client_secret': twitch_client_secret,
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri
    }

    response = requests.post(token_url, data=data)
    token_data = response.json()
    
    return token_data.get('access_token')

# Function to get broadcaster ID using channel name
def get_broadcaster_id(channel_name):
    twitch_client_id = os.getenv('TWITCH_CLIENT_ID')
    api_url = f'https://api.twitch.tv/helix/users?login={channel_name}'
    
    headers = {
        'Client-ID': twitch_client_id
    }
    
    response = requests.get(api_url, headers=headers)
    data = response.json().get('data', [])
    
    if data:
        return data[0]['id']
    else:
        print(response.json())
        return None

# Route to fetch and display clips
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

        access_token = session['access_token']
        twitch_client_id = os.getenv('TWITCH_CLIENT_ID')

        headers = {
            'Client-ID': twitch_client_id,
            'Authorization': f'Bearer {access_token}',  # Make sure the format is correct
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
    app.run()