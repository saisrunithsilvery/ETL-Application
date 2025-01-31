#!/bin/bash

# Install Python and pip if not present
sudo apt update
sudo apt install python3 python3-pip

# Start enterprise service
cd backend/enterprise_service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export PDF_SERVICES_CLIENT_ID=YOUR CLIENT ID
export PDF_SERVICES_CLIENT_SECRET=YOUR CLIENT SECRET
export aws_access_key_id=YOUR ACCESS KEY
export aws_secret_access_key=YOUR SECRET ACCESS KEY
uvicorn main:app --reload &

# Start opensource service
cd ..
cd opensource_service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export aws_access_key_id=YOUR ACCESS KEY
export aws_secret_access_key=YOUR SECRET ACCESS KEY
uvicorn main:app --reload &

# Start frontend
cd ..
cd frontend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py