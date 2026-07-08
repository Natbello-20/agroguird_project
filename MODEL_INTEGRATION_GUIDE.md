# Model & Recommendation Integration Guide

## ✅ What Was Integrated

The AgroGuard system now supports **real TensorFlow Lite model integration** for maize disease detection with comprehensive multilingual recommendations.

---

## 📦 Integrated Components

### 1. **TFLite Model Support** (`model.py`)
- ✅ TensorFlow Lite model loader
- ✅ Support for `mobile_assets/maize_model.tflite`
- ✅ Lazy loading of TensorFlow (only loads when needed)
- ✅ Mock model fallback for testing

### 2. **Disease Classes** (4 Maize Diseases)
```python
0: "Corn___Healthy"
1: "Corn___Common_Rust"
2: "Corn___Northern_Leaf_Blight"
3: "Corn___Gray_Leaf_Spot"
```

### 3. **Disease Information** (`mobile_assets/disease_info.json`)
Each disease includes:
- Name (English)
- Scientific name
- Description
- Symptoms list
- Management recommendations
- Prevention tips

### 4. **Multilingual Treatments** (`treatment.json`)
Treatments in 3 languages:
- **English** (`en`)
- **Twi** (`tw`)
- **Fante** (`ff`)

New maize diseases added:
- `Corn___Healthy`
- `Corn___Common_Rust`
- `Corn___Northern_Leaf_Blight`
- `Corn___Gray_Leaf_Spot`

---

## 🎯 API Response Format

### `/predict` Endpoint Enhanced Response

```json
{
  "disease": "Common Rust",
  "disease_class": "Corn Common_Rust",
  "confidence": 0.92,
  "treatment": "Apply fungicides like Propiconazole or Azoxystrobin when pustules first appear...",
  "status": "High Risk",
  "recommendations": [
    "Apply fungicide when symptoms first appear",
    "Plant resistant corn hybrids",
    "Reduce plant density for better air circulation"
  ],
  "prevention": [
    "Use resistant varieties",
    "Practice crop rotation",
    "Monitor fields regularly"
  ],
  "disease_info": {
    "name": "Common Rust",
    "description": "Fungal disease causing rust-colored pustules on leaves",
    "symptoms": [
      "Small circular to elongate rust-colored pustules",
      "Pustules on both sides of leaves",
      "Leaves may turn yellow and die prematurely"
    ],
    "scientific_name": "Puccinia sorghi"
  }
}
```

---

## 🚀 How to Use

### **Option 1: Mock Mode (Default - Fast)**
No TensorFlow required, uses random predictions from maize disease classes.

```bash
# Start server with mock model (default)
python -m uvicorn main:app --reload
```

### **Option 2: Real TFLite Model**
Requires TensorFlow installed.

```bash
# Set environment variable
# On Windows:
set USE_REAL_MODEL=true

# On Linux/Mac:
export USE_REAL_MODEL=true

# Start server
python -m uvicorn main:app --reload
```

Or add to `.env` file:
```env
USE_REAL_MODEL=true
```

---

## 📁 File Structure

```
agroguird_project/
├── mobile_assets/
│   ├── maize_model.tflite      # TensorFlow Lite model (224x224 input)
│   ├── labels.txt              # Disease class labels
│   └── disease_info.json       # Detailed disease information
├── model.py                     # Disease detection model class
├── main.py                      # FastAPI app with /predict endpoint
├── treatment.json               # Multilingual treatment recommendations
└── MODEL_INTEGRATION_GUIDE.md  # This file
```

---

## 🔧 Model Details

### Input Specifications
- **Format:** TensorFlow Lite (.tflite)
- **Input Shape:** `(1, 224, 224, 3)` - RGB image
- **Input Type:** `float32`
- **Normalization:** Pixels scaled to [0, 1]

### Output Specifications
- **Output Shape:** `(1, 4)` - 4 disease classes
- **Output Type:** `float32` (probabilities/logits)
- **Classes:** 4 maize diseases

### Preprocessing Pipeline
1. Convert image bytes → OpenCV image (BGR)
2. Resize to 224x224
3. Normalize to float32 [0, 1]
4. Add batch dimension → (1, 224, 224, 3)
5. Run TFLite interpreter

---

## 🧪 Testing

### Test Mock Model
```bash
python test_model.py
```

