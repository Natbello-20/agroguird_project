# AgroGuard Deployment Guide

## ✅ Deployment Issue Fixed

### **Problem**
```
ImportError: email-validator is not installed
```

### **Root Cause**
The `schemas.py` file uses `EmailStr` from Pydantic, which requires the `email-validator` package. This dependency was missing from `requirements.txt`.

### **Solution**
Added missing dependencies to `requirements.txt`:
- ✅ `email-validator==2.1.0` - Required by Pydantic EmailStr
- ✅ `opencv-python-headless==4.8.1.78` - Required for image processing (headless version for servers)
- ✅ `numpy==1.26.2` - Required by OpenCV and TensorFlow

---

## 📦 Complete Requirements

```txt
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
jinja2==3.1.2
python-dotenv==1.0.0
httpx==0.27.0
passlib[bcrypt]==1.7.4
bcrypt==3.2.0
pyjwt==2.8.0
email-validator==2.1.0        # NEW - Required by Pydantic EmailStr
opencv-python-headless==4.8.1.78  # NEW - Image processing (server-friendly)
numpy==1.26.2                 # NEW - Required by OpenCV and model
```

---

## 🚀 Deployment Steps

### **1. Commit and Push Changes**
```bash
git add requirements.txt
git commit -m "Add missing dependencies for deployment"
git push origin main
```

### **2. Render Will Auto-Deploy**
Render should automatically detect the changes and redeploy. If not, manually trigger a deploy from the Render dashboard.

### **3. Set Environment Variables**
In Render dashboard, set these environment variables:

```env
# Required
JWT_SECRET_KEY=your-super-secure-random-key-here
WEATHER_API_KEY=your-openweathermap-api-key

# Optional
USE_REAL_MODEL=false          # Set to true to use TFLite model
DEBUG=false
HOST=0.0.0.0
PORT=10000
JWT_EXPIRATION_HOURS=24
```

---

## 🌍 Environment Variables Explained

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JWT_SECRET_KEY` | ✅ Yes | `change-me-in-production` | Secret key for JWT token signing |
| `WEATHER_API_KEY` | ⚠️ Recommended | - | OpenWeatherMap API key for weather data |
| `USE_REAL_MODEL` | ❌ No | `false` | Enable TFLite model (requires TensorFlow) |
| `DEBUG` | ❌ No | `false` | Enable debug mode |
| `HOST` | ❌ No | `0.0.0.0` | Server host |
| `PORT` | ❌ No | `10000` | Server port (Render uses 10000) |
| `JWT_EXPIRATION_HOURS` | ❌ No | `24` | JWT token expiration time |

---

## 🔐 Security Notes for Production

### **1. Generate Strong JWT Secret**
```bash
# On Linux/Mac
openssl rand -hex 32

# On Windows PowerShell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))
```

### **2. Change Default Credentials**
After first deployment, immediately change:
- ✅ Super Admin: `superadmin` / `SuperAdmin@123`
- ✅ Officer: `admin` / `admin123`

### **3. Use HTTPS**
Render provides free SSL certificates. Ensure your app is accessed via `https://`

---

## 🧪 Testing Deployment

### **1. Check Health**
```bash
curl https://your-app.onrender.com/
```

### **2. Test Prediction Endpoint**
```bash
curl -X POST "https://your-app.onrender.com/predict?lang=en" \
  -H "device-id: test-device" \
  -H "x-latitude: 6.6885" \
  -H "x-longitude: -1.6244" \
  -F "file=@maize_leaf.jpg"
```

### **3. Test Super Admin Login**
```bash
curl -X POST "https://your-app.onrender.com/superadmin/login" \
  -d "username=superadmin&password=SuperAdmin@123"
```

---

## 📊 Model Deployment Options

### **Option 1: Mock Model (Default - Recommended for Free Tier)**
- ✅ No TensorFlow required
- ✅ Fast startup (<30 seconds)
- ✅ Works on Render free tier
- ✅ Uses random predictions from real disease classes

**Environment:**
```env
USE_REAL_MODEL=false
```

### **Option 2: Real TFLite Model**
- ⚠️ Requires TensorFlow (large dependency ~500MB)
- ⚠️ Slow startup (2-3 minutes)
- ⚠️ May exceed free tier limits
- ✅ Real disease predictions

**To enable:**
1. Add to `requirements.txt`:
   ```txt
   tensorflow==2.15.0
   ```

2. Set environment variable:
   ```env
   USE_REAL_MODEL=true
   ```

3. Upgrade Render plan (free tier may be too small)

---

## 🐛 Common Deployment Issues

### **Issue 1: Build Timeout**
**Symptom:** Build fails after 15 minutes

**Solution:**
- Ensure you're using `opencv-python-headless` (not `opencv-python`)
- Keep `USE_REAL_MODEL=false` for free tier
- Don't add TensorFlow to requirements unless needed

### **Issue 2: Memory Limit Exceeded**
**Symptom:** App crashes with "Out of Memory"

**Solution:**
- Upgrade to paid Render plan
- Or keep using mock model (no TensorFlow)

### **Issue 3: Database Not Found**
**Symptom:** `agroguard.db` not found

**Solution:**
- Database is created automatically on first run
- Check Render logs to ensure startup completed
- Consider using PostgreSQL for persistent storage

### **Issue 4: Static Files Not Loading**
**Symptom:** 404 errors for `/static/` URLs

**Solution:**
- Ensure `static/` directory exists in repo
- Check `main.py` has: `app.mount("/static", StaticFiles(directory="static"), name="static")`

---

## 📝 Post-Deployment Checklist

- [ ] App is accessible via HTTPS
- [ ] Prediction endpoint works
- [ ] Super admin login works
- [ ] Officer login works
- [ ] Changed default passwords
- [ ] Set strong JWT secret key
- [ ] Weather API key configured (optional)
- [ ] Database initialized with tables
- [ ] Static files loading correctly

---

## 🔗 Useful Commands

### Check Logs
```bash
# Via Render dashboard: Logs tab
# Or use Render CLI
render logs --app your-app-name --tail
```

### Force Redeploy
```bash
# Via Render dashboard: Manual Deploy button
# Or commit empty change
git commit --allow-empty -m "Force redeploy"
git push origin main
```

### SSH into Container (Paid Plans Only)
```bash
render ssh --app your-app-name
```

---

## 🎓 Database Notes

### **Current: SQLite (File-Based)**
- ✅ Simple, no setup required
- ⚠️ Ephemeral on Render (resets on deploy)
- ⚠️ Not suitable for production

### **Recommended: PostgreSQL**
For production, migrate to PostgreSQL:

1. Add to `requirements.txt`:
   ```txt
   psycopg2-binary==2.9.9
   sqlalchemy==2.0.23
   ```

2. Update `database.py` to use SQLAlchemy with PostgreSQL

3. Set `DATABASE_URL` in Render environment variables

---

## 📞 Support

**Render Documentation:** https://render.com/docs
**AgroGuard Issues:** Check project logs and error messages
**Email Validator:** https://github.com/JoshData/python-email-validator

---

**Your app should now deploy successfully!** 🚀🎉

Once deployed, access your app at: `https://your-app-name.onrender.com`
