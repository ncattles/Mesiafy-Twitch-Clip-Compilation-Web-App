---

# Mesiafy - Twitch Clip Finder Website

![Mesiafy Screenshot](./images/Enter%20Twitch%20Channel.png)

Mesiafy is a web application that allows users to search for Twitch streamer usernames and retrieve information about their clips. It was hosted as a Docker container on an AWS EC2 instance with the URL [mesiafy.com](http://mesiafy.com).

## Features

- **Search for Twitch Streamers:** Users can search for their favorite Twitch streamers by entering their usernames.

- **Retrieve Clip Information:** Mesiafy fetches information about clips associated with the provided Twitch streamer username. This information includes the creation date and view count of each clip.

- **OAuth 2.0 Authorization:** Mesiafy uses the OAuth 2.0 protocol to authorize with Twitch, allowing it to make API calls to retrieve clip data.

- **Nginx Reverse Proxy:** The backend of the website is configured with an Nginx web server that acts as a reverse proxy. It forwards requests made to the container on port 80 0r 443 to the port that the Flask application is running on.

- **Gunicorn WSGI HTTP Server:** Requests made to the nginx web server are forwarded to the flask backend using gunicorn that run with multiple workers to allow for multiple request handling

## Usage

NOTE: This site was recently taken down due to the growing expenses to keep it hosted.

1. Open your web browser and navigate to [http://mesiafy.com](http://mesiafy.com).

2. Enter the Twitch streamer's username in the search bar and click "Submit."

3. Mesiafy will retrieve and display information about the streamer's clips.

![Mesiafy Demo](./images/Clips.png)

---
