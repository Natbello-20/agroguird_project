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
# DISEASE MODEL (MOCK)
# ============================================================================

# Mock Model (Same as before)
class DiseaseModel:
    def __init__(self):
        self.diseases = [
            "Tomato___Early_blight", "Tomato___Late_blight", "Tomato___Leaf_Mold", "Tomato___Healthy",
            "Corn___Leaf_Spot", "Corn___Healthy", "Potato___Early_Blight", "Potato___Healthy",
            "Cassava___Brown_Leaf_Spot", "Cassava___Healthy", "Rice___Leaf_Blast", "Rice___Healthy",
            "Cocoa___Frosty_Pod", "Cocoa___Healthy",
        ]

    def predict(self, image_bytes):
        disease = random.choice(self.diseases)
        confidence = round(random.uniform(0.80, 0.98), 2)
        return disease, confidence

model = DiseaseModel()

# ============================================================================
# ROUTES
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict")
async def predict_disease(
    file: UploadFile = File(...),
    lang: str = Query("en"),
    device_id: str = Header(None), # Anonymous Farmer ID
    x_latitude: str = Header(None),  # GPS latitude from phone
    x_longitude: str = Header(None),  # GPS longitude from phone,
):
    try:
        # Compute segment identifier from GPS (rounded to 4 decimal places)
        segment_id: Optional[str] = None
        if x_latitude and x_longitude:
            try:
                lat = round(float(x_latitude), 4)
                lon = round(float(x_longitude), 4)
                segment_id = f"{lat}_{lon}"
            except ValueError:
                segment_id = None

        # Validate file
        if not file.content_type.startswith("image/"):
            return JSONResponse({
                "error": "Invalid file type. Please upload an image.",
                "disease": "Unknown",
                "confidence": 0,
                "treatment": ""
            })
        
        # Read image
        contents = await file.read()
        
        # Check size (5MB)
        if len(contents) > 5 * 1024 * 1024:
            return JSONResponse({
                "error": "Image too large (max 5MB)",
                "disease": "Unknown",
                "confidence": 0,
                "treatment": ""
            })
        
        # Compute segment identifier from GPS
        segment_id = None
        if x_latitude and x_longitude:
            try:
                segment_id = f"{round(float(x_latitude), 4)}_{round(float(x_longitude), 4)}"
            except ValueError:
                pass
        
        # Enforce 5-scan limit per segment
        if segment_id:
            attempt_count = database.count_scans_for_segment(device_id, segment_id)
            if attempt_count >= 5:
                return JSONResponse({
                    "error": "Scan limit reached for this field segment. Please move to a new area.",
                    "disease": "Unknown",
                    "confidence": 0,
                    "treatment": ""
                }, status_code=400)

        # Validate that the image is a maize leaf
        if not model.is_maize_leaf(contents):
            return JSONResponse({
                "error": "Non-maize leaf detected. Please upload a maize leaf image.",
                "disease": "Unknown",
                "confidence": 0,
                "treatment": ""
            }, status_code=400)

        # Predict
        disease, confidence = model.predict(contents)
        
        # Treatment Logic (Simplified)
        treatments = {
            "Tomato___Early_blight": "Apply fungicides like Mancozeb.",
            "Tomato___Late_blight": "Use copper-based fungicides.",
            "Tomato___Leaf_Mold": "Improve air circulation and use fungicides.",
            "Tomato___Healthy": "No treatment needed. Maintain good watering.",
            "Corn___Leaf_Spot": "Rotate crops and use resistant varieties.",
            "Corn___Healthy": "No treatment needed. Monitor regularly.",
            "Potato___Early_Blight": "Apply fungicides and ensure proper spacing.",
            "Potato___Healthy": "No treatment needed. Ensure good soil drainage.",
            "Cassava___Brown_Leaf_Spot": "Remove infected leaves and use resistant varieties.",
            "Cassava___Healthy": "No treatment needed. Maintain soil fertility.",
            "Rice___Leaf_Blast": "Use resistant varieties and proper nitrogen management.",
            "Rice___Healthy": "No treatment needed. Ensure adequate water.",
            "Cocoa___Frosty_Pod": "Prune infected pods and apply fungicides.",
            "Cocoa___Healthy": "No treatment needed. Maintain shade and nutrition.",
        }
        treatment = treatments.get(disease, "Consult an extension officer.")
        
        # Save to Database (include segment_id)
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
        
        if device_id:
            database.register_farmer_scan(device_id, crop, disease, confidence, location, status_text, segment_id)
        
        return JSONResponse({
            "disease": disease.replace("___", " "),
            "confidence": confidence,
            "treatment": treatment,
            "status": status_text
        })
    
    except Exception as e:
        return JSONResponse({
            "error": f"Server error: {str(e)}",
            "disease": "Unknown",
            "confidence": 0,
            "treatment": ""
        })

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
    first_run = not os.path.exists("agroguard.db")
    database.init_db()  # Always run — safely migrates existing DB
    if first_run:
        database.create_officer("admin", "admin123")  # Default officer credentials
        database.create_superadmin("superadmin", "SuperAdmin@123", "System Administrator")  # Default superadmin
        print("✓ Database initialized with default officer and superadmin accounts")
    else:
        # Ensure superadmin exists even on subsequent runs (in case DB was created before superadmin feature)
        existing_superadmin = database.get_superadmin_by_username("superadmin")
        if not existing_superadmin:
            database.create_superadmin("superadmin", "SuperAdmin@123", "System Administrator")
            print("✓ Default superadmin account created")


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = database.verify_officer(username, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    
    # Generate JWT
    access_token = auth.create_access_token(data={"sub": username, "type": "officer"})
    
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request, "error": None, "success": None})


@app.post("/signup")
async def signup(request: Request, username: str = Form(...), password: str = Form(...), confirm_password: str = Form(...)):
    # Validate passwords match
    if password != confirm_password:
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Passwords do not match", "success": None})
    
    # Validate password length
    if len(password) < 6:
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Password must be at least 6 characters", "success": None})
    
    # Try to create the officer
    try:
        database.create_officer(username, password)
        # Auto-login
        access_token = auth.create_access_token(data={"sub": username, "type": "officer"})
        response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        return response
    except Exception as e:
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Username already exists", "success": None})


@app.post("/aeo/login", response_model=schemas.TokenResponse)
async def aeo_login(login_data: schemas.AEOLoginRequest):
    """
    AEO login endpoint - accepts staff_id, ghana_card, or phone as identifier
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


if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=DEBUG)
