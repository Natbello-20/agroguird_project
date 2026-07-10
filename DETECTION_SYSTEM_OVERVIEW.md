# AgroGuard Disease Detection System - Complete Overview

## 🎯 Detection Flow

### 1. **Image Upload**
```
User uploads image → Backend receives file → Validation checks
```

**Validation Checks:**
- ✅ File type must be image (JPEG, PNG, etc.)
- ✅ File size must be ≤ 5MB
- ✅ Image must be decodable

**Error Messages:**
- "Invalid File" - Wrong file type
- "File Too Large" - Image > 5MB
- "Invalid Image" - Corrupted or unreadable image

---

### 2. **AI Model Prediction**

The system uses a **TensorFlow Lite model** trained specifically on maize/corn leaf diseases.

**Model Details:**
- **File:** `mobile_assets/maize_model.tflite`
- **Input:** 224x224 RGB image
- **Output:** 4 disease classes
- **Classes:**
  1. `Corn___Healthy`
  2. `Corn___Common_Rust`
  3. `Corn___Northern_Leaf_Blight`
  4. `Corn___Gray_Leaf_Spot`

---

### 3. **Multi-Criteria Non-Maize Detection** ✨

The system uses **THREE validation criteria** to detect non-maize leaves:

#### **Criterion 1: Low Confidence**
```python
CONFIDENCE_THRESHOLD = 0.7  # 70%
```
- If model confidence < 70% → **Likely non-maize**
- Example: Image gets 45% confidence → REJECTED

#### **Criterion 2: High Entropy (Uncertainty)**
```python
ENTROPY_THRESHOLD = 1.0
```
- **Entropy** measures model uncertainty
- High entropy = Model is confused = Not a clear maize leaf
- Formula: `-Σ(p * log(p))` where p = probability for each class
- Example: All 4 classes get ~25% each → High entropy → REJECTED

#### **Criterion 3: Low Confidence Gap**
```python
GAP_THRESHOLD = 0.5  # 50%
```
- **Gap** = Difference between top 2 predictions
- Low gap = No clear winner = Uncertain prediction
- Example: 
  - Class 1: 40%
  - Class 2: 38%
  - Gap: 2% → Too low → REJECTED

---

### 4. **Detection Logic**

```python
is_likely_non_maize = (
    confidence < 0.7 OR
    entropy > 1.0 OR
    confidence_gap < 0.5
)

if is_likely_non_maize:
    return "No maize leaf detected. Please capture a maize leaf image for disease analysis."
```

**Any ONE failing criterion triggers rejection!**

---

### 5. **Response Messages**

#### ✅ **Successful Maize Detection**
```json
{
  "disease": "Corn Common Rust",
  "confidence": 0.92,
  "treatment": "Apply fungicide...",
  "recommendations": ["Remove infected leaves", "Improve air circulation"]
}
```

#### ❌ **Non-Maize Leaf Detected**
```json
{
  "error": "No maize leaf detected. Please capture a maize leaf image for disease analysis.",
  "disease": "Not Maize Leaf",
  "confidence": 0.45
}
```

**Error Modal Displays:**
- Error message in popup dialog
- User must dismiss and retake photo

---

## 📊 Detection Examples

### Example 1: Clear Maize Leaf with Disease
```
Input: Photo of maize leaf with rust spots
Model Output:
  - Corn___Common_Rust: 92%
  - Corn___Healthy: 5%
  - Corn___Northern_Leaf_Blight: 2%
  - Corn___Gray_Leaf_Spot: 1%

Validation:
  ✅ Confidence: 0.92 > 0.7
  ✅ Entropy: 0.35 < 1.0 (low uncertainty)
  ✅ Gap: 0.87 > 0.5 (clear winner)

Result: ✅ ACCEPTED - "Corn Common Rust (92% confidence)"
```

### Example 2: Tomato Leaf (Non-Maize)
```
Input: Photo of tomato leaf
Model Output:
  - Corn___Healthy: 35%
  - Corn___Common_Rust: 32%
  - Corn___Northern_Leaf_Blight: 20%
  - Corn___Gray_Leaf_Spot: 13%

Validation:
  ❌ Confidence: 0.35 < 0.7 (FAIL)
  ❌ Entropy: 1.25 > 1.0 (high uncertainty - FAIL)
  ❌ Gap: 0.03 < 0.5 (no clear winner - FAIL)

Result: ❌ REJECTED - "No maize leaf detected. Please capture a maize leaf image for disease analysis."
```

### Example 3: Blurry Maize Image
```
Input: Out-of-focus maize leaf photo
Model Output:
  - Corn___Healthy: 55%
  - Corn___Common_Rust: 30%
  - Corn___Northern_Leaf_Blight: 10%
  - Corn___Gray_Leaf_Spot: 5%

Validation:
  ❌ Confidence: 0.55 < 0.7 (FAIL)
  ✅ Entropy: 0.92 < 1.0 
  ❌ Gap: 0.25 < 0.5 (FAIL)

Result: ❌ REJECTED - "No maize leaf detected. Please capture a maize leaf image for disease analysis."
```

### Example 4: Healthy Maize Leaf
```
Input: Clear photo of healthy maize leaf
Model Output:
  - Corn___Healthy: 96%
  - Corn___Common_Rust: 2%
  - Corn___Northern_Leaf_Blight: 1%
  - Corn___Gray_Leaf_Spot: 1%

Validation:
  ✅ Confidence: 0.96 > 0.7
  ✅ Entropy: 0.18 < 1.0 (very certain)
  ✅ Gap: 0.94 > 0.5 (huge gap)

Result: ✅ ACCEPTED - "Corn Healthy (96% confidence)"
```

