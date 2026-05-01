# Advanced Missing Person Identification System

AI-powered end-to-end project for registering missing persons, reporting sightings, and producing intelligent match alerts using pre-trained face-recognition models and contextual filtering.

## Stack

- **Backend**: FastAPI + MongoDB
- **Face pipeline**: OpenCV YuNet (detection) + OpenCV SFace (embedding) pre-trained models
- **Matching logic**: embedding similarity + city + physical feature overlap
- **Frontend**: React (Vite)
- **Notifications**: SMTP email alerts

## Local Architecture

- Backend: `http://127.0.0.1:5000`
- Frontend: `http://localhost:3000`

## Backend Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Copy env template and configure:
   ```bash
   copy backend/.env.example backend/.env
   ```
4. Run API server:
   ```bash
   uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 5000
   ```

> On first face-processing request, pre-trained YuNet/SFace ONNX files are downloaded into `backend/models/` automatically.

## Frontend Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Run frontend:
   ```bash
   npm run dev
   ```

## Implemented Workflow

- Register missing person with multiple photos and descriptive data
- Upload sighting report with image + context
- Compute face embedding similarity (pre-trained model only)
- Apply contextual filtering (location + feature overlap)
- Decision thresholds:
  - `> 85%` → strong match
  - `70–85%` → possible match
  - `< 70%` → no match
- Trigger email alerts for detected matches
- Accept/reject feedback persisted for validation history
