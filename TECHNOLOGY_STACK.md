# AgroGuard - Complete Technology Stack

## 📊 Overview
AgroGuard is a full-stack web application for agricultural disease detection and management, built with Python backend, modern frontend frameworks, and machine learning capabilities.

---

## 🎨 Frontend Technologies

### UI Framework
- **Bootstrap 5.3.0**
  - Purpose: Responsive UI components and grid system
  - Usage: All pages (login, dashboard, admin panel)
  - CDN: `https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css`

### Icons
- **Bootstrap Icons 1.10.5**
  - Purpose: Vector icons for UI elements
  - Usage: Navigation, forms, status indicators
  - CDN: `https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css`

### Mapping
- **Leaflet 1.9.4**
  - Purpose: Interactive maps for Ghana regions
  - Usage: Disease outbreak visualization, location tracking
  - CDN: `https://unpkg.com/leaflet@1.9.4/dist/leaflet.js`

### Data Visualization
- **Chart.js (Latest)**
  - Purpose: Disease statistics and trend charts
  - Usage: Dashboard analytics, disease prevalence graphs
  - CDN: `https://cdn.jsdelivr.net/npm/chart.js`

### Frontend Languages
- **HTML5**
  - Semantic markup for all pages
  - Progressive Web App (PWA) support via manifest.json

- **CSS3**
  - Custom styling and animations
  - Flexbox and Grid layouts
  - CSS Variables for theming
  - Gradient backgrounds
  - Responsive design with media queries

- **JavaScript (ES6+)**
  - Client-side form validation
  - AJAX requests (Fetch API)
  - Dynamic UI updates
  - Chart rendering
  - Map interactions
  - Cookie management
  - Service Worker for offline support

### Template Engine
- **Jinja2 3.1.2**
  - Purpose: Server-side HTML templating
  - Usage: Dynamic content rendering, template inheritance

---

## 🔧 Backend Technologies

### Web Framework
- **FastAPI 0.104.1**
  - Purpose: High-performance Python web framework
  - Features:
    - Async/await support
    - Automatic API documentation (Swagger/OpenAPI)
    - Data validation with Pydantic
    - Dependency injection
    - WebSocket support (future use)

### ASGI Server
- **Uvicorn 0.24.0**
  - Purpose: Lightning-fast ASGI server
  - Features:
    - Auto-reload for development
    - Production-ready performance
    - HTTP/1.1 and WebSocket support

### Programming Language
- **Python 3.12.0**
  - Modern Python features
  - Type hints for better code quality
  - Async/await for concurrent operations

---

## 🗄️ Database Technologies

### Primary Database
- **SQLite 3**
  - Purpose: Embedded relational database
  - File: `agroguard.db`
  - Features:
    - Zero configuration
    - ACID compliant
    - Lightweight and fast
    - No separate server process

### Database Tables
```sql
1. users         - Officer accounts
2. farmers       - Farmer profiles (device-linked)
3. scans         - Disease scan history
4. aeo           - Agricultural Extension Officers
5. superadmin    - Super administrator accounts
6. audit_log     - System audit trail
7. regions       - Ghana regions data
8. districts     - Ghana districts data
```

### Database Library
- **sqlite3** (Python built-in)
  - Purpose: SQLite database interface
  - Features: Row factory for dict-like access

---

## 🤖 Machine Learning & AI

### ML Framework
- **TensorFlow 2.15.0 - 2.17.0**
  - Purpose: Deep learning framework
  - Usage: Model training and inference

### Inference Engine
- **TensorFlow Lite**
  - Purpose: Lightweight model inference
  - File: `mobile_assets/maize_model.tflite`
  - Input: 224x224x3 RGB images
  - Output: 4 disease classes

### Image Processing
- **Pillow (PIL) >= 10.0.0**
  - Purpose: Image manipulation
  - Usage:
    - Image loading and preprocessing
    - Resizing to 224x224
    - Format conversion
    - Quality adjustments

### Numerical Computing
- **NumPy >= 1.24.0, < 2.0.0**
  - Purpose: Array operations and mathematical functions
  - Usage:
    - Image array manipulation
    - Confidence calculations
    - Entropy and statistical analysis

### Disease Classes (Maize)
1. Corn___Healthy
2. Corn___Common_Rust
3. Corn___Northern_Leaf_Blight
4. Corn___Gray_Leaf_Spot

