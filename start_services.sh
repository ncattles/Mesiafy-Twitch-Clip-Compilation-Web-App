#!/bin/bash

# Start Nginx in the background
service nginx start

# Start your Flask app using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app