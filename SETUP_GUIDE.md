# AgroGuard - Local Setup Guide

This guide will help you set up and run the AgroGuard application on any machine locally.

---

## 📋 Prerequisites

Before you begin, make sure you have the following installed on your machine:

### Required Software:
1. **Python 3.9 or higher**
   - Check version: `python --version` or `python3 --version`
   - Download from: https://www.python.org/downloads/

2. **Git** (for cloning the repository)
   - Check version: `git --version`
   - Download from: https://git-scm.com/downloads

3. **pip** (Python package manager - usually comes with Python)
   - Check version: `pip --version`

### System Requirements:
- **RAM**: Minimum 4GB (8GB recommended for AI model)
- **Disk Space**: At least 2GB free space
- **Operating System**: Windows, macOS, or Linux

---

## 🚀 Step-by-Step Setup Instructions

### Step 1: Clone the Repository

Open your terminal/command prompt and run:

```bash
# Clone the repository
git clone https://github.com/Natbello-20/agroguird_project.git

# Navigate into the project directory
cd agroguird_project
```

**Alternative (if you have a ZIP file):**
- Extract the ZIP file to a folder
- Open terminal/command prompt in that folder

---

### Step 2: Create a Virtual Environment (Recommended)

Creating a virtual environment keeps your project dependencies isolated.

**Windows:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

**macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

You should see `(venv)` at the beginning of your terminal prompt when activated.

---

### Step 3: Install Dependencies

With your virtual environment activated, install all required packages:

```bash
# Upgrade pip first (recommended)
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

**Note:** This may take 5-10 minutes as it downloads and installs TensorFlow and other large packages.

**If you encounter errors:**
- Try: `pip install --no-cache-dir -r requirements.txt`
- Or install packages individually if one fails

---

### Step 4: Set Up Environment Variables

Create a `.env` file for configuration:

**Windows:**
```bash
copy .env.example .env
```

**macOS/Linux:**
```bash
cp .env.example .env
```

**Edit the `.env` file:**
Open `.env` in any text editor and add your configuration:

```env
# Ghana NLP Translation API Configuration
# Get your API key from https://www.ghananlp.org/
GHANA_NLP_API_KEY=your_api_key_here

# Optional: Database configuration
# DATABASE_URL=sqlite:///./agroguard.db

# Optional: JWT Secret (auto-generated if not provided)
# JWT_SECRET_KEY=your-secret-key-here
```

**Note:** The app will work without the Ghana NLP API key, but translation features may be limited.

---

### Step 5: Verify Project Structure

Make sure you have these important files and folders:

```
agroguird_project/
├── main.py                 ✅ Main application file
├── auth.py                 ✅ Authentication module
├── database.py             ✅ Database operations
├── model.py                ✅ AI model loader
├── requirements.txt        ✅ Dependencies list
├── .env                    ✅ Environment variables (you created this)
├── treatment.json          ✅ Treatment database
├── templates/              ✅ HTML templates folder
│   ├── index.html
│   ├── dashboard.html
│   ├── login.html
│   └── role_selection.html
├── static/                 ✅ Static assets folder
│   ├── sw.js
│   ├── manifest.json
│   └── images/
└── mobile_assets/          ✅ AI model folder
    ├── maize_model.tflite
    └── labels.txt
```

---

### Step 6: Initialize the Database

The database will be created automatically on first run, but you can initialize it manually:

```bash
# Run Python and execute database setup
python -c "from database import init_db; init_db()"
```

**Or** just proceed to the next step - the database will auto-create.

---

### Step 7: Run the Application

Start the development server:

```bash
# Run the application
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Explanation of flags:**
- `--reload` - Auto-restart server when code changes (useful for development)
- `--host 0.0.0.0` - Make server accessible from other devices on your network
- `--port 8000` - Run on port 8000

**You should see output like:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

### Step 8: Access the Application

Open your web browser and navigate to:

🌐 **Farmer App (Main Interface):**
- http://localhost:8000
- http://127.0.0.1:8000

👨‍🌾 **Extension Officer Dashboard:**
- http://localhost:8000/dashboard

🔐 **Officer Login:**
- http://localhost:8000/login

📱 **Role Selection (First Time Users):**
- http://localhost:8000/role-selection

---

## 🎯 Testing the Application

### Test as a Farmer:
1. Go to http://localhost:8000
2. Select "I am a Farmer" (Me yɛ Okuani)
3. Enter your name and phone number
4. Upload a maize leaf photo or use camera
5. View disease diagnosis and treatment

### Test as an Extension Officer:
1. First, create an AEO account:
   - Method 1: Use the super admin dashboard (if available)
   - Method 2: Register via API endpoint
   
2. Login at http://localhost:8000/login
3. Complete your profile
4. Access the dashboard to:
   - View scan statistics
   - Send alerts to farmers
   - Export data (CSV/Excel)
   - Monitor disease trends

