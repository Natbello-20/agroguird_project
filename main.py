"""
AgroGuard - Phase 2 Backend
With real OpenWeatherMap weather integration
"""

import json
import os
import random
import time
import uvicorn
import httpx
from pathlib import Path
from typing import Optional, Dict, Any

# Load environment
from dotenv import load_dotenv
load_dotenv()

# FastAPI imports
from fastapi import FastAPI, Request, UploadFile, File, Header, Query, Form, HTTPException, status, Response, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# Local imports
import database
import auth
import schemas


# ============================================================================
# SETUP
# ============================================================================

app = FastAPI(title="AgroGuard", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates
templates = Jinja2Templates(directory="templates")

# Static Files
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")

# Config
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# ============================================================================
# DISEASE MODEL
# ============================================================================

# Import the disease detection model
from model import DiseaseDetectionModel

# Initialize model - FORCE REAL MODEL ONLY (No mock mode confusion)
# The real model is at: mobile_assets/maize_model.tflite
print("[INIT] Initializing disease detection model...")
try:
    model = DiseaseDetectionModel(model_path="mobile_assets/maize_model.tflite")
    print(f"✅ [MODEL] Real TensorFlow model loaded successfully!")
    print(f"✅ [MODEL] Input size: {model.image_size}, Classes: {len(model.labels)}")
except Exception as e:
    print(f"❌ [MODEL] CRITICAL ERROR: Failed to load TensorFlow model!")
    print(f"❌ [MODEL] Error: {e}")
    print(f"❌ [MODEL] Application cannot start without the model.")
    raise  # Stop the application - don't run without model

# ============================================================================
# ROUTES
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Landing page - Role selection"""
    return templates.TemplateResponse("role_selection.html", {"request": request})

@app.get("/farmer", response_class=HTMLResponse)
async def farmer_app(request: Request):
    """Farmer mobile app"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict")
