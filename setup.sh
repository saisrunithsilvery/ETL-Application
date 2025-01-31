#!/bin/bash

# Exit on error
set -e

# Function to create and activate virtual environment
setup_venv() {
    local dir=$1
    echo "Setting up virtual environment in $dir"
    cd "$dir"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
}

# Function to start a service
start_service() {
    local service=$1
    echo "Starting $service service"
    cd "backend/${service}_service"
    setup_venv .
    
    if [ "$service" = "enterprise" ]; then
        # Enterprise-specific environment variables
        export PDF_SERVICES_CLIENT_ID=${PDF_SERVICES_CLIENT_ID:-"YOUR_CLIENT_ID"}
        export PDF_SERVICES_CLIENT_SECRET=${PDF_SERVICES_CLIENT_SECRET:-"YOUR_CLIENT_SECRET"}
    fi
    
    # Common AWS credentials
    export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:-"YOUR_ACCESS_KEY"}
    export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-"YOUR_SECRET_KEY"}
    
    echo "Starting uvicorn for $service service"
    uvicorn main:app --reload --port ${PORT:-8000} &
    sleep 5  # Wait for service to start
}

main() {
    # Install system dependencies
    echo "Updating system and installing dependencies..."
    sudo apt update
    sudo apt install -y python3 python3-pip
    
    # Store initial directory
    BASE_DIR=$(pwd)
    
    # Start backend services
    start_service "enterprise"
    cd "$BASE_DIR"
    start_service "opensource"
    
    # Start frontend
    echo "Starting frontend..."
    cd "$BASE_DIR/frontend"
    setup_venv .
    streamlit run streamlit_app.py
}

main