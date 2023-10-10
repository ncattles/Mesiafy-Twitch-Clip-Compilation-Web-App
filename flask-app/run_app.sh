#!/bin/bash

# Step 1: Upgrade pip
pip install --upgrade pip

# Step 2: Install the required packages 
pip install -r requirements.txt

# Step 3: Start the Flask application
flask run --host=0.0.0.0 --port=8001