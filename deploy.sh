#!/bin/bash
# AWS EC2 Ubuntu Deployment Script
# This script is meant to be run on an Ubuntu Server 22.04 LTS instance.

echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo "Installing Python, pip, and Git..."
sudo apt install python3-pip python3-venv git -y

echo "Installing required system packages for OpenCV..."
sudo apt-get install libgl1-mesa-glx libglib2.0-0 -y

echo "Installing MongoDB..."
sudo apt-get install gnupg curl -y
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod

echo "Setting up Application..."
# Assuming you clone your repository into a directory named 'ai-hematology-analyzer'
# git clone <your-repo-url> ai-hematology-analyzer
# cd ai-hematology-analyzer

echo "Creating python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing requirements..."
pip install -r requirements.txt

echo "============================================="
echo "Deployment Environment Setup Complete!"
echo "To run the application, we recommend using 'tmux' or 'screen' to manage the processes."
echo "1. Backend:  uvicorn backend.main:app --host 0.0.0.0 --port 8000"
echo "2. Frontend: streamlit run frontend/app.py --server.port 8501"
echo ""
echo "Make sure to open inbound ports 8000 and 8501 in your EC2 Security Group settings!"
echo "============================================="