async def predict_disease(
    file: UploadFile = File(...),
    lang: str = Query("en"),
    device_id: str = Header(None),  # Anonymous Farmer ID
    x_latitude: str = Header(None),  # GPS latitude from phone
    x_longitude: str = Header(None),  # GPS longitude from phone
):
    try:
        # Validate required headers for production use
        if not device_id:
            # Allow testing without device_id but log warning
            print("⚠ Warning: No device_id provided. Scan limiting disabled.")
            device_id = f"anonymous_{int(time.time())}"
        
        # Compute segment identifier from GPS (rounded to 4 decimal places = ~11 meters)
        segment_id: Optional[str] = None
        if x_latitude and x_longitude:
            try:
                lat = round(float(x_latitude), 4)
                lon = round(float(x_longitude), 4)
                segment_id = f"{lat}_{lon}"
                print(f"✓ GPS Segment: {segment_id}")
            except ValueError:
                print("⚠ Warning: Invalid GPS coordinates")
                segment_id = None
        else:
            print("⚠ Warning: No GPS coordinates provided. Location-based limiting disabled.")

        # Validate file type
        if not file.content_type.startswith("image/"):
            return JSONResponse({
                "error": "Invalid file type. Please upload an image.",
                "disease": "Invalid File",
                "confidence": 0,
                "treatment": "",
                "recommendations": []
            }, status_code=400)
        
        # Read image bytes
        contents = await file.read()
        
        # Check size (5MB)
        if len(contents) > 5 * 1024 * 1024:
            return JSONResponse({
                "error": "Image too large (max 5MB)",
                "disease": "File Too Large",
                "confidence": 0,
                "treatment": "",
                "recommendations": []
            }, status_code=400)

        # Convert bytes to OpenCV image
        import numpy as np
        import cv2
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return JSONResponse({
                "error": "Could not decode image. Please try another image.",
                "disease": "Invalid Image",
                "confidence": 0,
                "treatment": "",
                "recommendations": []
            })

        # GREEN PRE-FILTER REMOVED: Model now has "not_maize" class and can detect non-maize objects!
        # The retrained model is smart enough to reject fabric, hands, tables, etc.
        # We rely on the AI model's intelligence instead of simple color filtering.

        # Run prediction with the NEW retrained model (now has "not_maize" class!)
        print(f"[PREDICT] Starting prediction with real TensorFlow model...")
        print(f"[PREDICT] Model status - model_loaded: {model.model_loaded}")
        
        result = model.predict(img)
        disease, confidence = result[0], result[1]
        entropy = result[2] if len(result) > 2 else 0.0
        confidence_gap = result[3] if len(result) > 3 else 0.0
        
        print(f"[PREDICT] Result - Disease: {disease}, Confidence: {confidence:.4f}, Entropy: {entropy:.4f}, Gap: {confidence_gap:.4f}")
        
        if disease is None:
            return JSONResponse({
                "error": "Prediction failed. Please try again.",
                "disease": "Analysis Failed",
                "confidence": 0,
                "treatment": "",
                "recommendations": []
            })
        
        # NEW: Check if model predicted "Not_Maize" class
        if disease == "Corn___Not_Maize":
            print(f"[MODEL-REJECT] Model detected non-maize object with confidence: {confidence:.4f}")
            return JSONResponse({
                "error": "This is not a maize leaf. Please capture a maize leaf to check for diseases.",
                "disease": "Not Maize Leaf",
                "confidence": float(round(confidence, 2)),
                "treatment": "",
                "recommendations": [],
                "debug_info": {
                    "rejection_reason": "model_predicted_not_maize",
                    "confidence": float(round(confidence, 4)),
                    "entropy": float(round(entropy, 4)),
                    "confidence_gap": float(round(confidence_gap, 4))
                }
            }, status_code=400)
        
        # Additional validation for maize classes (confidence threshold)
        # Even if model says it's maize, check if it's confident enough
        
        CONFIDENCE_THRESHOLD = 0.55  # Lowered from 0.60 since model now has not_maize class
        
        if confidence < CONFIDENCE_THRESHOLD:
            print(f"[REJECT] Low confidence - model uncertain: {confidence:.4f} < {CONFIDENCE_THRESHOLD}")
            return JSONResponse({
                "error": "Image quality is too poor or unclear. Please try again with better lighting.",
                "disease": "Poor Image Quality",
                "confidence": float(round(confidence, 2)),
                "treatment": "",
                "recommendations": [],
                "debug_info": {
                    "rejection_reason": f"low confidence ({confidence:.2f} < {CONFIDENCE_THRESHOLD})",
                    "confidence": float(round(confidence, 4)),
                    "entropy": float(round(entropy, 4)),
                    "confidence_gap": float(round(confidence_gap, 4))
                }
            }, status_code=400)
        
        # Additional safety: Verify it's a corn disease (model should only output Corn___ classes)
        if not disease.startswith('Corn___'):
            return JSONResponse({
                "error": "This is not a maize leaf. Please capture a maize leaf to check for diseases.",
                "disease": "Not Maize Leaf",
                "confidence": float(round(confidence, 2)),
                "treatment": "",
                "recommendations": []
            }, status_code=400)

        # Load treatment recommendations from treatment.json
        treatment_data = _load_treatment_data()
        
        # Get treatment for detected disease
        disease_key = disease  # e.g., "Corn___Healthy"
        treatment_info = treatment_data.get(disease_key, {}).get(lang, {})
        
        # Fallback to English if language not available
        if not treatment_info:
            treatment_info = treatment_data.get(disease_key, {}).get("en", {})
        
        treatment_title = treatment_info.get("title", disease.replace("___", " "))
        treatment_text = treatment_info.get("treatment", "Consult an agricultural extension officer for guidance.")
        
        # Get detailed disease information
        disease_info = model.get_disease_info(disease)
        recommendations = disease_info.get("management", [])
        prevention = disease_info.get("prevention", [])
        
        # Save to Database
        status_text = "High Risk" if "Healthy" not in disease else "Healthy"
        crop = disease.split("___")[0]
        
        # Resolve real location from GPS coordinates
        location = "Unknown Region"
        if x_latitude and x_longitude:
            try:
                api_key = os.getenv("WEATHER_API_KEY", "")
                if api_key and api_key != "your_weather_api_key_here":
                    async with httpx.AsyncClient(timeout=3.0) as client:
                        resp = await client.get(
                            "https://api.openweathermap.org/data/2.5/weather",
                            params={"lat": x_latitude, "lon": x_longitude, "appid": api_key}
                        )
                        if resp.status_code == 200:
                            location = resp.json().get("name", "Unknown Region")
            except Exception as loc_err:
                print(f"[Location] Reverse lookup failed: {loc_err}")
        
        if device_id and not device_id.startswith("anonymous_"):
            database.register_farmer_scan(device_id, crop, disease, confidence, location, status_text, segment_id)
        
        response_data = {
            "disease": treatment_title,
            "disease_class": disease.replace("___", " "),
            "confidence": float(round(confidence, 2)),
            "treatment": treatment_text,
            "status": status_text,
            "recommendations": recommendations,
            "prevention": prevention,
            "disease_info": {
                "name": disease_info.get("name", treatment_title),
                "description": disease_info.get("description", ""),
                "symptoms": disease_info.get("symptoms", []),
                "scientific_name": disease_info.get("scientific_name", "")
            },
            "location": location
        }
        
        print(f"[SUCCESS] Returning response: disease='{treatment_title}', confidence={confidence:.2f}")
        print(f"[SUCCESS] Full disease name: {disease}")
        
        return JSONResponse(response_data)
    
    except Exception as e:
        return JSONResponse({
            "error": f"Server error: {str(e)}",
            "disease": "System Error",
            "confidence": 0,
            "treatment": "",
            "recommendations": []
        }, status_code=500)