---

## 🔐 Security & Authentication

### Password Hashing
- **Passlib 1.7.4**
  - Purpose: Password hashing library
  - Algorithms: bcrypt, pbkdf2

- **bcrypt 3.2.0**
  - Purpose: Secure password hashing
  - Features: Salt generation, slow hashing

### Token-Based Authentication
- **PyJWT 2.8.0**
  - Purpose: JSON Web Token implementation
  - Features:
    - Token generation
    - Token validation
    - Expiration handling
    - Algorithm: HS256

### Authentication Flow
```
1. User Login → Password verification (bcrypt)
2. Generate JWT token (PyJWT)
3. Store token in HTTP-only cookie
4. Token validation on protected routes
5. Role-based access control (SuperAdmin, AEO, Farmer)
```

---

## 🌐 External APIs & Services

### Weather API
- **OpenWeatherMap API**
  - Purpose: Real-time weather data
  - Usage: Location-based weather information
  - Endpoint: `https://api.openweathermap.org/data/2.5/weather`

### HTTP Client
- **httpx 0.27.0**
  - Purpose: Async HTTP client
  - Features:
    - Async/await support
    - HTTP/2 support
    - Connection pooling
    - Timeout handling

---

## 📝 Data & Configuration

### File Uploads
- **python-multipart 0.0.6**
  - Purpose: Form data and file upload parsing
  - Usage: Image uploads for disease detection

### Environment Variables
- **python-dotenv 1.0.0**
  - Purpose: Environment variable management
  - File: `.env`
  - Variables:
    - `USE_REAL_MODEL=true`
    - `MODEL_PATH=mobile_assets/maize_model.tflite`
    - `JWT_SECRET_KEY=...`
    - `WEATHER_API_KEY=...`

### Data Files
- **treatment.json**
  - Purpose: Disease treatment recommendations
  - Format: JSON
  - Languages: English (en), Twi (tw), Fante (ff)

- **disease_info.json**
  - Purpose: Detailed disease information
  - Contains: Symptoms, management, prevention

- **manifest.json**
  - Purpose: Progressive Web App configuration
  - Features: Installable app, offline support

---

## 📧 Validation

### Email Validation
- **email-validator 2.1.0**
  - Purpose: Email address validation
  - Features:
    - Syntax validation
    - DNS validation
    - Internationalized email support

---

## 🎯 Progressive Web App (PWA)

### Service Worker
- **File:** `static/sw.js`
- **Features:**
  - Offline caching
  - Background sync
  - Push notifications (future)

### Web App Manifest
- **File:** `static/manifest.json`
- **Features:**
  - App name and icons
  - Theme colors
  - Display mode
  - Installability

---

## 🚀 Deployment Technologies

### Runtime
- **Python 3.12.0**
  - Specified in: `runtime.txt`
  - Compatible with all dependencies

### Hosting Platform
- **Render** (Cloud Platform)
  - Features:
    - Auto-deploy from GitHub
    - Free SSL certificates
    - Auto-scaling
    - Environment variable management

### Version Control
- **Git**
  - Repository: https://github.com/Natbello-20/agroguird_project
  - `.gitignore`: Excludes .env, .venv, .db files

---

## 📁 File Storage

### Static Files
- **Directory:** `static/`
- **Contents:**
  - Images (farm_background.png)
  - Service Worker (sw.js)
  - Web App Manifest (manifest.json)

### Templates
- **Directory:** `templates/`
- **Engine:** Jinja2
- **Files:**
  - index.html (Disease detection)
  - login.html (AEO login)
  - dashboard.html (Officer dashboard)
  - superadmin_dashboard.html (Admin panel)
  - superadmin_login.html (Admin login)
  - signup.html (Disabled)

### Model Assets
- **Directory:** `mobile_assets/`
- **File:** `maize_model.tflite`
- **Size:** ~10MB
- **Format:** TensorFlow Lite

---

## 🏗️ Architecture Pattern

### Backend Pattern
- **MVC-like Structure:**
  - **Models:** `database.py`, `models/aeo.py`, `models/audit_log.py`
  - **Views:** `templates/*.html` (Jinja2)
  - **Controllers:** `main.py` (FastAPI routes)

