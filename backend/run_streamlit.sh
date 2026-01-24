#!/bin/bash
cd /app/backend
export $(cat .env | xargs)
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
