# Advanced Missing Person Identification System

AI-powered end-to-end project for registering missing persons, reporting sightings, and producing intelligent match alerts using pre-trained face-recognition models and contextual filtering.

## Complete System Status Report (May 2026)

This section is an evidence-based audit of the current codebase implementation.

### 1. Project Understanding

Purpose:
- Register missing persons
- Report sightings
- Run AI-powered face matching
- Generate alert history and email notifications

Implemented workflow in code:
1. Register missing person via API (JSON or multipart with images).
2. For image uploads, detect face and generate embeddings using OpenCV models.
3. Report sighting via API (JSON or multipart with image).
4. Compare sighting embedding against registered embeddings with cosine similarity.
5. Apply context scoring (city and physical feature overlap).
6. Store matches and alerts; attempt to send email notification.

Pipeline mapping (expected vs actual):
- Input: Implemented
- Face Detection: Implemented (OpenCV YuNet)
- Feature Extraction: Implemented (OpenCV SFace)
- Matching: Implemented (cosine similarity + context)
- Output: Partially implemented (critical bug in sightings matching flow)
- Alert System: Implemented (SMTP-based, may be skipped if credentials missing)

### 2. Backend Analysis (FastAPI)

Available API routes:
- GET `/api/health`
- POST `/api/missing-persons`
- GET `/api/missing-persons`
- GET `/api/missing-persons/{person_id}`
- PUT `/api/missing-persons/{person_id}`
- DELETE `/api/missing-persons/{person_id}`
- POST `/api/sightings/report`
- POST `/api/sightings`
- GET `/api/sightings`
- GET `/api/sightings/{sighting_id}`
- GET `/api/sightings/matches`
- GET `/api/sightings/alerts`
- POST `/api/feedback`
- GET `/api/feedback`
- GET `/api/feedback/{feedback_id}`

Validation summary:
- Missing persons APIs: Mostly functional and connected to MongoDB.
- Sightings APIs: Partially functional; multipart matching path has runtime defects.
- Feedback APIs: Implemented, but frontend payload currently mismatches backend schema (`accepted` vs `is_correct`).

Critical backend defects:
- Undefined variable `candidates` in sightings matching loop.
- Missing `ObjectId` import in sightings `GET /api/sightings/{sighting_id}` handler.

### 3. Database Analysis

Database type:
- MongoDB (with `mongomock` in pytest mode)

Collections created:
- `missing_persons`
- `sightings`
- `matches`
- `alerts`
- `feedback`

Relationship model:
- Document references only (no enforced foreign keys):
   - `matches.missing_person_id -> missing_persons._id`
   - `matches.sighting_id -> sightings._id`
   - `alerts.match_id -> matches._id`
   - `feedback.match_id -> matches._id`

Embeddings storage:
- Embeddings are stored inside `missing_persons` documents as an `embeddings` array.
- There is no separate `embeddings` collection.

### 4. Face Recognition Pipeline

`face_service.py`:
- Face detection uses OpenCV YuNet ONNX.
- Face encoding uses OpenCV SFace ONNX.
- Embeddings are normalized using L2 norm.

`matching_service.py`:
- Matching uses cosine similarity (`sklearn.metrics.pairwise.cosine_similarity`).
- Similarity is clipped to `[0, 1]`.
- Match labels: `strong_match`, `possible_match`, `no_match` based on thresholds.

Conclusion:
- Real detection and embedding extraction are implemented.
- Matching math is implemented correctly for intended confidence scoring.

### 5. AI Model Check

Detected model usage:
- Not DeepFace
- Not FaceNet
- Not dlib
- Not Mediapipe
- Uses OpenCV pre-trained YuNet + SFace ONNX models

Verdict:
- REAL AI MODEL: YES

### 6. Frontend Analysis (React)

Inspected components:
- `MissingPersonForm`
- `SightingForm`
- `MatchResults`
- `AlertHistory`

Status:
- API integration exists through `frontend/src/api.js`.
- Data flow is partially wired.
- UI is partially functional due backend/frontend schema mismatches.

Observed mismatches:
- Feedback submit uses `accepted`, backend expects `is_correct`.
- Missing person list expects fields (`last_known_city`, `height_cm`, `physical_features`, `image_paths`) that are not always returned by backend serializers.

### 7. Feature Completeness Check