def _load_treatment_data() -> dict:
    """Load treatment data from treatment.json file"""
    try:
        with open("treatment.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠ Could not load treatment.json: {e}")
        return {}

# ============================================================================
# WEATHER API (OpenWeatherMap - with caching & fallback)
# ============================================================================

# In-memory cache (60 second TTL)
_weather_cache: Dict[str, Any] = {}
_weather_cache_time: float = 0
WEATHER_CACHE_TTL = 60  # seconds

# Fallback data (used when API key is missing or call fails)
WEATHER_FALLBACK = {
    "temp": 32,
    "humidity": 85,
    "condition": "Partly Cloudy",
    "risk": "Medium",
    "city": "Kumasi",
    "source": "fallback"
}

def _calculate_risk(humidity: int) -> str:
    """Calculate disease outbreak risk level from humidity."""
    if humidity >= 80:
        return "High"
    elif humidity >= 60:
        return "Medium"
    return "Low"


@app.get("/weather")
async def get_weather(lat: Optional[float] = None, lon: Optional[float] = None):
    global _weather_cache, _weather_cache_time

    # Build a cache key based on location (rounded to 1 decimal for nearby reuse)
    if lat is not None and lon is not None:
        cache_key = f"{round(lat, 1)}_{round(lon, 1)}"
    else:
        cache_key = "default_city"

    # Return cached result if still fresh and same location
    now = time.time()
    if (_weather_cache 
        and _weather_cache.get("_cache_key") == cache_key 
        and (now - _weather_cache_time) < WEATHER_CACHE_TTL):
        return {k: v for k, v in _weather_cache.items() if not k.startswith("_")}

    # Read config
    api_key = os.getenv("WEATHER_API_KEY", "")
    api_url = os.getenv("WEATHER_API_URL", "https://api.openweathermap.org/data/2.5/weather")
    city = os.getenv("WEATHER_CITY", "Kumasi,GH")

    # No key set yet — return fallback silently
    if not api_key or api_key == "your_weather_api_key_here":
        return WEATHER_FALLBACK

    try:
        # Build request params — use coordinates if available, otherwise city name
        params = {"appid": api_key, "units": "metric"}
        if lat is not None and lon is not None:
            params["lat"] = lat
            params["lon"] = lon
        else:
            params["q"] = city

        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(api_url, params=params)
            resp.raise_for_status()
            raw = resp.json()

        temp = round(raw["main"]["temp"])
        humidity = raw["main"]["humidity"]
        condition = raw["weather"][0]["description"].title()
        city_name = raw["name"]
        risk = _calculate_risk(humidity)

        result = {
            "temp": temp,
            "humidity": humidity,
            "condition": condition,
            "risk": risk,
            "city": city_name,
            "source": "live"
        }

        # Cache result (with internal cache key)
        _weather_cache = {**result, "_cache_key": cache_key}
        _weather_cache_time = now
        return result

    except Exception as e:
        print(f"[Weather] API call failed: {e}. Using fallback.")
        return WEATHER_FALLBACK


# ============================================================================
# DASHBOARD & AUTH ROUTES
# ============================================================================

