# AI Hematology Analyzer

A complete end-to-end web application that automates Complete Blood Count (CBC) by scanning microscopic slides to detect and count RBCs, WBCs, and Platelets.

## Features
- **YOLOv11 Inference** for rapid and accurate object detection of blood cells.
- **FastAPI Backend** that serves inference results and interfaces with MongoDB.
- **Streamlit Frontend Dashboard** providing a highly interactive user UI to upload scans and view historical reports.
- **Persistent Data** saved to MongoDB for scan history.

## Project Structure
- `backend/` - FastAPI backend (`main.py`)
- `frontend/` - Streamlit application (`app.py`)
- `training/` - Scripts to download datasets (`download_dataset.py`) and train YOLOv11 (`train_yolo.py`)
- `requirements.txt` - Python dependencies

## Setup and Running Locally

1. **Install Dependencies**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **MongoDB Setup**
   Ensure you have MongoDB running locally on port 27017, or set the `MONGO_URI` environment variable to your remote cluster.

3. **Train the Model (Optional)**
   If you want to train your own YOLOv11 model instead of using the default (`yolov11n` fallback):
   ```bash
   cd training
   export ROBOFLOW_API_KEY="your_api_key_here"  # Setup Roboflow to download dataset
   python download_dataset.py
   python train_yolo.py
   ```

4. **Start the Backend API**
   Open a new terminal, activate the venv, and run:
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Start the Frontend Dashboard**
   Open another terminal, activate the venv, and run:
   ```bash
   streamlit run frontend/app.py
   ```
   Navigate to `http://localhost:8501` to use the analyzer!

## AWS EC2 Deployment
See the `deploy.sh` script for full instructions on setting up the environment on a fresh Ubuntu EC2 instance.
