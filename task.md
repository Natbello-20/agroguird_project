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
    - [ ] Add loading skeletons/animations
    - [ ] Mobile responsiveness tuning
- [ ] **Deployment**
    - [ ] Dockerize application
    - [ ] Deploy to cloud provider

## Debugging
- [ ] Fix 'Connection Refused' / Server Startup issue