---

## 🔍 Why Multi-Criteria?

**Single Criterion Problems:**

1. **Confidence alone:**
   - Model might be 80% confident on a tomato leaf (if trained poorly)
   - ❌ Would incorrectly accept non-maize

2. **Entropy alone:**
   - Low quality maize leaf might have low entropy but wrong prediction
   - ❌ Would incorrectly reject real maize

3. **Gap alone:**
   - Model might confidently predict wrong class with large gap
   - ❌ Would incorrectly accept non-maize

**Multi-Criteria Solution:**
- ✅ All three metrics must pass
- ✅ Catches edge cases
- ✅ More robust detection

---

## 🎨 User Experience Flow

### Success Flow:
```
1. User takes photo of maize leaf
2. Image uploads → Processing (3-5 seconds)
3. ✅ Disease detected → Show result card
   - Disease name
   - Confidence percentage
   - Treatment recommendations
   - Management tips
4. Save to scan history
5. User can view history anytime
```

### Rejection Flow:
```
1. User takes photo of non-maize leaf (or blurry maize)
2. Image uploads → Processing (3-5 seconds)
3. ❌ Detection fails → Show error modal
   Message: "No maize leaf detected. Please capture a maize leaf image for disease analysis."
4. User dismisses modal
5. Camera resets → User can retake photo
```

---

## 📱 Frontend Display

### Error Modal (Non-Maize):
```html
<dialog>
  <h3>Error</h3>
  <p>No maize leaf detected. Please capture a maize leaf image for disease analysis.</p>
  <button>Close</button>
</dialog>
```

### Success Card (Maize Detected):
```html
<div class="scan-result-card">
  <h6>Detected Issue</h6>
  <h3>Corn Common Rust</h3>
  <span class="badge">92%</span>
  
  <h6>RECOMMENDED TREATMENT</h6>
  <p>Apply fungicide spray containing mancozeb...</p>
  
  <button>Done</button>
</div>
```

---

## 🧪 Testing the System

### Test Case 1: Real Maize Leaf
```bash
curl -X POST http://localhost:8000/predict \
  -H "device-id: test_device_001" \
  -F "file=@maize_leaf.jpg" \
  -F "lang=en"

Expected: 200 OK with disease prediction
```

### Test Case 2: Non-Maize Image
```bash
curl -X POST http://localhost:8000/predict \
  -H "device-id: test_device_001" \
  -F "file=@tomato_leaf.jpg" \
  -F "lang=en"

Expected: 400 Bad Request
{
  "error": "No maize leaf detected. Please capture a maize leaf image for disease analysis.",
  "disease": "Not Maize Leaf",
  "confidence": 0.45
}
```

### Test Case 3: Invalid File
```bash
curl -X POST http://localhost:8000/predict \
  -H "device-id: test_device_001" \
  -F "file=@document.pdf"

Expected: 400 Bad Request
{
  "error": "Invalid file type. Please upload an image.",
  "disease": "Invalid File",
  "confidence": 0
}
```

---

## 🛠️ Model Configuration

### Environment Variables:
```env
USE_REAL_MODEL=true
MODEL_PATH=mobile_assets/maize_model.tflite
```

### Model Loading:
```python
# Real model (production)
model = DiseaseDetectionModel(use_mock=False)

# Mock model (testing)
model = DiseaseDetectionModel(use_mock=True)
```

### Mock Model Behavior:
- 80% chance: Returns high confidence (0.75-0.98)
- 20% chance: Returns low confidence (0.3-0.5) to simulate non-maize

---

## 🔧 Adjusting Detection Sensitivity

### Make Detection More Strict (fewer false positives):
```python
CONFIDENCE_THRESHOLD = 0.85  # Increase from 0.7
ENTROPY_THRESHOLD = 0.8      # Decrease from 1.0
GAP_THRESHOLD = 0.6          # Increase from 0.5
```

### Make Detection More Lenient (fewer false negatives):
```python
CONFIDENCE_THRESHOLD = 0.6   # Decrease from 0.7
ENTROPY_THRESHOLD = 1.2      # Increase from 1.0
GAP_THRESHOLD = 0.4          # Decrease from 0.5
```

**Current Settings (Balanced):**
- CONFIDENCE_THRESHOLD = 0.7
- ENTROPY_THRESHOLD = 1.0
- GAP_THRESHOLD = 0.5

---

## 📈 Performance Metrics

### Expected Accuracy:
- **True Positives (Correct maize detection):** ~95%
- **True Negatives (Correct non-maize rejection):** ~90%
- **False Positives (Non-maize accepted as maize):** ~5%
- **False Negatives (Maize rejected as non-maize):** ~10%

### Common False Negatives:
- Very blurry maize images
- Maize leaves at extreme angles
- Poor lighting conditions
- Heavily diseased leaves (unrecognizable)

**Solution:** User can retake photo with better quality

---

## 🎯 Summary

**Detection System Goals:**
1. ✅ Accept clear maize leaf images
2. ✅ Reject non-maize leaves
3. ✅ Reject poor quality images
4. ✅ Provide clear feedback to users
5. ✅ Enable users to retake photos

**Key Features:**
- Multi-criteria validation (3 checks)
- User-friendly error messages
- Clear disease + confidence display
- Treatment recommendations
- Scan history tracking

**User Message for Non-Maize:**
> "No maize leaf detected. Please capture a maize leaf image for disease analysis."

This replaces the previous "Unknown" label with a clear, actionable message!

---

**Last Updated:** January 2026  
**Version:** 1.0.0  
**Model:** TensorFlow Lite (Maize Disease Detection)
