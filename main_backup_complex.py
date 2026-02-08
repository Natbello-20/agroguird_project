"""
AgroGuard - Minimal Phase 1 Backend
Simple, lightweight, no complex dependencies
"""

from fastapi import FastAPI, UploadFile, File, Query, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import uvicorn
import json
import random
import os
from pathlib import Path

# Load environment
from dotenv import load_dotenv
load_dotenv()

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

# Config
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Load treatment data
with open("treatment.json", "r", encoding="utf-8") as f:
    TREATMENTS = json.load(f)

# ============================================================================
# DISEASE MODEL (MOCK)
# ============================================================================

class DiseaseModel:
    """Simple mock disease detector"""
    
    diseases = [
        "Tomato___Early_blight",
        "Tomato___Late_blight",
        "Tomato___Leaf_Mold",
        "Tomato___Healthy",
        "Corn___Leaf_Spot",
        "Corn___Healthy",
        "Potato___Early_Blight",
        "Potato___Healthy",
        "Cassava___Brown_Leaf_Spot",
        "Cassava___Healthy",
        "Rice___Leaf_Blast",
        "Rice___Healthy",
        "Cocoa___Frosty_Pod",
        "Cocoa___Healthy",
    ]
    
    def predict(self, image_bytes):
        """Predict disease from image"""
        disease = random.choice(self.diseases)
        confidence = round(random.uniform(0.80, 0.98), 2)
        return disease, confidence

model = DiseaseModel()

# ============================================================================
# ROUTES
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve main UI"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/predict")
async def predict(file: UploadFile = File(...), lang: str = Query("en")):
    """
    Predict crop disease from image
    
    Args:
        file: Image file
        lang: Language (en, tw, ff)
    
    Returns:
        Disease prediction with treatment
    """
    try:
        # Validate file
        if not file.content_type.startswith("image/"):
            return {
                "error": "Invalid file type. Please upload an image.",
                "disease": "Unknown",
                "confidence": 0,
                "treatment": ""
            }
        
        # Read image
        image_bytes = await file.read()
        
        # Check size (5MB)
        if len(image_bytes) > 5 * 1024 * 1024:
            return {
                "error": "Image too large (max 5MB)",
                "disease": "Unknown",
                "confidence": 0,
                "treatment": ""
            }
        
        # Predict
        detected_class, confidence = model.predict(image_bytes)
        
        # Get treatment
        disease_info = TREATMENTS.get(detected_class, {})
        lang_data = disease_info.get(lang, disease_info.get("en", {}))
        
        return {
            "disease": lang_data.get("title", "Unknown Disease"),
            "confidence": confidence,
            "treatment": lang_data.get("treatment", "Consult with an agricultural expert")
        }
    
    except Exception as e:
        return {
            "error": f"Server error: {str(e)}",
            "disease": "Unknown",
            "confidence": 0,
            "treatment": ""
        }


@app.get("/weather")
async def get_weather():
    """Mock weather data"""
    return {
        "temp": 32,
        "humidity": 85,
        "condition": "Good",
        "risk": "Low"
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=DEBUG)