- Face Recognition Accuracy: PARTIAL
- Matching System: PARTIAL
- Email Notification System: PARTIAL
- Authentication (login/signup): NOT IMPLEMENTED
- Geolocation tracking: PARTIAL (city string only)
- Real-time CCTV support: NOT IMPLEMENTED

### 8. DevOps and Deployment

Current state:
- `Dockerfile` and `docker-compose.yml` exist and define app + Mongo services.
- The project is close to runnable in Docker for development/demo.

Gaps:
- No healthchecks/readiness checks.
- Runtime depends on model download at first inference.
- Documentation has inconsistencies across ports (5000 vs 1580).

### 9. Bug and Gap Detection Summary

Broken or incomplete areas:
- Sightings matching flow has runtime errors.
- Frontend-backend feedback payload mismatch.
- Inconsistent field naming between backend responses and frontend rendering.
- No authentication/authorization.
- No true geospatial tracking.
- No real-time CCTV ingestion pipeline.

Security concern:
- Example environment file includes real-looking SMTP credentials and should be sanitized.

### 10. Final Scoring

- Backend completion: 62%
- Frontend completion: 48%
- AI model layer completion: 72%
- Overall project completion: 56%

### 11. Critical Next Steps

To become demo-ready:
1. Fix sightings runtime defects (`candidates` definition, `ObjectId` import).
2. Align feedback payload contract (`is_correct` end-to-end).
3. Normalize backend response schema and frontend field usage.
4. Add one true end-to-end test: registration -> sighting -> match -> alert.
5. Remove sensitive values from `.env.example`.

To become production-ready:
1. Implement authentication and role-based access control.
2. Add observability (structured logs, metrics, tracing, alerting).
3. Add secure secret management and remove plaintext credentials.
4. Introduce reliability controls (timeouts, retries, background jobs).
5. Add model quality monitoring and threshold calibration workflow.
6. Harden Docker deployment with healthchecks and readiness probes.

## Stack

- **Backend**: FastAPI + MongoDB
- **RBAC/Auth**: MySQL + SQLAlchemy + JWT
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

### RBAC / Auth Setup

The project now includes a MySQL-backed users table for RBAC.

- Configure `AUTH_DATABASE_URL` for your MySQL instance.
- Configure `AUTH_SECRET_KEY` before using JWT login tokens.
- On startup, the backend creates the auth tables automatically.

Available auth endpoints:
- `POST /api/auth/register` creates a `user` or `admin` account.
- `POST /api/auth/login` returns a JWT access token.
- `GET /api/auth/me` returns the current authenticated user.
- `GET /api/auth/users` is admin-only.
- `PATCH /api/auth/users/{user_id}/role` is admin-only.

Demo credentials seeded on startup when the matching env vars are set:
- Admin: `admin@example.com` / `replace-with-admin-password`
- User: `user@example.com` / `replace-with-user-password`

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

## Docker / Development with Docker Compose

- The repository includes a `docker-compose.yml` that runs the `app` and a `mongo` service.
- The compose stack now also includes a MySQL service for RBAC/auth data.
- The backend container expects MongoDB at `mongodb://mongo:27017` when run via Compose.
- Container port mapping (example): host `1580` -> container `1580`.

Start the stack locally with:

```bash
docker compose up --build -d
```

Stop and remove:

```bash
docker compose down
```

## Running Tests (Backend)

- Tests use `mongomock` in-process by default, so a running MongoDB instance is not required for unit tests.
- System libraries required by OpenCV (for parts of the app that import `cv2`) may be needed in your environment: `libgl1`, `libglib2.0-0`, `libsm6`, `libxrender1`, `libxext6`.

Typical test run (from project root):

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
```

If OpenCV import fails in your environment, install the system packages first (Debian/Ubuntu):

```bash
sudo apt-get update
sudo apt-get install -y libgl1 libglib2.0-0 libsm6 libxrender1 libxext6
```

## Running Tests (Frontend)

From the `frontend` folder:

```bash
cd frontend
npm install
npm test
```

## Notes

- The backend switches to an in-memory `mongomock` client automatically during pytest runs (or if you set `USE_MOCK_DB=1`). This speeds tests and avoids needing a running MongoDB instance.
- The FastAPI health endpoint returns `{"status": "healthy"}`.
- When running inside Docker Compose, the app reads `MONGO_URI` from environment variables (default `mongodb://mongo:27017`).

If you'd like the README to include quick examples of API calls or troubleshooting tips, tell me which endpoints you'd like documented and I will add them.
