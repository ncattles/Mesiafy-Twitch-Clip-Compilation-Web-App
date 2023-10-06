# Use a Python 3.11.4 base image
FROM python:3.11.4

# Set the working directory
WORKDIR /app

# Copy the Flask application files into the container
COPY flask-app/ /app

# Expose the port on which your Flask application will run (e.g., 5000)
EXPOSE 8080

# update pip
RUN pip install --upgrade pip

# Install the dependencies
RUN pip install -r requirements.txt

# start flask app
CMD ["flask" ,"run" ,"--host=0.0.0.0" ,"--port=8080"] 