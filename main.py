"""
AgroGuard - Minimal Phase 1 Backend
Simple, lightweight, no complex dependencies
"""

import json
import os
import random
import uvicorn
from pathlib import Path
from typing import Optional

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
    device_id: str = Header(None) # Anonymous Farmer ID
):
    try:
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
        
        # Save to Database
        status_text = "High Risk" if "Healthy" not in disease else "Healthy"
        location = "Ashanti Region" # Mock location for now (browser geo would be separate)
        crop = disease.split("___")[0]
        
        if device_id:
            database.register_farmer_scan(device_id, crop, disease, confidence, location, status_text)
        
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

@app.get("/weather")
async def get_weather():
    return {
        "temp": 32,
        "humidity": 85,
        "condition": "Partly Cloudy",
        "risk": "Low"
    }


# ============================================================================
# DASHBOARD & AUTH ROUTES
# ============================================================================

# Initialize DB on startup
@app.on_event("startup")
async def startup_event():
    if not os.path.exists("agroguard.db"):
        database.init_db()
        database.create_officer("admin", "admin123")  # Default credentials


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


if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=DEBUG)
