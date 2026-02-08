# Google Translate Setup Guide

## Overview
AgroGuard now uses **Google Translate API (Free Tier)** for multilingual support instead of Ghana NLP API.

**Free Tier Benefits:**
- ✅ 500,000 characters/month for free
- ✅ Unlimited languages (Twi, Fante, etc.)
- ✅ No payment needed
- ✅ Automatic fallback if translation fails

---

## Setup Steps

### Step 1: Create Google Cloud Project

1. Go to **[Google Cloud Console](https://console.cloud.google.com/)**
2. Click **Create Project**
3. Name it: `agroguard` (or your preferred name)
4. Click **Create**

### Step 2: Enable Cloud Translation API

1. In the Cloud Console, go to **APIs & Services** → **Library**
2. Search for **"Cloud Translation API"**
3. Click on **Cloud Translation API**
4. Click **ENABLE**

### Step 3: Create Service Account

1. Go to **APIs & Services** → **Credentials**
2. Click **+ Create Credentials** → **Service Account**
3. Fill in:
   - Service account name: `agroguard-translator`
   - Service account ID: (auto-filled)
4. Click **Create and Continue**
5. Skip optional steps, click **Done**

### Step 4: Generate and Download Key

1. In **Service Accounts**, click the service account you just created
2. Go to **Keys** tab
3. Click **Add Key** → **Create new key**
4. Select **JSON**
5. Click **Create**
6. A JSON file will download automatically

**Important:** Save this file safely!

### Step 5: Set Environment Variable

#### **Option A: Windows (Recommended)**

Place the JSON file in your project folder, then add to `.env`:

```
GOOGLE_APPLICATION_CREDENTIALS=service-account-key.json
```

#### **Option B: Windows PowerShell**

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\Users\YourUsername\Desktop\agroguird_project\service-account-key.json"
```

#### **Option C: System Environment Variable (Permanent)**

1. Press `Win + X` → **System**
2. Click **Advanced system settings**
3. Click **Environment Variables**
4. Under **User variables**, click **New**
5. Variable name: `GOOGLE_APPLICATION_CREDENTIALS`
6. Variable value: Full path to JSON file
7. Click **OK** and restart your terminal

---

## How to Test

### 1. Start the application:

```bash
python main.py
```

You should see:
```
✓ Google Translate API initialized successfully
```

### 2. Test translation endpoint:

Open your browser and visit:

```
http://localhost:8000/translate?text=Hello&source_lang=en&target_lang=tw
```

Expected response:
```json
{
  "translated": "[Twi translation of Hello]",
  "source_lang": "en",
  "target_lang": "tw"
}
```

### 3. Test the app:

1. Go to `http://localhost:8000`
2. Upload an image
3. Select **Twi** or **Fante** language
4. Click **Analyze Image**
5. Treatment should appear in selected language

---

## Supported Languages

| Code | Language |
|------|----------|
| `en` | English |
| `tw` | Twi (Akan) |
| `ff` | Fante (Mfantse) |

Add more languages by updating `LANGUAGE_CODES` in `main.py`.

---

## Troubleshooting

### Issue: "Translation service not configured"

**Solution:** 
- Check `GOOGLE_APPLICATION_CREDENTIALS` is set correctly
- Verify JSON file path exists
- Restart Python application

### Issue: Translation fails with error

**Solution:**
- Check Google Cloud Console for billing issues
- Verify API is enabled in console
- Check service account has `Translate Admin` role

### Issue: Free tier limit exceeded

**Solution:**
- Create a new project (gets fresh quota)
- Or enable billing (still very cheap: ~$15/million characters)

---

## Cost Estimation

| Monthly Characters | Cost |
|--------------------|------|
| 0 - 500,000 | **FREE** |
| 500,001 - 1M | ~$7.50 |
| 1M - 10M | ~$75 |

**Best practice:** Monitor usage in Cloud Console → Billing

---

## What Changed from Ghana NLP

| Feature | Ghana NLP | Google Translate |
|---------|-----------|------------------|
| Cost | Payable (varies) | **Free up to 500k chars** |
| API Key | Required | **Automatic (JSON file)** |
| Setup | 1 step | **5 steps (one-time)** |
| Languages | Limited | **100+ languages** |
| Reliability | Depends | **Google's infrastructure** |

---

## Files Modified

- ✅ `main.py` - Updated to use Google Translate API
- ✅ `requirements.txt` - Added google-cloud-translate package
- ✅ `.env` - Updated configuration instructions

---

## Support

If you encounter issues:
1. Check [Google Cloud Documentation](https://cloud.google.com/translate/docs)
2. Review error messages in terminal output
3. Verify service account permissions in Cloud Console

