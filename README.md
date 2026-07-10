# AgroGuard — Project Proposal

## Executive Summary

**AgroGuard** is a smart, AI-powered crop disease detection and agricultural monitoring platform designed for Ghanaian farmers and Agricultural Extension Officers (AEOs). The system enables farmers to photograph their crops with any mobile device and receive an instant diagnosis of plant diseases, along with localised treatment advice — no agricultural expertise required. Extension officers gain access to a centralised web dashboard to monitor disease outbreaks, track scan activity, and respond proactively across multiple farming districts.

AgroGuard is built to work in low-connectivity, rural environments while remaining scalable for national deployment.

---

## Problem Statement

Crop diseases cause significant yield losses across Ghana every year, disproportionately affecting smallholder farmers who lack timely access to expert agricultural advice. By the time visible symptoms are noticed and an extension officer can be reached, the disease may have already spread beyond control. Farmers in remote areas face barriers of language, literacy, and limited phone capability that further delay intervention.

AgroGuard addresses these challenges by putting a diagnostic tool directly in the farmer's hands, while giving extension officers the system-level visibility they need to act at scale.

---

## Target Users

| User Type | Description |
|---|---|
| **Smallholder Farmers** | Rural farmers who photograph their crops to get instant disease diagnostics. Anonymous — no registration required. |
| **Agricultural Extension Officers (AEOs)** | Government or NGO field officers who monitor regional crop health, review outbreak trends, and deploy advisories. |
| **System Administrators** | Manage officer accounts and platform configuration. |

---

## Core Features

### 1. Crop Disease Detection (AI Scan Engine)
- Farmers upload a photo of a crop leaf through a simple web interface.
- The AI model analyses the image and identifies the disease (or confirms the plant is healthy).
- Supports crops common to Ghana: **Tomato, Corn, Potato, Cassava, Rice, and Cocoa**.
- Detects diseases including: Early Blight, Late Blight, Leaf Mold, Leaf Spot, Rice Leaf Blast, and Cocoa Frosty Pod Rot.
- Powered by a TensorFlow deep learning model (with a mock fallback for development/testing).
- Returns a **confidence score** (80–99%) alongside the disease name.
- Scans are recorded with a device ID — no personal data collected from farmers.

### 2. Multi-Language Treatment Advice
- Instant treatment recommendations are provided in the farmer's local language.
- Supported Languages:
  - **English (en)** — National language
  - **Twi (tw)** — Most widely spoken local language in Ghana
  - **Fante (ff)** — Coastal and southern Ghana
- Treatment advice includes specific fungicide names, application intervals, and practical field guidance.
- Language can be selected per API request, making the system adaptable to future language additions.

### 3. Farmer Scan Record Tracking (Anonymous)
- Each farmer is identified by an anonymous **device ID** — no account or registration required.
- First-seen and last-seen timestamps are recorded per device.
- All scan results (crop, disease, confidence, location, timestamp) are stored for aggregation.
- Supports offline-capable architecture with offline batch sync schema designed for Phase 2.

### 4. Extension Officer Authentication
- Officers register and log in via a secure web portal.
- Passwords are hashed using **bcrypt** before storage — plain text is never saved.
- Authentication is managed with **JSON Web Tokens (JWT)** via the HS256 algorithm.
- Tokens expire after a configurable period (default: 24 hours).
- Tokens are stored in **HTTP-only cookies** for session security.
- Both Cookie-based and Bearer header token strategies are supported.
- Login failures return contextual error messages without revealing system internals.

### 5. Officer Signup & Account Management
- Extension officers can self-register through a dedicated signup page.
- Password validation enforces a minimum length of 6 characters and confirms password matching before submission.
- Duplicate usernames are rejected with a clear error message.
- Upon successful registration, the officer is automatically logged in and redirected to the dashboard.

### 6. Officer Dashboard (Analytics & Monitoring)
The dashboard provides Extension Officers with a live overview of agricultural health across monitored districts. Key metrics displayed include:

| Metric | Description |
|---|---|
| **Total Scans** | Cumulative number of disease scans recorded |
| **Critical Alerts** | Count of scans flagged as High Risk |
| **Active Farmers** | Distinct device IDs seen (unique farmers using the tool) |
| **Districts Monitored** | Number of distinct locations with scan activity |

The dashboard also includes:
- **Recent Alerts Panel** — The 5 most recent High Risk disease detections with disease name, location, confidence score, and timestamp.
- **Recent Scans Table** — Last 10 scan records linked to farmer device IDs.
- **Disease Distribution Chart** — Top 5 most frequently detected diseases across all scans.
- **Daily Scans Trend Chart** — Scan volume over the last 7 days, revealing outbreak spikes or monitoring gaps.

