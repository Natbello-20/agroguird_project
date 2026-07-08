# AgroGuard Project - Tasks

## Phase 1: MVP Core (Current Focus)
- [x] **Project Setup**
    - [x] Initialize FastAPI backend (`main.py`)
    - [x] Create directory structure
    - [x] Set up environment variables (`.env`)
- [x] **Disease Detection Feature**
    - [x] Create mock model (`model.py`)
    - [x] Implement image upload endpoint
    - [x] Frontend for scanning (`index.html`)
    - [x] Display treatment recommendations
- [x] **Database & User Management**
    - [x] Initialize SQLite database (`database.py`)
    - [x] Create User/Officer tables
    - [x] Create Scan History tables
- [x] **Officer Portal**
    - [x] Implement Login page & logic
    - [x] Implement Signup page & logic
    - [x] Create Dashboard with basic stats
    - [x] Add Charts (Disease & Scans)
    - [x] Add Ghana-focused Map
- [x] **Authentication Enhancement**
    - [x] Fully integrate `auth.py` (JWT) into `main.py`
    - [x] Secure dashboard endpoints with proper dependencies

## Phase 2: Intelligence & Real Components
- [ ] **ML Integration**
    - [ ] Replace mock model with real TensorFlow model
    - [ ] Optimize image preprocessing
- [x] **External APIs**
    - [x] Integrate real Weather API (OpenWeatherMap)
    - [ ] Improve Translation API integration

## Phase 3: Polish & Deployment
- [ ] **UI/UX Improvements**
    - [x] Add Stylized Background to Auth Pages
    - [x] Add loading skeletons/animations
    - [x] Mobile responsiveness tuning
- [ ] **Deployment**
    - [ ] Dockerize application
    - [ ] Deploy to cloud provider

## Debugging
- [ ] Fix 'Connection Refused' / Server Startup issue

## New Requirements

- **Scanning Workflow**: Limit scanning to 5 attempts per 5‑yard segment. Randomly select up to five scans before analysis. Reject images that are not maize leaves.
- **Farmer Data Integration**: Link farmer name and phone number (collected on first app launch) to the AEO dashboard, including location ID and related metadata.
- **AEO Administration**: Admin creates and grants AEO staff. Extension office staff log in using staff ID, Ghana Card, and phone number, removing separate AEO signup and enabling sign‑in to access the dashboard.
- **Model & Recommendation Integration**: Load trained model files and recommendation data to provide disease diagnostics and actionable suggestions.