Expected output:
```
============================================================
Testing Model Integration
============================================================
1. Testing mock model initialization...
   ✓ Model initialized (mock=True)
   ✓ Labels loaded: 4 classes
   ✓ Disease info loaded: 4 conditions

2. Testing mock prediction...
   ✓ Prediction: Corn___Healthy
   ✓ Confidence: 0.8
   ✓ Is maize: True

3. Testing disease info retrieval...
   ✓ Disease name: Healthy Maize Leaf
   ✓ Symptoms count: 3
   ✓ Management steps: 3

4. Testing all disease classes...
   0: Corn___Healthy
   1: Corn___Common_Rust
   2: Corn___Northern_Leaf_Blight
   3: Corn___Gray_Leaf_Spot
```

### Test API Endpoint
```bash
# Using curl (with a maize leaf image)
curl -X POST "http://localhost:8000/predict?lang=en" \
  -H "device-id: test-device" \
  -H "x-latitude: 6.6885" \
  -H "x-longitude: -1.6244" \
  -F "file=@maize_leaf.jpg"
```

---

## 🌍 Multilingual Support

### Request with Language Parameter
```bash
# English (default)
curl -X POST "http://localhost:8000/predict?lang=en" ...

# Twi
curl -X POST "http://localhost:8000/predict?lang=tw" ...

# Fante
curl -X POST "http://localhost:8000/predict?lang=ff" ...
```

### Response Changes by Language
```json
// English (lang=en)
{
  "disease": "Common Rust",
  "treatment": "Apply fungicides like Propiconazole..."
}

// Twi (lang=tw)
{
  "disease": "Ɔkukɔ Ntini Rust",
  "treatment": "Hyɛ fungicide a wɔfrɛ no Propiconazole..."
}
```

---

## 🛠️ Extending the System

### Add New Disease Classes
1. **Update `model.py`:**
   ```python
   MAIZE_CLASSES = {
       0: "Corn___Healthy",
       1: "Corn___Common_Rust",
       2: "Corn___Northern_Leaf_Blight",
       3: "Corn___Gray_Leaf_Spot",
       4: "Corn___New_Disease",  # Add here
   }
   ```

2. **Update `mobile_assets/disease_info.json`:**
   ```json
   {
     "new_disease": {
       "name": "New Disease",
       "scientific_name": "Scientific Name",
       "description": "...",
       "symptoms": [...],
       "management": [...],
       "prevention": [...]
     }
   }
   ```

3. **Update `treatment.json`:**
   ```json
   {
     "Corn___New_Disease": {
       "en": {"title": "...", "treatment": "..."},
       "tw": {"title": "...", "treatment": "..."},
       "ff": {"title": "...", "treatment": "..."}
     }
   }
   ```

### Replace the Model
1. Place new `.tflite` file in `mobile_assets/maize_model.tflite`
2. Update input size if different (default: 224x224)
3. Update disease classes in `model.py`
4. Restart server

---

## 📊 Model Performance Tips

### Improve Accuracy
- Use high-quality images (well-lit, focused)
- Capture close-up shots of affected areas
- Ensure proper framing (leaf fills frame)
- Avoid blurry or dark images

### Optimize Speed
- Use mock mode for development/testing
- Enable real model only in production
- Consider quantized models for faster inference
- Cache model in memory (already done)

---

## 🔒 Validation & Safety

### Image Validation
✅ File type check (must be image/*)
✅ File size limit (max 5MB)
✅ Image decode validation
✅ Maize leaf verification (rejects non-maize)

### Scan Limits
✅ 5-scan limit per GPS segment (5-yard radius)
✅ Device ID tracking
✅ Location-based segmentation

---

## 📝 Task Completion

- ✅ Load trained model files
- ✅ Integrate disease detection with TFLite
- ✅ Load recommendation data
- ✅ Provide actionable treatment suggestions
- ✅ Multilingual support (EN/TW/FF)
- ✅ Detailed disease information
- ✅ Management and prevention tips
- ✅ Scientific names and symptoms

---

## 🎓 Credits

**Model:** Custom TensorFlow Lite maize disease classifier
**Diseases:** 4 maize conditions (Healthy + 3 diseases)
**Languages:** English, Twi, Fante
**Framework:** FastAPI + TensorFlow Lite + OpenCV

---

**Built with AgroGuard** 🌱 | Protecting Ghanaian maize crops through AI
