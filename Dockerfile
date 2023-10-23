# Use a Python 3.11.4 base image
FROM python:3.11.4

# Set the working directory
WORKDIR /app

# Copy the Flask application files into the container
COPY flask-app/ /app

# update pip
RUN pip install --upgrade pip

# Install the dependencies
RUN pip install -r requirements.txt

# Install Nginx 
RUN apt-get update && apt-get install -y nginx

# Copy over Nginx configuration file and SSL certificate files
COPY nginx.conf /etc/nginx/sites-available/default
COPY server.crt /etc/nginx/ssl/server.crt
COPY server.key /etc/nginx/ssl/server.key

# Expose the ports on which Flask app will run 
EXPOSE 80
EXPOSE 443
EXPOSE 5000

# Use a shell script to start Nginx and Gunicorn
COPY start_services.sh /start_services.sh
RUN chmod +x /start_services.sh

# start flask app
CMD ["/start_services.sh"] 