#!/bin/bash

# Start enterprise service
cd backend/enterprise_service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload &

# Start opensource service
cd ..
cd opensource
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload &

# Start frontend with virtual environment
cd ..
cd frontend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py