# Initialize DB on startup
@app.on_event("startup")
async def startup_event():
    print("🚀 [STARTUP] Initializing AgroGuard...")
    
    first_run = not os.path.exists("agroguard.db")
    
    # Always run init_db - it safely creates missing tables and columns
    print("📊 [STARTUP] Checking database schema...")
    database.init_db()
    
    if first_run:
        print("🆕 [STARTUP] First run detected - creating default accounts...")
        database.create_officer("admin", "admin123")  # Default officer credentials
        database.create_superadmin("superadmin", "SuperAdmin@123", "System Administrator")  # Default superadmin
        print("✅ [STARTUP] Database initialized with default officer and superadmin accounts")
    else:
        print("✅ [STARTUP] Database schema updated (if needed)")
        # Ensure superadmin exists even on subsequent runs (in case DB was created before superadmin feature)
        existing_superadmin = database.get_superadmin_by_username("superadmin")
        if not existing_superadmin:
            print("🔧 [STARTUP] Creating default superadmin account...")
            database.create_superadmin("superadmin", "SuperAdmin@123", "System Administrator")
            print("✅ [STARTUP] Default superadmin account created")
    
    print("✅ [STARTUP] AgroGuard backend ready!")



@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login")
async def login(
    request: Request,
    ghana_card: str = Form(None),
    staff_id: str = Form(None),
    password: str = Form(...)
):
    """
    AEO Officer login - accepts Ghana Card OR Staff ID with password created by SuperAdmin
    """
    # Determine which identifier was provided
    identifier = ghana_card or staff_id
    
    if not identifier:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Please provide either Ghana Card ID or Staff ID"
            }
        )
    
    # Retrieve AEO record by identifier
    aeo = database.get_aeo_by_identifier(identifier.strip())
    
    if not aeo:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid credentials. Please check your ID and password."
            }
        )
    
    # Check if account is active
    if not aeo['is_active']:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Your account has been deactivated. Please contact administrator."
            }
        )
    
    # Verify password using passlib context from database module
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    if not pwd_context.verify(password, aeo['hashed_password']):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid credentials. Please check your ID and password."
            }
        )
    
    # Generate JWT token
    access_token = auth.create_access_token(
        data={
            "sub": str(aeo['id']),
            "type": "aeo",
            "staff_id": aeo['staff_id'],
            "name": aeo['name']
        }
    )
    
    # Check if profile is complete (email and district must be filled)
    # Note: phone is set during account creation by superadmin, but email and district are completed by AEO
    profile_complete = (
        aeo.get('email') and aeo.get('email').strip() and
        aeo.get('district') and aeo.get('district').strip()
    )
    
    print(f"[LOGIN] AEO {aeo['staff_id']} - Profile complete: {profile_complete}")
    print(f"[LOGIN] Email: {aeo.get('email')}, District: {aeo.get('district')}")
    
    # Set cookie
    response = RedirectResponse(
        url="/complete-profile" if not profile_complete else "/dashboard",
        status_code=status.HTTP_303_SEE_OTHER
    )
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


@app.get("/complete-profile", response_class=HTMLResponse)
async def complete_profile_page(request: Request, current_user: dict = Depends(auth.get_current_user)):
    """Profile completion page for first-time AEO login"""
    return templates.TemplateResponse("complete_profile.html", {"request": request})


