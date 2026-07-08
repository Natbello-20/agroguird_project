"""
AgroGuard Pydantic Schemas for API validation
Defines request/response models for all endpoints
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List


# ============================================================================
# AUTHENTICATION SCHEMAS
# ============================================================================

class FarmerRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    phone_number: Optional[str] = None
    device_id: str  # For offline sync tracking
    farm_name: Optional[str] = None
    district_id: Optional[int] = None


class FarmerLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AEOLoginRequest(BaseModel):
    staff_id: Optional[str] = None
    ghana_card: Optional[str] = None
    phone: Optional[str] = None
    password: str


class AEOCreateRequest(BaseModel):
    staff_id: str = Field(..., min_length=3)
    ghana_card: str = Field(..., min_length=10)
    phone: str = Field(..., min_length=10)
    name: str = Field(..., min_length=2)
    temporary_password: str = Field(..., min_length=8)


class AEOResponse(BaseModel):
    id: int
    staff_id: str
    ghana_card: str
    phone: str
    name: str
    must_change_password: bool
    is_active: bool
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    user_type: str  # "farmer" or "aeo"


class FarmerResponse(BaseModel):
    id: int
    email: str
    full_name: str
    farm_name: Optional[str]
    district_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# LOCATION SCHEMAS
# ============================================================================

class RegionResponse(BaseModel):
    id: int
    name: str
    region_code: str
    lat: Optional[float]
    lng: Optional[float]
    
    class Config:
        from_attributes = True


class DistrictResponse(BaseModel):
    id: int
    name: str
    region_id: int
    lat: Optional[float]
    lng: Optional[float]
    
    class Config:
        from_attributes = True


class DistrictListResponse(BaseModel):
    districts: List[DistrictResponse]


# ============================================================================
# FIELD SCHEMAS
# ============================================================================

class FieldCreateRequest(BaseModel):
    field_name: str
    crop_type: str
    crop_variety: Optional[str] = None
    size_hectares: Optional[float] = None
    district_id: int
    planting_date: Optional[datetime] = None
    expected_harvest_date: Optional[datetime] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class FieldResponse(BaseModel):
    id: int
    field_name: str
    crop_type: str
    crop_variety: Optional[str]
    size_hectares: Optional[float]
    district_id: int
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class FieldListResponse(BaseModel):
    fields: List[FieldResponse]


# ============================================================================
# SCAN SCHEMAS (PHASE 1)
# ============================================================================

class ScanCreateRequest(BaseModel):
    field_id: int
    disease_detected: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    crop_type: str
    image_path: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    soil_moisture: Optional[str] = None  # "Wet", "Moist", "Dry"
    weather_condition: Optional[str] = None  # "Sunny", "Rainy", "Cloudy"
    notes: Optional[str] = None
    device_id: Optional[str] = None
    treatment_recommended: Optional[str] = None


class ScanResponse(BaseModel):
    id: int
    field_id: int
    disease_detected: str
    confidence: float
    crop_type: str
    scan_date: datetime
    treatment_recommended: Optional[str]
    treatment_completed: bool
    treatment_outcome: Optional[str]
    
    class Config:
        from_attributes = True


class ScanHistoryResponse(BaseModel):
    scans: List[ScanResponse]
    total_count: int


# ============================================================================
# OFFLINE SYNC SCHEMAS (PHASE 1)
# ============================================================================

class OfflineScanBatch(BaseModel):
    """Batch of scans saved offline, ready to sync"""
    scans: List[ScanCreateRequest]
    farmer_id: int
    device_id: str
    sync_timestamp: datetime


class SyncResponse(BaseModel):
    synced_count: int
    failed_count: int
    messages: List[str]


# ============================================================================
# PREDICTION SCHEMAS (FROM EXISTING API)
# ============================================================================

class PredictionResponse(BaseModel):
    disease: str
    confidence: float
    treatment: str
    crop_type: Optional[str] = None


# ============================================================================
# ANALYTICS SCHEMAS (PHASE 2)
# ============================================================================

class RegionalAnalyticsRequest(BaseModel):
    region_id: Optional[int] = None
    year: int
    month: int


class DiseasePrevalenceData(BaseModel):
    disease_type: str
    crop_type: str
    prevalence_percentage: float
    total_scans: int
    farmers_affected: int


class RegionalAnalyticsResponse(BaseModel):
    region_name: str
    period: str  # "January 2026"
    diseases: List[DiseasePrevalenceData]
    top_crop_scanned: str
    most_common_disease: str


# ============================================================================
# AEO DASHBOARD SCHEMAS (PHASE 3)
# ============================================================================

class RegionStatusData(BaseModel):
    region_id: int
    region_name: str
    status: str  # "Green", "Yellow", "Red"
    risk_level: float  # 0-100
    total_scans_this_month: int
    most_common_disease: str
    farmers_affected: int


class DashboardOverviewResponse(BaseModel):
    regions: List[RegionStatusData]
    top_3_diseases: List[str]
    top_3_crops: List[str]
    advice_compliance_percentage: float


class BroadcastCreateRequest(BaseModel):
    region_id: int
    message: str
    message_type: str = "Info"  # "Alert", "Advice", "Info"
    expires_hours: Optional[int] = None


class BroadcastResponse(BaseModel):
    id: int
    message: str
    message_type: str
    created_at: datetime
    expires_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============================================================================
# ERROR SCHEMAS
# ============================================================================

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
