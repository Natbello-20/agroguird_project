# AgroGuard — AI-Powered Crop Disease Detection Platform

## Executive Summary

**AgroGuard** is an intelligent, AI-powered crop disease detection and agricultural monitoring platform designed for Ghanaian farmers and Agricultural Extension Officers (AEOs). The system enables farmers to photograph their crops with any mobile device and receive instant diagnosis of plant diseases, along with localised treatment advice — no agricultural expertise required. Extension officers gain access to a centralised web dashboard to monitor disease outbreaks, track scan activity, send alerts, and respond proactively across multiple farming districts.

AgroGuard is built as a **Progressive Web App (PWA)** to work in low-connectivity, rural environments with full offline capabilities, while remaining scalable for national deployment.

---

## Problem Statement

Crop diseases cause significant yield losses across Ghana every year, disproportionately affecting smallholder farmers who lack timely access to expert agricultural advice. By the time visible symptoms are noticed and an extension officer can be reached, the disease may have already spread beyond control. Farmers in remote areas face barriers of language, literacy, limited connectivity, and limited phone capability that further delay intervention.

AgroGuard addresses these challenges by putting a diagnostic tool directly in the farmer's hands with offline capabilities, while giving extension officers the system-level visibility they need to act at scale.

---

## Target Users

| User Type | Description |
|---|---|
| **Smallholder Farmers** | Rural farmers who photograph their crops to get instant disease diagnostics. Simple registration with name and phone. |
| **Agricultural Extension Officers (AEOs)** | Government or NGO field officers who monitor regional crop health, review outbreak trends, send alerts, and deploy advisories. |
| **System Administrators** | Manage officer accounts and platform configuration. |

---

## Core Features

### 1. 🌾 Crop Disease Detection (AI Scan Engine)
- Farmers upload a photo of a crop leaf through a simple mobile-friendly web interface
- AI model analyses the image and identifies the disease (or confirms the plant is healthy)
- **Maize/Corn disease detection**: Common Rust, Gray Leaf Spot, Healthy, Northern Leaf Blight
- **Non-maize detection**: Model intelligently rejects non-maize objects (fabric, hands, tables, etc.)
- Powered by a retrained TensorFlow deep learning model with 95%+ accuracy
- Returns a **confidence score** alongside the disease name
- Scans are recorded with device ID and optional farmer profile
- **Offline scanning**: Scans can be performed without internet and auto-sync when online

### 2. 🌍 Multi-Language Treatment Advice
- Instant treatment recommendations in the farmer's local language
- Supported Languages:
  - **English (en)** — National language
  - **Twi (tw)** — Most widely spoken local language in Ghana
  - **Fante (ff)** — Coastal and southern Ghana
- Treatment advice includes specific fungicide names, application intervals, and practical field guidance
- Language can be switched on-the-fly for each scan

### 3. 📱 Progressive Web App (PWA) Features
- **Installable**: Add to home screen like a native app
- **Offline-First Architecture**: 
  - Service Worker caches all assets for offline use
  - IndexedDB stores offline scans for later analysis
  - Background sync automatically uploads pending scans when online
- **Offline Indicator**: Real-time badge shows connection status
- **Install Prompt**: Automatic PWA installation prompt with dismiss option
- Works seamlessly on iOS, Android, and desktop browsers

### 4. 📊 Offline Scan Queue System
- **Scan offline, analyze online**: Take photos without internet
- **IndexedDB Storage**: Secure local storage for pending scans
- **Auto-Sync**: Pending scans automatically analyzed when connection restored
- **History View**: See all offline scans with status (Pending/Analyzed)
- **View Results**: Tap analyzed scans to see full disease report
- **Manual Analysis**: Click "Analyze" button on pending scans
- **Smart Cleanup**: Remove invalid scans (non-maize images)
- **Badge Notification**: Shows count of unsynced scans on History icon

### 5. 🔔 Real-Time Alert System
- **AEO to Farmer Alerts**: Extension officers send alerts directly to farmers
- **Alert Targeting**:
  - Broadcast to all farmers
  - Specific region or district
  - Farmers growing specific crops
  - Individual phone numbers
- **Priority Levels**: Critical/Urgent, Important, Info
- **Alert Types**: Disease outbreaks, weather warnings, market info, training notices
- **Auto-Dismiss**: Alerts disappear when clicked
- **Read Tracking**: Badge shows unread alert count
- **Dynamic System**: Real-time updates from AEO dashboard

