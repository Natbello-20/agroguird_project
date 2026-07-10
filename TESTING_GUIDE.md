# AgroGuard Testing Guide

## Server Status
✅ Server is running at: **http://localhost:8000**

## What to Test

### 1. Test with MAIZE Leaf Images
**Expected behavior:**
- ✅ Should show disease name (e.g., "Common Rust", "Gray Leaf Spot", "Healthy Corn")
- ✅ Should show confidence percentage (e.g., 94%, 75%)
- ✅ Should show treatment recommendations
- ✅ Should show disease information

**How to test:**
1. Open http://localhost:8000 in your browser
2. Upload a maize/corn leaf image
3. Check the results displayed

### 2. Test with NON-MAIZE Images
**Expected behavior:**
- ❌ Should show error message: "Non-maize leaf detected. Please upload a maize leaf image."
- ❌ Should NOT show treatment recommendations
- ❌ Should reject: flowers, people, animals, buildings, other plants

**How to test:**
1. Upload a flower image
2. Upload a picture of a person
3. Upload any non-maize object
4. All should be rejected with error message

### 3. Check Server Logs
**What to look for:**
```
[DEBUG] Predicted: Corn___Common_Rust with confidence: 0.9948
[DEBUG] Entropy: 0.0335 (lower = more certain)
[DEBUG] Confidence gap: 0.9900 (higher = more decisive)
[SUCCESS] Returning response: disease='Common Rust', confidence=0.99
```

## Current System Configuration

### Multi-Criteria Detection
The system now uses THREE checks to reject non-maize images:

1. **Confidence Threshold**: Must be ≥ 0.7 (70%)
2. **Entropy Check**: Must be ≤ 1.0 (lower = more certain)
3. **Confidence Gap**: Must be ≥ 0.5 (difference between top 2 predictions)

### Real Model Active
- ✅ Using trained TFLite model: `mobile_assets/maize_model.tflite`
- ✅ Environment: `USE_REAL_MODEL=true`
- ✅ Image processing: PIL/Pillow (no OpenCV)

## Viewing Server Logs

### In Browser Console (F12)
1. Press **F12** to open Developer Tools
2. Go to **Console** tab
3. Look for any JavaScript errors

### In Terminal (Server Logs)
The terminal running the server shows:
- Each prediction request
- Disease detected
- Confidence scores
- Entropy and gap values
- Success or error messages

## Common Issues to Check

### Issue: Everything shows "Unknown"
**Possible causes:**
1. Frontend not parsing JSON response correctly
2. Treatment data not loading from `treatment.json`
3. JavaScript error in browser console

**How to debug:**
1. Press F12 and check Console tab for errors
2. Check Network tab to see actual API response
3. Look at server logs to see what's being returned

### Issue: Non-maize images accepted
**Possible causes:**
1. Thresholds too lenient
2. Model giving high confidence to non-maize

**How to debug:**
1. Check server logs for confidence, entropy, and gap values
2. If all three criteria pass, the model is too confident
3. May need to retrain model with "Not Maize" class

### Issue: Maize images rejected
**Possible causes:**
1. Thresholds too strict
2. Poor quality image

**How to debug:**
1. Check confidence, entropy, and gap in logs
2. Try with better quality image
3. May need to adjust thresholds

## Testing Checklist

- [ ] Server starts without errors
- [ ] Homepage loads at http://localhost:8000
- [ ] Upload maize leaf → Shows disease name and treatment
- [ ] Upload flower → Shows "Non-maize leaf detected" error
- [ ] Upload person photo → Shows rejection error
- [ ] Check browser console for JavaScript errors
- [ ] Check server logs for prediction details
- [ ] Test with multiple maize images
- [ ] Test with multiple non-maize images

## Next Steps Based on Results

### If maize images work but UI shows "Unknown":
→ Frontend/JavaScript issue - check browser console

### If non-maize images still accepted:
→ Model confidence issue - may need model retraining with "Not Maize" class

### If everything works perfectly:
→ System is ready! ✅

## Quick Test Command

You can test the API directly with curl:
```bash
curl -X POST -F "file=@path/to/image.jpg" http://localhost:8000/predict?lang=en
```

This will show you the raw JSON response from the API.

## Current Status
- **Backend**: Working correctly (logs show predictions)
- **Frontend**: Need to verify (user reported "Unknown")
- **Model**: Loaded and predicting
- **Detection**: Multi-criteria rejection implemented

---

**Remember**: The disconnect seems to be between backend (working) and frontend (showing "Unknown"). Please check:
1. Browser console (F12 → Console tab)
2. Network tab (F12 → Network tab) to see actual API responses
3. Any JavaScript errors that might prevent proper display
