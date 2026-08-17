# AgroGuard System Documentation

**Version:** 2.0  
**Last Updated:** January 2026  
**Document Type:** Technical System Documentation

---

## Table of Contents
1. [System Use Cases](#system-use-cases)
2. [System Architecture](#system-architecture)
3. [Database Structure (ER Diagram)](#database-structure-er-diagram)
4. [API Endpoints Reference](#api-endpoints-reference)
5. [Technology Stack](#technology-stack)

---

## System Use Cases

### 1. Farmer Use Cases

#### UC-F1: Register Farmer Profile
- **Actor:** Farmer
- **Preconditions:** Mobile device with browser
- **Flow:**
  1. Opens AgroGuard PWA
  2. System detects first-time user
  3. Prompts for name and phone
  4. Generates unique device ID
  5. Stores profile locally and in database
- **Postconditions:** Profile created

#### UC-F2: Scan Crop (Online)
- **Actor:** Farmer
- **Preconditions:** Registered, internet available
- **Flow:**
  1. Selects language (en/tw/ff)
  2. Taps Camera or Gallery
  3. Captures/selects maize leaf photo
  4. System analyzes via AI model
  5. Returns disease, confidence, treatment
- **Postconditions:** Disease detected, scan saved

#### UC-F3: Scan Crop (Offline)
- **Actor:** Farmer
- **Preconditions:** No internet
- **Flow:**
  1. Captures photo offline
  2. System saves to IndexedDB
  3. Shows "Pending analysis"
  4. Auto-syncs when online
  5. Returns results
- **Postconditions:** Scan queued, synced later

#### UC-F4: View History
- **Actor:** Farmer
- **Flow:**
  1. Taps History icon
  2. Views analyzed scans
  3. Views pending scans
  4. Manually triggers analysis
  5. Deletes invalid scans
- **Postconditions:** History displayed

#### UC-F5: View Alerts
- **Actor:** Farmer
- **Flow:**
  1. AEO sends alert
  2. Badge appears on bell icon
  3. Taps bell to view
  4. Reads alert details
  5. Alert marked as read
- **Postconditions:** Alerts viewed

#### UC-F6: Contact AEO
- **Actor:** Farmer
- **Flow:**
  1. Taps Profile → Get Help
  2. Selects category
  3. Enters message
  4. Submits request
  5. AEO notified
- **Postconditions:** Support request submitted

---

### 2. AEO Use Cases

#### UC-A1: Login
- **Actor:** AEO
- **Flow:**
  1. Opens /login
  2. Enters Staff ID/Ghana Card/Phone + password
  3. System validates
  4. First login: change password
  5. Redirects to dashboard
- **Postconditions:** Authenticated

#### UC-A2: View Dashboard
- **Actor:** AEO
- **Flow:**
  1. Opens dashboard
  2. Views statistics (scans, alerts, farmers)
  3. Views charts (disease distribution, activity)
  4. Views recent scans table
- **Postconditions:** Analytics displayed

#### UC-A3: Send Alert
- **Actor:** AEO
- **Flow:**
  1. Clicks "Send Alert"
  2. Selects type (Disease/Weather/Market/Training)
  3. Selects audience (All/Region/Phone)
  4. Selects priority (High/Medium/Low)
  5. Enters title & message
  6. System estimates recipients
  7. Submits alert
- **Postconditions:** Alert broadcast to farmers

#### UC-A4: Export Data
- **Actor:** AEO
- **Flow:**
  1. Clicks "Export Report"
  2. Selects type (Farmers/Scans)
  3. Selects format (CSV/Excel)
  4. System generates file
  5. Downloads file
- **Postconditions:** Data exported

#### UC-A5: View Support Requests
- **Actor:** AEO
- **Flow:**
  1. Opens Support section
  2. Views farmer requests
  3. Selects request
  4. Views details
  5. Marks as resolved
- **Postconditions:** Request handled

#### UC-A6: Update Profile
- **Actor:** AEO
- **Flow:**
  1. Clicks profile avatar
  2. Enters name, email, phone, district
  3. Uploads profile picture
  4. Saves changes
- **Postconditions:** Profile updated

---

### 3. Super Admin Use Cases

#### UC-S1: Create AEO Account
- **Actor:** Super Admin
- **Flow:**
  1. Opens "Create AEO"
  2. Enters Staff ID, Ghana Card, Phone, Name, Email, District
  3. System generates temp password
  4. Creates account
  5. Displays credentials
- **Postconditions:** AEO account created

#### UC-S2: Manage AEO Accounts
- **Actor:** Super Admin
- **Flow:**
  1. Views AEO list
  2. Selects AEO
  3. Performs action (Activate/Deactivate/Reset Password/Update/Delete)
  4. System logs action
- **Postconditions:** AEO updated

#### UC-S3: View Audit Log
- **Actor:** Super Admin
- **Flow:**
  1. Opens Audit Log
  2. Views all actions
  3. Filters by date/type/performer
- **Postconditions:** Audit trail displayed

---

## System Architecture

### High-Level Architecture

```
┌──────────────────────────────────────────────────────┐
│              PRESENTATION LAYER                       │
├──────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌──────────┐  ┌───────────┐          │
│  │ Farmer  │  │   AEO    │  │   Super   │          │
│  │   PWA   │  │Dashboard │  │   Admin   │          │
│  └────┬────┘  └────┬─────┘  └────┬──────┘          │
│       └────────────┴─────────────┘                   │
└───────────────────┬──────────────────────────────────┘
                    │
            ┌───────▼────────┐
            │ Service Worker │
            │   (Cache v4)   │
            └───────┬────────┘
                    │
┌───────────────────▼──────────────────────────────────┐
│              APPLICATION LAYER                        │
├──────────────────────────────────────────────────────┤
│              ┌────────────┐                          │
│              │  FastAPI   │                          │
│              │  (main.py) │                          │
│              └─────┬──────┘                          │
│       ┌────────────┼────────────┐                    │
│  ┌────▼────┐  ┌───▼────┐  ┌────▼─────┐             │
│  │  Auth   │  │Disease │  │ Database │             │
│  │  (JWT)  │  │  Model │  │  Module  │             │
│  └─────────┘  └────────┘  └──────────┘             │
└──────────────────────────────────────────────────────┘
                    │
┌───────────────────▼──────────────────────────────────┐
│                DATA LAYER                             │
├──────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │TensorFlow│  │  SQLite  │  │IndexedDB │          │
│  │  Model   │  │    DB    │  │ (Client) │          │
│  └──────────┘  └──────────┘  └──────────┘          │
└──────────────────────────────────────────────────────┘
```

### Component Architecture

**Frontend (Farmer PWA):**
- Instruction Card Component
- Camera/Gallery Input
- Scan History Manager
- Offline Queue (IndexedDB)
- Profile Manager (LocalStorage)
- Alert System
- Notification System
- Language Selector

**Frontend (AEO Dashboard):**
- Statistics Widgets
- Alert Broadcasting Panel
- Report Export (CSV/Excel)
- Disease Charts (Chart.js)
- Farmers Table
- Support Tickets Panel
- Notification Bell
- Profile Manager

**Backend (FastAPI):**
- Authentication Layer (JWT, Bcrypt)
- Disease Prediction Engine (TensorFlow, OpenCV)
- Alert Management System
- Data Export Engine (CSV, Excel)
- Database Access Layer

### Data Flow Diagrams

**Disease Scan (Online):**
```
Farmer → Camera → FastAPI → AI Model → Treatment Lookup → Database → Result
```

**Offline Scan:**
```
Farmer → Camera → IndexedDB → (Wait for online) → Background Sync → FastAPI → Result
```

**Alert Broadcast:**
```
AEO → Alert Form → Validation → Database → Farmer API Poll → Display Alert
```

---

## Database Structure (ER Diagram)

### Tables Overview

```
┌─────────────────────────────────────────────────────┐
│              DATABASE: agroguard.db                  │
│                 (SQLite 3.x)                         │
└─────────────────────────────────────────────────────┘

1. FARMERS (Farmer accounts)
2. SCANS (Disease scan records)
3. AEO (Agricultural Extension Officers)
4. ALERTS (Broadcast alerts)
5. SUPERADMIN (System administrators)
6. AUDIT_LOG (Action audit trail)
7. SUPPORT_TICKETS (AEO support)
8. FARMER_SUPPORT_REQUESTS (Farmer support)
9. USERS (Legacy officer accounts)
```

### Entity-Relationship Diagram

```
┌────────────────────────────────────────────────┐
│ FARMERS                                         │
├────────────────────────────────────────────────┤
│ PK  device_id          TEXT (Unique)           │
│     name               TEXT                     │
│     phone              TEXT                     │
│     ghana_card         TEXT                     │
│     district           TEXT                     │
│     crops              TEXT                     │
│     registration_method TEXT                    │
│     registered_by      TEXT                     │
│     first_seen         TIMESTAMP                │
│     last_seen          TIMESTAMP                │
└────────────────────────────────────────────────┘
              │
              │ 1:N
              ▼
┌────────────────────────────────────────────────┐
│ SCANS                                           │
├────────────────────────────────────────────────┤
│ PK  id                 INTEGER                  │
│ FK  farmer_device_id   TEXT → FARMERS          │
│     crop               TEXT                     │
│     disease            TEXT                     │
│     confidence         REAL                     │
│     location           TEXT                     │
│     status             TEXT                     │
│     segment_id         TEXT                     │
│     timestamp          TIMESTAMP                │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│ AEO                                             │
├────────────────────────────────────────────────┤
│ PK  id                 INTEGER                  │
│ UK  staff_id           TEXT (Unique)            │
│ UK  ghana_card         TEXT (Unique)            │
│ UK  phone              TEXT (Unique)            │
│     name               TEXT                     │
│     email              TEXT                     │
│     district           TEXT                     │
│     region             TEXT                     │
│     hashed_password    TEXT                     │
│     must_change_password INTEGER                │
│     is_active          INTEGER                  │
│     biometric_id       TEXT                     │
│     profile_completed  INTEGER                  │
│     last_login         TIMESTAMP                │
│     profile_picture    TEXT                     │
└────────────────────────────────────────────────┘
              │
              │ 1:N
              ▼
┌────────────────────────────────────────────────┐
│ ALERTS                                          │
├────────────────────────────────────────────────┤
│ PK  id                 INTEGER                  │
│     alert_type         TEXT                     │
│     title              TEXT                     │
│     message            TEXT                     │
│     priority           TEXT                     │
│     target_type        TEXT                     │
│     target_audience    TEXT                     │
│     target_phone       TEXT                     │
│     district           TEXT                     │
│ FK  sent_by            INTEGER → AEO           │
│     recipient_count    INTEGER                  │
│     created_at         TIMESTAMP                │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│ SUPERADMIN                                      │
├────────────────────────────────────────────────┤
│ PK  id                 INTEGER                  │
│ UK  username           TEXT (Unique)            │
│     hashed_password    TEXT                     │
│     full_name          TEXT                     │
│     is_active          INTEGER                  │
│     created_at         TIMESTAMP                │
└────────────────────────────────────────────────┘
              │
              │ 1:N
              ▼
┌────────────────────────────────────────────────┐
│ AUDIT_LOG                                       │
├────────────────────────────────────────────────┤
│ PK  id                 INTEGER                  │
│     action             TEXT                     │
│     entity             TEXT                     │
│     entity_id          INTEGER                  │
│     performed_by       INTEGER                  │
│     timestamp          TIMESTAMP                │
│     details            TEXT                     │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│ SUPPORT_TICKETS                                 │
├────────────────────────────────────────────────┤
│ PK  id                 INTEGER                  │
│     category           TEXT                     │
│     priority           TEXT                     │
│     subject            TEXT                     │
│     description        TEXT                     │
│     contact            TEXT                     │
│ FK  submitted_by       INTEGER → AEO           │
│     status             TEXT                     │
│     created_at         TIMESTAMP                │
│     resolved_at        TIMESTAMP                │
│     resolved_by        INTEGER                  │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│ FARMER_SUPPORT_REQUESTS                         │
├────────────────────────────────────────────────┤
│ PK  id                 INTEGER                  │
│ FK  farmer_id          TEXT → FARMERS          │
│     category           TEXT                     │
│     subject            TEXT                     │
│     message            TEXT                     │
│     name               TEXT                     │
│     phone              TEXT                     │
│     status             TEXT                     │
│     created_at         TIMESTAMP                │
│     resolved_at        TIMESTAMP                │
│     resolved_by        INTEGER                  │
│     notes              TEXT                     │
└────────────────────────────────────────────────┘
```

### Relationships

```
FARMERS (1) ────< (N) SCANS
  One farmer performs multiple scans

FARMERS (1) ────< (N) FARMER_SUPPORT_REQUESTS
  One farmer submits multiple support requests

AEO (1) ────< (N) ALERTS
  One AEO sends multiple alerts

AEO (1) ────< (N) SUPPORT_TICKETS
  One AEO submits multiple support tickets

SUPERADMIN (1) ────< (N) AUDIT_LOG
  One admin performs multiple actions
```

---

## API Endpoints Reference

### Farmer Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/` | Landing page | No |
| GET | `/farmer` | Farmer PWA app | No |
| POST | `/predict?lang={en\|tw\|ff}` | Disease prediction | Device ID |
| POST | `/api/farmer/profile` | Register/update profile | Device ID |
| GET | `/api/farmer/alerts` | Get AEO alerts | Device ID |
| GET | `/api/farmer/get-all-aeos` | List AEOs | No |
| POST | `/api/farmer/support` | Submit support request | Device ID |

### AEO Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/login` | Login page | No |
| POST | `/login` | Login (form) | No |
| POST | `/api/aeo/login` | Login (API) | No |
| GET | `/dashboard` | Dashboard | JWT |
| GET | `/api/dashboard/stats` | Dashboard stats | JWT |
| POST | `/api/alert/send` | Send alert | JWT |
| POST | `/api/alert/estimate-recipients` | Estimate recipients | JWT |
| GET | `/api/export/farmers?format={csv\|excel}` | Export farmers | JWT |
| GET | `/api/export/scans?format={csv\|excel}` | Export scans | JWT |
| GET | `/api/farmers` | List farmers | JWT |
| POST | `/api/support/ticket` | Submit ticket | JWT |
| PUT | `/api/aeo/profile` | Update profile | JWT |
| POST | `/api/aeo/profile/picture` | Upload picture | JWT |

### Super Admin Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/superadmin/login` | Login page | No |
| POST | `/superadmin/login` | Login | No |
| GET | `/superadmin/dashboard` | Dashboard | JWT (Admin) |
| POST | `/api/superadmin/aeo/create` | Create AEO | JWT (Admin) |
| GET | `/api/superadmin/aeo/list` | List AEOs | JWT (Admin) |
| PUT | `/api/superadmin/aeo/{id}/toggle` | Toggle AEO status | JWT (Admin) |
| DELETE | `/api/superadmin/aeo/{id}` | Delete AEO | JWT (Admin) |
| GET | `/api/superadmin/audit-log` | View audit log | JWT (Admin) |

### Common Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/logout` | Logout | JWT |
| GET | `/about` | About page | No |
| GET | `/privacy` | Privacy policy | No |

---

## Technology Stack

### Backend
- **Framework:** FastAPI 0.104+
- **Server:** Uvicorn (ASGI)
- **Database:** SQLite 3.x
- **ORM:** Raw SQL (sqlite3 module)
- **Authentication:** JWT (PyJWT) + Bcrypt
- **AI/ML:** TensorFlow 2.x, OpenCV, PIL
- **Data Export:** openpyxl, CSV built-in
- **Templates:** Jinja2
- **Validation:** Pydantic
- **Environment:** python-dotenv

### Frontend
- **Type:** Progressive Web App (PWA)
- **Templates:** HTML5 + Jinja2
- **Styling:** Bootstrap 5.3
- **Icons:** Bootstrap Icons 1.10.5
- **Charts:** Chart.js
- **Maps:** Leaflet.js 1.9.4
- **Offline Storage:** IndexedDB
- **Caching:** Service Worker (v4)
- **JavaScript:** Vanilla ES6+

### AI/ML
- **Model:** TensorFlow Lite (.tflite)
- **Classes:** 4 (Common Rust, Gray Leaf Spot, Healthy, Northern Leaf Blight, Not Maize)
- **Accuracy:** 95%+
- **Input:** 224x224 RGB images
- **Preprocessing:** OpenCV (resize, normalize)

### Security
- **Password Hashing:** Bcrypt (cost factor 12)
- **Tokens:** JWT (30-day expiry)
- **Cookies:** HTTP-Only, Secure, SameSite
- **HTTPS:** Required in production
- **Input Validation:** Pydantic schemas
- **SQL Injection:** Parameterized queries

### Deployment
- **Platform:** Render.com
- **Auto-Deploy:** GitHub integration
- **Environment:** Python 3.9+
- **Process Manager:** Uvicorn
- **Static Files:** Served by FastAPI

### Development Tools
- **Version Control:** Git + GitHub
- **Package Manager:** pip
- **Virtual Environment:** venv
- **Code Style:** PEP 8
- **Documentation:** Markdown

---

## System Features Summary

### Farmer Features
✅ PWA offline capabilities  
✅ Camera + Gallery upload  
✅ Multi-language support (en/tw/ff)  
✅ Offline scan queue  
✅ Background sync  
✅ Scan history  
✅ Real-time alerts  
✅ AEO support requests  
✅ Profile management  

### AEO Features
✅ Dashboard analytics  
✅ Disease trend charts  
✅ Alert broadcasting  
✅ CSV/Excel export  
✅ Farmer management  
✅ Support ticket system  
✅ Profile customization  
✅ Notification system  

### Super Admin Features
✅ AEO account creation  
✅ Account management  
✅ Audit log tracking  
✅ System monitoring  
✅ Role-based access control  

### Technical Features
✅ Progressive Web App (PWA)  
✅ Offline-first architecture  
✅ AI-powered disease detection  
✅ Non-maize rejection  
✅ JWT authentication  
✅ Role-based authorization  
✅ Real-time data sync  
✅ Responsive design  
✅ Cross-platform compatibility  

---

## Contact & Support

- **GitHub:** [Natbello-20/agroguird_project](https://github.com/Natbello-20/agroguird_project)
- **Production:** [agroguard.onrender.com](https://agroguard.onrender.com)
- **Documentation:** See README.md for setup instructions

---

*AgroGuard System Documentation v2.0 - Comprehensive Technical Reference*