### 7. Weather Information Panel
- Provides contextual weather data (temperature, humidity, weather condition).
- Includes a risk indicator relevant to disease outbreak likelihood.
- Designed for integration with a live weather API feed.

### 8. Role-Based Access Control (RBAC)
- The system enforces distinct user roles at the API level.
- **Officers / AEOs** have access to the dashboard, analytics, and advisory tools.
- **Farmers** are anonymous — they access only the scan endpoint.
- Protected dashboard routes redirect unauthenticated users to the login page.
- Role enforcement is built into the API dependency injection system.

---

## Planned Features (Roadmap)

### Phase 2 — Field Management & Offline Sync
- Farmers can register named **fields** with crop type, size, planting date, and GPS coordinates.
- Fields are linked to specific districts within Ghana's regional hierarchy.
- **Offline scan batching**: Scans performed without connectivity are queued on-device and synced when a connection is available.
- Batch sync API endpoint processes multiple offline scans in a single request and returns sync status per scan.

### Phase 3 — Regional Analytics & AEO Broadcast System
- **Regional Disease Analytics**: Monthly prevalence reports showing disease rates by district and region.
- **Region Status Dashboard**: Colour-coded map view of Ghana showing Green/Yellow/Red alert levels per region based on disease prevalence.
- **AEO Broadcast Messaging**: Extension officers can send advisory messages to all farmers in a region (by region ID), with configurable expiry and message type (Alert, Advice, Info).
- **Treatment Compliance Tracking**: System tracks whether recommended treatments are marked as completed and their outcomes.
- Farmer registration with email, phone, and farm name for accounts where anonymity is not preferred.

---

## Technology Stack

| Layer | Technology |
|---|---|
| **Backend Framework** | FastAPI (Python) |
| **AI / ML Model** | TensorFlow / Keras (CNN-based image classification) |
| **Image Processing** | OpenCV |
| **Database** | SQLite (local), with schema designed to migrate to PostgreSQL |
| **Authentication** | JWT (PyJWT) + bcrypt password hashing |
| **Frontend Templates** | Jinja2 HTML templates with static CSS/JS |
| **Data Validation** | Pydantic (request/response schemas) |
| **Environment Config** | python-dotenv (.env file) |
| **Server** | Uvicorn (ASGI) |

---

## Data & Privacy Approach

- Farmers are identified only by their device ID — no name, phone number, or email is collected unless a farmer opts into a named account (Phase 3).
- All scan data is stored locally in a SQLite database with no third-party data sharing.
- Officer passwords are never stored in plain text; only bcrypt hashes are persisted.
- JWT tokens are HTTP-only cookies, not accessible to JavaScript, reducing XSS exposure.

---

## Supported Crops & Diseases

| Crop | Detected Conditions |
|---|---|
| Tomato | Early Blight, Late Blight, Leaf Mold, Healthy |
| Corn | Leaf Spot, Healthy |
| Potato | Early Blight, Healthy |
| Cassava | Brown Leaf Spot, Healthy |
| Rice | Leaf Blast, Healthy |
| Cocoa | Frosty Pod Rot, Healthy |

---

## Impact & Value Proposition

- **Speed**: Farmers get a diagnosis in seconds rather than waiting days for an officer visit.
- **Accessibility**: Works on basic smartphones through a browser — no app installation required.
- **Language**: Treatment advice delivered in Twi and Fante ensures comprehension beyond English-literate users.
- **Scale**: Extension officers can monitor hundreds of farms simultaneously through the centralised dashboard.
- **Early Warning**: Outbreak trends identified from aggregated scan data allow officers to intervene before diseases spread regionally.
- **Low Barrier to Entry**: Anonymous farmer access means no registration friction — scan and get results immediately.

---

## Project Structure Overview

```
agroguird_project/
├── main.py             # API routes and application entry point
├── auth.py             # JWT token creation, validation, and role guards
├── database.py         # SQLite database setup and query functions
├── model.py            # Disease detection model loader and predictor
├── schemas.py          # Pydantic request/response data models
├── treatment.json      # Multilingual treatment advice database
├── templates/          # HTML pages (index, login, signup, dashboard)
├── static/             # CSS and JavaScript assets
├── requirements.txt    # Python dependencies
└── .env                # Environment configuration (secrets, ports)
```

---

*AgroGuard — Protecting Ghanaian crops through intelligent, accessible technology.*
#   D e p l o y m e n t   F i x  
 