### Additional Modules
- **auth.py** - Authentication logic
- **schemas.py** - Pydantic data models
- **model.py** - ML model interface

### Request Flow
```
Client Request
    ↓
FastAPI Route (main.py)
    ↓
Authentication (auth.py)
    ↓
Business Logic
    ↓
Database (database.py)
    ↓
Template Rendering (Jinja2)
    ↓
Response to Client
```

---

## 🔄 API Endpoints

### Public Endpoints
- `GET /` - Homepage
- `GET /login` - AEO login page
- `POST /login` - AEO login handler
- `POST /predict` - Disease prediction API

### Protected Endpoints (JWT Required)
- `GET /dashboard` - Officer dashboard
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /superadmin/dashboard` - Admin panel
- `POST /superadmin/aeo/create` - Create AEO account
- `GET /logout` - Logout handler

### API Format
- **Request:** JSON or Form Data
- **Response:** JSON
- **Authentication:** JWT in HTTP-only cookie or Authorization header

---

## 📊 Development Tools

### Code Editor
- Compatible with: VS Code, PyCharm, Sublime Text

### Recommended VS Code Extensions
- Python
- Pylance
- Jinja
- Bootstrap IntelliSense

### Development Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🌍 Localization

### Supported Languages
1. **English (en)** - Default
2. **Twi (tw)** - Ghana local language
3. **Fante (ff)** - Ghana local language

### Translation Files
- `treatment.json` - Treatment recommendations in all languages
- Query parameter: `?lang=en|tw|ff`

---

## 📈 Future Technologies (Potential)

### Planned Additions
- **Redis** - Caching and session storage
- **PostgreSQL** - Production database upgrade
- **Celery** - Background task processing
- **Docker** - Containerization
- **Nginx** - Reverse proxy and load balancing
- **React/Vue** - Frontend SPA framework
- **Socket.io** - Real-time updates
- **Sentry** - Error tracking
- **Prometheus** - Monitoring

---

## 📊 Technology Summary Table

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Backend** | FastAPI | 0.104.1 | Web framework |
| | Uvicorn | 0.24.0 | ASGI server |
| | Python | 3.12.0 | Programming language |
| **Database** | SQLite | 3 | Relational database |
| **Frontend** | Bootstrap | 5.3.0 | UI framework |
| | Chart.js | Latest | Data visualization |
| | Leaflet | 1.9.4 | Interactive maps |
| **ML/AI** | TensorFlow | 2.15-2.17 | Deep learning |
| | TensorFlow Lite | Included | Model inference |
| | Pillow | ≥10.0.0 | Image processing |
| | NumPy | 1.24-2.0 | Numerical computing |
| **Security** | bcrypt | 3.2.0 | Password hashing |
| | PyJWT | 2.8.0 | JWT authentication |
| | Passlib | 1.7.4 | Password library |
| **Utilities** | httpx | 0.27.0 | HTTP client |
| | Jinja2 | 3.1.2 | Template engine |
| | python-dotenv | 1.0.0 | Environment config |
| **Deployment** | Render | Cloud | Hosting platform |
| | Git/GitHub | - | Version control |

---

## 🎯 Key Features Enabled by Technologies

### 1. Real-time Disease Detection
- TensorFlow Lite + Pillow + NumPy

### 2. Secure Authentication
- bcrypt + PyJWT + HTTP-only cookies

### 3. Responsive UI
- Bootstrap 5 + CSS3 + JavaScript

### 4. Interactive Maps
- Leaflet + GeoJSON

### 5. Data Visualization
- Chart.js + Canvas API

### 6. Multilingual Support
- Jinja2 templates + JSON data files

### 7. Progressive Web App
- Service Worker + Web App Manifest

### 8. RESTful API
- FastAPI + Pydantic + JSON

---

## 📝 Notes

- **Zero External Database Server:** Uses SQLite for simplicity
- **Cloud-Ready:** Easily deployable to Render, AWS, Azure, GCP
- **Mobile-First:** Responsive design works on all devices
- **Offline Capable:** PWA features enable offline usage
- **Scalable:** Can migrate to PostgreSQL + Redis for production

---

**Last Updated:** January 2026  
**Python Version:** 3.12.0  
**Framework:** FastAPI 0.104.1  
**License:** MIT (if applicable)
