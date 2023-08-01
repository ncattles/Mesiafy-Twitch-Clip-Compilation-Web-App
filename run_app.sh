#!/bin/bash

# Step 1: Upgrade pip
pip install --upgrade pip

# Step 2: Install the required packages 
pip install -r requirements.txt

# Step 3: Start the Flask application
sudo flask run --cert=adhoc