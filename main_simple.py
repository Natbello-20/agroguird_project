"""
AgroGuard - Crop Disease Detection API
Simple, minimal implementation for Ghana farmers
"""

from fastapi import FastAPI, UploadFile, File, Query, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import random
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import bcrypt
import jwt

# Load environment
load_dotenv()

# ============================================================
# DATABASE SETUP - SQLITE ONLY
# ============================================================
DATABASE_URL = "sqlite:///./agroguard.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Farmer(Base):
    __tablename__ = "farmers"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True)
    name = Column(String, default="Anonymous Farmer")
    created_at = Column(DateTime, default=datetime.utcnow)

class Scan(Base):
    __tablename__ = "scans"
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, index=True)
    disease = Column(String)
    confidence = Column(Float)
    treatment = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# ============================================================
# FASTAPI APP
# ============================================================
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

# Load treatments
with open("treatment.json", "r", encoding="utf-8") as f:
    TREATMENTS = json.load(f)

# Disease list
DISEASES = [
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Corn___Leaf_Spot",
    "Potato___Early_Blight",
    "Cassava___Brown_Leaf_Spot",
    "Rice___Leaf_Blast",
    "Cocoa___Frosty_Pod"
]

# Get DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================
# ROUTES
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve frontend"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/predict")
async def predict(
    file: UploadFile = File(...),
    device_id: str = Query(...),
    lang: str = Query("en"),
    db: Session = Depends(get_db)
):
    """Predict disease from image"""
    
    # Get or create farmer
    farmer = db.query(Farmer).filter(Farmer.device_id == device_id).first()
    if not farmer:
        farmer = Farmer(device_id=device_id)
        db.add(farmer)
        db.commit()
        db.refresh(farmer)
    
    # Mock prediction (no TensorFlow needed)
    disease = random.choice(DISEASES)
    confidence = round(random.uniform(0.85, 0.99), 2)
    
    # Get treatment
    disease_data = TREATMENTS.get(disease, {})
    treatment = disease_data.get(lang, disease_data.get("en", {}).get("treatment", "Consult expert"))
    
    # Save scan
    scan = Scan(
        farmer_id=farmer.id,
        disease=disease,
        confidence=confidence,
        treatment=treatment
    )
    db.add(scan)
    db.commit()
    
    return {
        "disease": disease.replace("___", " "),
        "confidence": confidence,
        "treatment": treatment
    }

@app.get("/api/scans/{device_id}")
async def get_scans(device_id: str, db: Session = Depends(get_db)):
    """Get scan history for device"""
    farmer = db.query(Farmer).filter(Farmer.device_id == device_id).first()
    if not farmer:
        return {"scans": []}
    
    scans = db.query(Scan).filter(Scan.farmer_id == farmer.id).order_by(Scan.created_at.desc()).all()
    return {"scans": [{"id": s.id, "disease": s.disease, "confidence": s.confidence, "date": s.created_at} for s in scans]}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