### 6. 🔐 Farmer Profile System
- **First-Launch Welcome**: Name and phone collection on first use
- **Privacy-Focused**: Minimal data collection
- **Profile Storage**: Secure local storage with device ID
- **Call AEO**: Direct access to Agricultural Extension Officers
- **Help & Support**: Contact system administrators

### 7. 👨‍🌾 Extension Officer Dashboard
Comprehensive analytics and management portal for AEOs:

**Quick Stats:**
- Total Scans (with % change)
- Critical Alerts count
- Active Farmers (unique users)
- Districts Monitored

**Features:**
- **Send Alerts**: Broadcast system to target farmers
- **Export Reports**: Download farmer and scan data (CSV/Excel)
- **Recent Scans**: Live feed of farmer scans
- **Disease Trends**: Visual charts and analytics
- **Weather Integration**: Risk assessment based on weather
- **Profile Management**: Update officer information
- **Support System**: Handle farmer inquiries

### 8. 📈 Data Export & Reporting
- **CSV Export**: Quick data exports for spreadsheet analysis
- **Excel Export**: Formatted reports with styling and auto-column widths
- **Farmer Data**: Export all registered farmers with contact info
- **Scan Data**: Export disease detection history with timestamps
- **openpyxl Integration**: Professional Excel formatting

### 9. 🎨 Professional UI/UX
- **Custom Notifications**: No more ugly browser alerts
- **Smooth Animations**: Slide-in notifications, fade effects
- **Color-Coded**: Green (success), Red (error), Yellow (warning)
- **Mobile-First Design**: Optimized for smartphones
- **Dark Mode Ready**: Modern glassmorphism effects
- **Responsive**: Works on all screen sizes

### 10. ☁️ Weather Information Panel
- Real-time weather data (temperature, humidity, conditions)
- Disease risk indicator based on weather
- Integration-ready for live weather API

---

## 🆕 Latest Updates (Build 2026)

### January 2026
- ✅ PWA offline capabilities with IndexedDB
- ✅ Background sync for pending scans
- ✅ Real-time AEO alert system
- ✅ Excel export with openpyxl
- ✅ Custom notification system (replaced all browser alerts)
- ✅ Non-maize image detection and rejection
- ✅ Offline scan queue with manual analysis
- ✅ Pending scan badge on History icon
- ✅ Dynamic localStorage-based notification tracking

---

## Technology Stack

| Layer | Technology |
|---|---|
| **Backend Framework** | FastAPI (Python 3.9+) |
| **AI / ML Model** | TensorFlow 2.x / Keras (Retrained CNN with not_maize class) |
| **Image Processing** | OpenCV, PIL |
| **Database** | SQLite (local), PostgreSQL-ready schema |
| **Authentication** | JWT (PyJWT) + bcrypt password hashing |
| **Frontend** | Progressive Web App (PWA) with Service Workers |
| **Offline Storage** | IndexedDB for scan queue |
| **Caching** | Service Worker Cache API (v3) |
| **Templates** | Jinja2 HTML with vanilla JavaScript |
| **Data Export** | openpyxl (Excel), CSV built-in |
| **Data Validation** | Pydantic (request/response schemas) |
| **Environment Config** | python-dotenv (.env file) |
| **Server** | Uvicorn (ASGI) |
| **Deployment** | Render.com (with auto-deploy from GitHub) |

---

## Data & Privacy Approach

- Farmers identified by device ID + optional name and phone
- Minimal data collection (name, phone) — no email, address, or sensitive info
- All scan data stored locally in SQLite with no third-party data sharing
- Officer passwords never stored in plain text; only bcrypt hashes persisted
- JWT tokens in HTTP-only cookies, not accessible to JavaScript
- IndexedDB for secure client-side offline storage
- GDPR-friendly: Users can request data deletion

---

## Supported Crops & Diseases

| Crop | Detected Conditions |
|---|---|
| **Maize/Corn** | Common Rust, Gray Leaf Spot, Healthy, Northern Leaf Blight, **Not Maize** (rejection class) |

### Coming Soon:
- Tomato: Early Blight, Late Blight, Leaf Mold
- Cassava: Brown Leaf Spot, Healthy
- Cocoa: Frosty Pod Rot, Healthy

---

## PWA Offline Features