@app.post("/api/aeo/complete-profile")
async def complete_profile(request: Request, current_user: dict = Depends(auth.get_current_user)):
    """Save AEO profile information"""
    try:
        data = await request.json()
        
        # Update AEO profile in database
        aeo_id = current_user["user_id"]
        
        conn = database.get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE aeos
            SET name = ?, email = ?, phone = ?, district = ?
            WHERE id = ?
        """, (
            data.get('name'),
            data.get('email'),
            data.get('phone'),
            data.get('district'),
            aeo_id
        ))
        
        conn.commit()
        conn.close()
        
        return JSONResponse({"success": True, "message": "Profile updated successfully"})
        
    except Exception as e:
        print(f"[complete-profile] Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile")


@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Signup disabled - AEO accounts are created by SuperAdmin only"""
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/signup")
async def signup(request: Request):
    """Signup disabled - AEO accounts are created by SuperAdmin only"""
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/api/aeo/login", response_model=schemas.TokenResponse)
async def aeo_login_api(login_data: schemas.AEOLoginRequest):
    """
    AEO login API endpoint (for mobile/API clients) - accepts staff_id, ghana_card, or phone as identifier
    along with password. Returns JWT token on success.
    """
    # Determine which identifier was provided
    identifier = login_data.staff_id or login_data.ghana_card or login_data.phone
    
    if not identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide at least one identifier (staff_id, ghana_card, or phone)"
        )
    
    if not login_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is required"
        )
    
    # Retrieve AEO record
    aeo = database.get_aeo_by_identifier(identifier)
    
    if not aeo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check if account is active
    if not aeo['is_active']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated"
        )
    
    # Verify password using passlib context from database module
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    if not pwd_context.verify(login_data.password, aeo['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Generate JWT token
    access_token = auth.create_access_token(
        data={
            "sub": str(aeo['id']),
            "type": "aeo",
            "staff_id": aeo['staff_id']
        }
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": aeo['id'],
        "user_type": "aeo"
    }


@app.get("/superadmin/login", response_class=HTMLResponse)
async def superadmin_login_page(request: Request):
    """Super Admin login page"""
    return templates.TemplateResponse("superadmin_login.html", {"request": request, "error": None})


@app.post("/superadmin/login")
async def superadmin_login_form(request: Request, username: str = Form(...), password: str = Form(...)):
    """Super Admin login form handler (for HTML form submission with redirect)"""
    superadmin = database.verify_superadmin(username, password)
    if not superadmin:
        return templates.TemplateResponse("superadmin_login.html", {"request": request, "error": "Invalid credentials"})
    
    # Generate JWT
    access_token = auth.create_access_token(
        data={
            "sub": str(superadmin['id']),
            "type": "superadmin",
            "username": superadmin['username']
        }
    )
    
    response = RedirectResponse(url="/superadmin/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


@app.get("/superadmin/dashboard", response_class=HTMLResponse)
async def superadmin_dashboard(request: Request, current_user: dict = Depends(auth.get_superadmin_user)):
    """Super Admin dashboard page"""
    return templates.TemplateResponse("superadmin_dashboard.html", {
        "request": request,
        "user": current_user.get("username", "Super Admin")
    })


@app.post("/api/superadmin/login", response_model=schemas.TokenResponse)
async def superadmin_api_login(username: str = Form(...), password: str = Form(...)):
    """
    Super Admin API login endpoint - accepts username and password.
    Returns JWT token with superadmin privileges on success (for API clients).
    """
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required"
        )
    
    # Verify super admin credentials
    superadmin = database.verify_superadmin(username, password)
    
    if not superadmin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Generate JWT token with superadmin type
    access_token = auth.create_access_token(
        data={
            "sub": str(superadmin['id']),
            "type": "superadmin",
            "username": superadmin['username']
        }
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": superadmin['id'],
        "user_type": "superadmin"
    }


@app.post("/superadmin/aeo/create", response_model=schemas.AEOResponse)
async def create_aeo_account(
    aeo_data: schemas.AEOCreateRequest,
    current_user: dict = Depends(auth.get_superadmin_user)
):
    """
    Super Admin only endpoint to create new AEO accounts.
    Requires superadmin JWT token. Creates AEO with temporary password
    that must be changed on first login.
    """
    try:
        # Create the AEO account
        aeo_id = database.create_aeo(
            staff_id=aeo_data.staff_id,
            ghana_card=aeo_data.ghana_card,
            phone=aeo_data.phone,
            name=aeo_data.name,
            password=aeo_data.temporary_password
        )
        
        if not aeo_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="AEO account creation failed. Staff ID, Ghana Card, or Phone may already exist."
            )
        
        # Log the action in audit log
        database.log_audit(
            action="create_aeo",
            entity="aeo",
            entity_id=aeo_id,
            performed_by=current_user["user_id"],
            details=f"Created AEO account for {aeo_data.name} (Staff ID: {aeo_data.staff_id})"
        )
        
        # Retrieve the created AEO to return
        aeo = database.get_aeo_by_identifier(aeo_data.staff_id)
        
        return {
            "id": aeo['id'],
            "staff_id": aeo['staff_id'],
            "ghana_card": aeo['ghana_card'],
            "phone": aeo['phone'],
            "name": aeo['name'],
            "must_change_password": bool(aeo['must_change_password']),
            "is_active": bool(aeo['is_active'])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create AEO account: {str(e)}"
        )


# Removed duplicate login route



@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, current_user: dict = Depends(auth.get_current_user)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": current_user["user_id"]})


@app.get("/api/dashboard/stats")
async def dashboard_stats(current_user: dict = Depends(auth.get_current_user)):
    stats = database.get_dashboard_stats()
    return JSONResponse(stats)


@app.post("/register-farmer")
async def register_farmer_profile(request: Request):
    """
    Called once from the farmer app on first launch.
    Saves the farmer's real name and phone number linked to their device ID.
    """
    try:
        data = await request.json()
        device_id = data.get("device_id", "").strip()
        name      = data.get("name", "").strip()
        phone     = data.get("phone", "").strip()

        if not device_id or not name or not phone:
            raise HTTPException(status_code=400, detail="device_id, name and phone are required.")

        database.register_farmer_profile(device_id, name, phone)
        return JSONResponse({"success": True, "message": "Farmer profile saved."})

    except HTTPException:
        raise
    except Exception as e:
        print(f"[register-farmer] Error: {e}")

# -------------------------------------------------
# NEW ENDPOINT – List all registered farmers for the dashboard
# -------------------------------------------------
@app.get("/api/farmers", response_class=JSONResponse)
async def get_farmers(current_user: dict = Depends(auth.get_current_user)):
    """
    Return a list of all farmers with their device_id, name, phone and last_seen.
    Only accessible to authenticated officers.
    """
    conn = database.get_db_connection()
    cur = conn.cursor()
    rows = cur.execute(
        """
        SELECT device_id, name, phone, last_seen
        FROM farmers
        ORDER BY last_seen DESC
        """
    ).fetchall()
    conn.close()
    farmers = [
        {
            "device_id": r["device_id"],
            "name": r["name"] or "Anonymous",
            "phone": r["phone"] or "—",
            "last_seen": r["last_seen"],
        }
        for r in rows
    ]
    return JSONResponse({"farmers": farmers})


# ============================================================================
# NEW FEATURES: Add Farmer, Send Alert, Support Ticket
# ============================================================================

@app.post("/api/farmer/add")
async def add_farmer_manually(request: Request, current_user: dict = Depends(auth.get_current_user)):
    """
    AEO manually adds a farmer (for farmers without smartphones).
    Creates a virtual device_id and stores farmer information.
    """
    try:
        data = await request.json()
        
        # Validate required fields
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        district = data.get('district', '').strip()
        
        if not name or not phone or not district:
            raise HTTPException(
                status_code=400,
                detail="Name, phone, and district are required"
            )
        
        # Optional fields
        ghana_card = data.get('ghana_card', '').strip() or None
        crops = data.get('crops', '').strip() or None
        
        # Generate a virtual device_id for manually added farmers
        import hashlib
        device_id = f"manual_{hashlib.md5(phone.encode()).hexdigest()[:16]}"
        
        # Check if farmer already exists
        conn = database.get_db_connection()
        cur = conn.cursor()
        existing = cur.execute(
            "SELECT id FROM farmers WHERE phone = ? OR device_id = ?",
            (phone, device_id)
        ).fetchone()
        
        if existing:
            conn.close()
            raise HTTPException(
                status_code=400,
                detail="A farmer with this phone number already exists"
            )
        
        # Insert farmer
        cur.execute("""
            INSERT INTO farmers (device_id, name, phone, ghana_card, district, crops, registration_method, registered_by, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, 'manual', ?, datetime('now'))
        """, (device_id, name, phone, ghana_card, district, crops, current_user['user_id']))
        
        farmer_id = cur.lastrowid
        conn.commit()
        conn.close()
        
        # Log the action
        database.log_audit(
            action="add_farmer_manual",
            entity="farmer",
            entity_id=farmer_id,
            performed_by=current_user['user_id'],
            details=f"Manually added farmer: {name} ({phone})"
        )
        
        return JSONResponse({
            "success": True,
            "message": f"Farmer '{name}' added successfully",
            "farmer_id": farmer_id,
            "device_id": device_id
        })
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[add-farmer] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add farmer: {str(e)}")


@app.post("/api/alert/send")
async def send_alert_to_farmers(request: Request, current_user: dict = Depends(auth.get_current_user)):
    """
    AEO sends broadcast alert/notification to farmers.
    Can target all farmers, specific district, or specific crop type.
    """
    try:
        data = await request.json()
        
        # Validate required fields
        alert_type = data.get('alert_type', '').strip()
        target = data.get('target', '').strip()
        message = data.get('message', '').strip()
        
        if not alert_type or not target or not message:
            raise HTTPException(
                status_code=400,
                detail="Alert type, target audience, and message are required"
            )
        
        # Optional fields
        district = data.get('district', '').strip() or None
        
        # Validate district for district-specific alerts
        if target == 'district' and not district:
            raise HTTPException(
                status_code=400,
                detail="District must be specified for district-specific alerts"
            )
        
        # Build query to find target farmers
        conn = database.get_db_connection()
        cur = conn.cursor()
        
        if target == 'all':
            # All farmers
            query = "SELECT id, name, phone FROM farmers WHERE phone IS NOT NULL"
            params = ()
        elif target == 'district':
            # Specific district
            query = "SELECT id, name, phone FROM farmers WHERE district = ? AND phone IS NOT NULL"
            params = (district,)
        elif target == 'crop':
            # Specific crop type (crops field contains the crop name)
            query = "SELECT id, name, phone FROM farmers WHERE crops LIKE ? AND phone IS NOT NULL"
            params = (f"%{district}%",)  # district field is reused for crop name in UI
        else:
            raise HTTPException(status_code=400, detail="Invalid target audience")
        
        farmers = cur.execute(query, params).fetchall()
        recipient_count = len(farmers)
        
        if recipient_count == 0:
            conn.close()
            raise HTTPException(
                status_code=400,
                detail="No farmers found matching the target criteria"
            )
        
        # Store alert in database (for tracking and history)
        cur.execute("""
            INSERT INTO alerts (alert_type, target_audience, district, message, sent_by, recipient_count, created_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (alert_type, target, district, message, current_user['user_id'], recipient_count))
        
        alert_id = cur.lastrowid
        conn.commit()
        conn.close()
        
        # Log the action
        database.log_audit(
            action="send_alert",
            entity="alert",
            entity_id=alert_id,
            performed_by=current_user['user_id'],
            details=f"Sent {alert_type} alert to {recipient_count} farmers"
        )
        
        # TODO: In production, integrate with SMS gateway (e.g., Twilio, Africa's Talking)
        # For now, we just store the alert in the database
        
        recipients_text = f"{recipient_count} farmer{'s' if recipient_count != 1 else ''}"
        if target == 'district':
            recipients_text += f" in {district}"
        
        return JSONResponse({
            "success": True,
            "message": "Alert sent successfully",
            "alert_id": alert_id,
            "recipients": recipients_text,
            "recipient_count": recipient_count
        })
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[send-alert] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send alert: {str(e)}")


@app.post("/api/support/ticket")
async def create_support_ticket(request: Request, current_user: dict = Depends(auth.get_current_user)):
    """
    AEO submits a support ticket for technical issues or help requests.
    Creates a ticket that can be tracked and resolved by system administrators.
    """
    try:
        data = await request.json()
        
        # Validate required fields
        category = data.get('category', '').strip()
        priority = data.get('priority', '').strip()
        subject = data.get('subject', '').strip()
        description = data.get('description', '').strip()
        
        if not category or not priority or not subject or not description:
            raise HTTPException(
                status_code=400,
                detail="Category, priority, subject, and description are required"
            )
        
        # Optional fields
        contact = data.get('contact', '').strip() or None
        
        # Insert ticket into database
        conn = database.get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO support_tickets (
                category, priority, subject, description, contact, 
                submitted_by, status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, 'open', datetime('now'))
        """, (category, priority, subject, description, contact, current_user['user_id']))
        
        ticket_id = cur.lastrowid
        conn.commit()
        conn.close()
        
        # Log the action
        database.log_audit(
            action="create_support_ticket",
            entity="support_ticket",
            entity_id=ticket_id,
            performed_by=current_user['user_id'],
            details=f"Created {priority} priority ticket: {subject}"
        )
        
        return JSONResponse({
            "success": True,
            "message": "Support ticket submitted successfully",
            "ticket_id": f"TICK-{ticket_id:05d}"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[support-ticket] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create ticket: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=DEBUG)
