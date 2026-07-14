# Render Deployment Setup Guide

## 🚨 Critical Issue: Model Not Loading on Render

**Problem:** The app shows "This is not a maize leaf" for ALL images (even real maize) on Render.

**Root Cause:** The environment variable `USE_REAL_MODEL` is not set on Render, so the app falls back to mock mode.

---

## ✅ Solution: Set Environment Variables on Render

### Step 1: Go to Render Dashboard

1. Open https://dashboard.render.com/
2. Find your **agroguird_project** service
3. Click on the service name

### Step 2: Add Environment Variables

1. Go to **Environment** tab (left sidebar)
2. Click **Add Environment Variable**
3. Add the following variables:

#### Required Variables:

```
USE_REAL_MODEL=true
WEATHER_API_KEY=9cf91ca0033d2e1d1f8f7cbc89cd96e4
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
```

#### Optional (Recommended):

```
DEBUG=False
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///agroguard.db
```

### Step 3: Save and Redeploy

1. Click **Save Changes**
2. Render will automatically redeploy
3. Wait for deployment to complete (~5 minutes)

---

## 🧪 Testing After Deployment

1. Open your Render app URL
2. Take a photo of a **real maize leaf**
3. The app should now:
   - ✅ Detect the disease correctly
   - ✅ Show confidence score (e.g., 0.85)
   - ✅ Display treatment recommendations
   - ❌ NOT show "This is not a maize leaf" error

4. Take a photo of something that's NOT maize
5. The app should:
   - ✅ Show "This is not a maize leaf" error
   - ✅ Display the beautiful error modal
   - ❌ NOT save to history

---

## 📊 How to Verify Model is Loading

Check Render logs:

1. Go to **Logs** tab in Render dashboard
2. Look for these messages on startup:

✅ **Model Loading Successfully:**
```
[MODEL] TensorFlow Lite interpreter loaded successfully
[MODEL] Input shape: (1, 224, 224, 3)
[MODEL] Output shape: (1, 4)
[MODEL] Model loaded with 4 classes
```

❌ **Model NOT Loading (Mock Mode):**
```
[DEBUG] Using mock prediction
```

---

## 🔧 Troubleshooting

### Issue: Still showing "Not a maize leaf" for real maize

**Check:**
1. Is `USE_REAL_MODEL=true` set in Render environment variables?
2. Are the model files (mobile_assets/) in the repository?
3. Check Render logs for "Model loaded successfully"

**Solution:**
- Set `USE_REAL_MODEL=true` in Render dashboard
- Redeploy the service

### Issue: Model files not found

**Check:**
```bash
git ls-files mobile_assets/
```

**Should show:**
```
mobile_assets/disease_info.json
mobile_assets/labels.txt
mobile_assets/maize_model.tflite
```

**If missing:**
```bash
git add mobile_assets/
git commit -m "Add model files"
git push origin main
```

---

## 📋 Current Environment Variables

### Local (.env file):
```env
USE_REAL_MODEL=true
WEATHER_API_KEY=9cf91ca0033d2e1d1f8f7cbc89cd96e4
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
DEBUG=False
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///agroguard.db
```

### Render (Must set manually):
Go to Render Dashboard → Environment → Add the same variables above

---

## 🚀 Quick Fix Summary

1. **Go to Render Dashboard**
2. **Click your service → Environment tab**
3. **Add:** `USE_REAL_MODEL=true`
4. **Add:** `WEATHER_API_KEY=9cf91ca0033d2e1d1f8f7cbc89cd96e4`
5. **Add:** `JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production`
6. **Save Changes**
7. **Wait for auto-redeploy (~5 minutes)**
8. **Test with real maize leaf** ✅

---

## ✅ Expected Result After Fix

- ✅ Real maize leaves are detected correctly
- ✅ Shows disease name and confidence
- ✅ Displays treatment recommendations
- ✅ Non-maize objects are rejected with error modal
- ✅ Model logs show "Model loaded successfully"
