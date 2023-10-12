terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = "us-east-1"
}

# home ip address
data "aws_ssm_parameter" "ip-address" {
  name = "/info/home-ip"
}

# Security Group for Flask App
resource "aws_security_group" "flask_app_sg" {
  name        = "flask_app_sg"
  description = "Allow inbound traffic on port 80 and 443 for flask app and SSH from home IP address"

  ingress {
    description = "Allow inbound traffic on port 80 for flask app"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow inbound traffic on port 443 for flask app"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow inbound traffic on port 22 for SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["${data.aws_ssm_parameter.ip-address.value}/32"]
  }

  egress {
    description = "Allow outbound traffic on all ports"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    flask_app = "flask_app_sg"
  }
}

# docker username
data "aws_ssm_parameter" "username" {
  name = "/flask-app/username"
}

# docker password
data "aws_ssm_parameter" "password" {
  name = "/flask-app/password"
}

# Security Group for Jenkins
resource "aws_security_group" "jenkins_instance_sg" {
  name        = "jenkins_instance"
  description = "Allow inbound traffic on port 8080 for Jenkins from home IP address"

  ingress {
    description = "Allow inbound traffic on port 8080 for Jenkins"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["${data.aws_ssm_parameter.ip-address.value}/32"]
  }

  tags = {
    flask_app = "jenkins_instance_sg"
  }
}

# Route53 Record for Flask App
resource "aws_route53_record" "flask_app" {
  zone_id = "Z02316063FX4EYNPYXNY4"
  name    = "mesiafy.com"
  ttl     = 300
  type    = "A"
  records = [aws_instance.flask_app_instance.public_ip]
}

# Additional Route53 Record for Flask App
resource "aws_route53_record" "www" {
  zone_id = "Z02316063FX4EYNPYXNY4"
  name    = "www.mesiafy.com"
  ttl     = 300
  type    = "A"
  records = [aws_instance.flask_app_instance.public_ip]
}

# EC2 Instance for Flask App
resource "aws_instance" "flask_app_instance" {
  ami                    = "ami-067d1e60475437da2"
  instance_type          = "t2.micro"
  subnet_id              = "subnet-0beff5d225fe14143"
  vpc_security_group_ids = [aws_security_group.flask_app_sg.id, aws_security_group.jenkins_instance_sg.id]
  key_name               = "my-key-pair"


  user_data = <<-EOF
    #!/bin/bash

    # install Docker
    sudo yum update -y
    sudo yum install -y docker
    sudo service docker start
    sudo usermod -a -G docker ec2-user
    
    # install Jenkins
    sudo wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo
    sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key
    sudo yum upgrade
    sudo dnf install java-17-amazon-corretto -y
    sudo yum install jenkins -y
    sudo systemctl enable jenkins
    sudo systemctl start jenkins 

    # install certbot for certificate management
    sudo dnf install -y augeas-libs
    sudo python3 -m venv /opt/certbot/
    sudo /opt/certbot/bin/pip install --upgrade pip
    sudo /opt/certbot/bin/pip install certbot
    sudo /opt/certbot/bin/pip install certbot-nginx

    # login to docker
    sudo docker login -u ${data.aws_ssm_parameter.username.value} -p ${data.aws_ssm_parameter.password.value}

    # pull docker image
    sudo docker pull ncattles/twitch_flask_app:latest

    # run docker image
    sudo docker run -d -p 80:80 -p 443:443 ncattles/twitch_flask_app:latest

    # logout of docker (this will get rid of the credentials in the instance)
    sudo docker logout 

    EOF

  user_data_replace_on_change = true

  tags = {
    flask_app = "flask_app_instance"
  }
}


output "flask_app_public_ip" {
  value = aws_instance.flask_app_instance.public_ip
}

