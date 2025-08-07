#!/bin/bash

# Simple AWS EC2 Deployment Script for Flask To-Do App (Class Project)

echo "🚀 Starting deployment..."

# Update packages
sudo apt-get update -y

# Install Python if needed
if ! command -v python3 &> /dev/null; then
    sudo apt-get install -y python3 python3-pip
fi

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

# Initialize database
python -c "from app import init_db; init_db()"

# Set production environment
export FLASK_ENV=production

# Start the application
echo "✅ Starting application..."
gunicorn --bind 0.0.0.0:5000 wsgi:app --workers 2 --timeout 60 