### Service Worker (sw.js v3)
- Caches all HTML, CSS, JS, and image assets
- Serves cached content when offline
- Background sync for pending uploads
- Automatic updates when new version deployed

### IndexedDB Schema
```javascript
Database: AgroGuardOffline
Store: offlineScans
Fields:
  - id (auto-increment)
  - imageData (base64)
  - imageName, imageType
  - timestamp
  - farmerId, language
  - synced (boolean)
  - syncedAt
  - result (analysis response)
```

---

## API Endpoints

### Farmer Endpoints
- `GET /` - Farmer app (PWA)
- `POST /predict` - Disease analysis
- `GET /api/farmer/alerts` - Get AEO alerts
- `GET /api/farmer/get-all-aeos` - List available extension officers

### AEO Endpoints
- `GET /dashboard` - Officer dashboard
- `POST /api/alert/send` - Send broadcast alert
- `GET /api/export/farmers` - Export farmer data (CSV/Excel)
- `GET /api/export/scans` - Export scan data (CSV/Excel)
- `GET /api/aeo/stats` - Dashboard statistics

### Authentication
- `POST /api/aeo/register` - AEO registration
- `POST /api/aeo/login` - Officer login
- `POST /api/aeo/logout` - End session

---

## Installation & Setup

### Prerequisites
- Python 3.9+
- pip (Python package manager)

### Local Development
```bash
# Clone repository
git clone https://github.com/Natbello-20/agroguird_project.git
cd agroguird_project

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Access the app
# Farmer app: http://localhost:8000
# AEO dashboard: http://localhost:8000/dashboard
```

### Production Deployment (Render.com)
1. Push code to GitHub
2. Connect Render to repository
3. Auto-deploy on every push to main branch
4. Environment variables configured in Render dashboard

---

## Project Structure

```
agroguird_project/
├── main.py                 # API routes and application entry
├── auth.py                 # JWT authentication & authorization
├── database.py             # Database operations
├── model.py                # AI model loader and predictor
├── treatment.json          # Multilingual treatment database
├── requirements.txt        # Python dependencies
├── .env                    # Environment configuration
├── templates/
│   ├── index.html         # Farmer PWA app
│   ├── dashboard.html     # AEO dashboard
│   ├── login.html         # Officer login
│   ├── role_selection.html # User type selection
│   └── complete_profile.html # AEO onboarding
├── static/
│   ├── sw.js              # Service Worker (PWA)
│   ├── manifest.json      # PWA manifest
│   └── images/            # Logo and assets
└── mobile_assets/
    ├── maize_model.tflite # AI model
    └── labels.txt         # Class labels
```

---

## Impact & Value Proposition

- **Speed**: Farmers get diagnosis in seconds vs. days waiting for officer visit
- **Accessibility**: Works on basic smartphones through browser — no app store needed
- **Offline-First**: Works without internet, syncs automatically when online
- **Language**: Treatment advice in Twi and Fante ensures comprehension
- **Scale**: Extension officers monitor hundreds of farms simultaneously
- **Early Warning**: Outbreak trends from aggregated data enable proactive intervention
- **Real-Time Alerts**: Officers can instantly notify farmers of disease outbreaks
- **Data-Driven**: Export and analyze farmer and scan data for insights
- **Low Barrier**: Simple registration, works immediately

---

## Future Roadmap

### Phase 2 (Q2 2026)
- [ ] SMS alert integration (Twilio/Africa's Talking)
- [ ] WhatsApp alert delivery
- [ ] Field management (GPS, crop tracking)
- [ ] History pagination (show 20, load more)
- [ ] Auto-cleanup old scans (keep 100 max)
- [ ] Search and filter history

### Phase 3 (Q3 2026)
- [ ] Regional disease maps
- [ ] Predictive analytics (ML-based outbreak prediction)
- [ ] Farmer-to-farmer messaging
- [ ] Market price information
- [ ] Weather-based planting recommendations
- [ ] Multi-crop support (Cassava, Tomato, Cocoa)

---

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## License

Copyright © 2026 AgroGuard Team. All rights reserved.

---

## Contact & Support

- **GitHub**: [Natbello-20/agroguird_project](https://github.com/Natbello-20/agroguird_project)
- **Deployment**: [agroguard.onrender.com](https://agroguard.onrender.com)

---

*AgroGuard — Protecting Ghanaian crops through intelligent, accessible, offline-first technology.*