---

## 🔧 Troubleshooting

### Issue: Port 8000 already in use
**Solution:**
```bash
# Use a different port
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```
Then access at http://localhost:8080

### Issue: Module not found errors
**Solution:**
```bash
# Make sure virtual environment is activated
# Then reinstall dependencies
pip install -r requirements.txt
```

### Issue: TensorFlow installation fails
**Solution:**
```bash
# Try installing TensorFlow separately
pip install tensorflow==2.18.0

# Or use CPU-only version (smaller, faster install)
pip install tensorflow-cpu==2.18.0
```

### Issue: AI model not loading
**Solution:**
- Check that `mobile_assets/maize_model.tflite` exists
- Check that `mobile_assets/labels.txt` exists
- Verify file permissions

### Issue: Database errors
**Solution:**
```bash
# Delete existing database and restart
# Windows:
del agroguard.db

# macOS/Linux:
rm agroguard.db

# Then restart the application
```

### Issue: Permission denied errors (Linux/macOS)
**Solution:**
```bash
# Add execution permissions
chmod +x main.py

# Or run with sudo (not recommended)
sudo uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📱 Accessing from Mobile Devices

To test on your phone or tablet:

1. Make sure your phone and computer are on the **same WiFi network**

2. Find your computer's local IP address:

   **Windows:**
   ```bash
   ipconfig
   # Look for "IPv4 Address" (e.g., 192.168.1.100)
   ```

   **macOS:**
   ```bash
   ifconfig | grep "inet "
   # Or check System Preferences > Network
   ```

   **Linux:**
   ```bash
   hostname -I
   # Or: ip addr show
   ```

3. On your phone's browser, go to:
   - `http://YOUR_IP_ADDRESS:8000`
   - Example: `http://192.168.1.100:8000`

4. Add to home screen for full PWA experience!

---

## 🛑 Stopping the Application

To stop the server:
- Press `CTRL + C` in the terminal

To deactivate the virtual environment:
```bash
deactivate
```

---

## 🔄 Updating the Application

To get the latest changes:

```bash
# Make sure you're in the project directory
cd agroguird_project

# Pull latest changes from GitHub
git pull origin main

# Activate virtual environment
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Update dependencies (if requirements.txt changed)
pip install -r requirements.txt --upgrade

# Restart the application
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📊 Database Management

### View Database Contents:
```bash
# Install SQLite browser (optional)
# Windows: Download from https://sqlitebrowser.org/
# macOS: brew install --cask db-browser-for-sqlite
# Linux: apt-get install sqlitebrowser

# Or use Python
python analyze_db.py
```

### Backup Database:
```bash
# Windows
copy agroguard.db agroguard_backup.db

# macOS/Linux
cp agroguard.db agroguard_backup.db
```

### Reset Database:
```bash
# Delete database file
# Windows: del agroguard.db
# macOS/Linux: rm agroguard.db

# Restart application (database will be recreated)
```

---

## 🌐 Production Deployment

For deploying to a production server:

### Option 1: Render.com (Recommended)
1. Push code to GitHub
2. Create new Web Service on Render
3. Connect your GitHub repository
4. Render auto-deploys on every push

### Option 2: Manual Server Deployment
```bash
# Install production server
pip install gunicorn

# Run with gunicorn (Linux/macOS)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# For Windows, continue using uvicorn without --reload
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 📝 Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GHANA_NLP_API_KEY` | Ghana NLP API key for translations | No | None |
| `DATABASE_URL` | Database connection string | No | `sqlite:///./agroguard.db` |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | No | Auto-generated |
| `ENVIRONMENT` | Environment mode (dev/prod) | No | `development` |

---

## 🧪 Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=.
```

---

## 💡 Tips for Development

1. **Use `--reload` flag** during development for auto-restart on code changes

2. **Check logs** in terminal for errors and debugging info

3. **Use browser DevTools** (F12) to debug frontend issues

4. **Test offline mode** by disconnecting internet after page loads

5. **Clear browser cache** if seeing old versions (Ctrl+Shift+R / Cmd+Shift+R)

6. **Use different browsers** to test compatibility

7. **Test on mobile** for best user experience validation

---

## 📞 Support

If you encounter issues:

1. Check the **Troubleshooting** section above
2. Review the main **README.md** file
3. Check GitHub Issues: https://github.com/Natbello-20/agroguird_project/issues
4. Contact the development team

---

## ✅ Quick Start Checklist

- [ ] Python 3.9+ installed
- [ ] Git installed
- [ ] Repository cloned
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created
- [ ] Application running (`uvicorn main:app --reload`)
- [ ] Accessed http://localhost:8000 successfully
- [ ] Tested farmer interface
- [ ] Tested officer dashboard

---

**Congratulations! 🎉 You've successfully set up AgroGuard locally!**

---

*Last Updated: January 2026*
*Version: 2.0*
