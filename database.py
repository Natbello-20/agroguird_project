import sqlite3
import uuid
from datetime import datetime
from passlib.context import CryptContext

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DB_NAME = "agroguard.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # 1. Users Table (Officers only)
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'officer',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. Farmers Table (with identity fields)
    c.execute('''
        CREATE TABLE IF NOT EXISTS farmers (
            device_id TEXT PRIMARY KEY,
            name TEXT,
            phone TEXT,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. Scans Table (Linked to Farmer Device ID)
    c.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_device_id TEXT,
            crop TEXT,
            disease TEXT,
            confidence REAL,
            location TEXT,
            status TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (farmer_device_id) REFERENCES farmers (device_id)
        )
    ''')

    # --- Safe migration: add name/phone columns if DB already existed ---
    for col, col_type in [("name", "TEXT"), ("phone", "TEXT")]:
        try:
            c.execute(f"ALTER TABLE farmers ADD COLUMN {col} {col_type}")
        except Exception:
            pass  # Column already exists
    
    conn.commit()
    conn.close()
    print("Database initialized.")

def create_officer(username, password):
    conn = get_db_connection()
    c = conn.cursor()
    
    hashed_password = pwd_context.hash(password)
    
    try:
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                  (username, hashed_password))
        conn.commit()
        print(f"Officer {username} created successfully.")
    except sqlite3.IntegrityError:
        print(f"Error: Username {username} already exists.")
    finally:
        conn.close()

def verify_officer(username, password):
    conn = get_db_connection()
    c = conn.cursor()
    
    user = c.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    
    if user and pwd_context.verify(password, user['password_hash']):
        return user
    return None

def register_farmer_scan(device_id, crop, disease, confidence, location, status):
    conn = get_db_connection()
    c = conn.cursor()
    
    # Ensure farmer exists (upsert-like logic)
    c.execute("INSERT OR IGNORE INTO farmers (device_id) VALUES (?)", (device_id,))
    c.execute("UPDATE farmers SET last_seen = CURRENT_TIMESTAMP WHERE device_id = ?", (device_id,))
    
    # Record scan
    c.execute('''
        INSERT INTO scans (farmer_device_id, crop, disease, confidence, location, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (device_id, crop, disease, confidence, location, status))
    
    scan_id = c.lastrowid
    conn.commit()
    conn.close()
    return scan_id

def register_farmer_profile(device_id, name, phone):
    """Save or update a farmer's name and phone number by device ID."""
    conn = get_db_connection()
    c = conn.cursor()
    # Ensure farmer row exists first
    c.execute("INSERT OR IGNORE INTO farmers (device_id) VALUES (?)", (device_id,))
    # Update profile fields and last_seen
    c.execute(
        "UPDATE farmers SET name = ?, phone = ?, last_seen = CURRENT_TIMESTAMP WHERE device_id = ?",
        (name, phone, device_id)
    )
    conn.commit()
    conn.close()

def get_dashboard_stats():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Aggregates
    total_scans = c.execute("SELECT COUNT(*) FROM scans").fetchone()[0]
    critical_alerts = c.execute("SELECT COUNT(*) FROM scans WHERE status = 'High Risk'").fetchone()[0]
    active_farmers = c.execute("SELECT COUNT(*) FROM farmers").fetchone()[0]
    # Simple district count proxy via distinct locations
    districts = c.execute("SELECT COUNT(DISTINCT location) FROM scans").fetchone()[0]
    
    # Recent Alerts (Limit 5 High Risk)
    alerts = c.execute('''
        SELECT disease, location, confidence, timestamp 
        FROM scans 
        WHERE status = 'High Risk' 
        ORDER BY timestamp DESC LIMIT 5
    ''').fetchall()
    
    # Recent Scans Table (Limit 10) — includes farmer name & phone
    recent_scans = c.execute('''
        SELECT s.*, f.device_id, f.name AS farmer_name, f.phone AS farmer_phone
        FROM scans s
        JOIN farmers f ON s.farmer_device_id = f.device_id
        ORDER BY s.timestamp DESC LIMIT 10
    ''').fetchall()

    # Chart 1: Disease Distribution
    distribution = c.execute('''
        SELECT disease, COUNT(*) as count 
        FROM scans 
        GROUP BY disease 
        ORDER BY count DESC LIMIT 5
    ''').fetchall()

    # Chart 2: Daily Scans (Last 7 Days)
    # Note: SQLite date manipulation can be tricky, using simple substring for YYYY-MM-DD
    daily = c.execute('''
        SELECT substr(timestamp, 1, 10) as day, COUNT(*) as count 
        FROM scans 
        GROUP BY day 
        ORDER BY day DESC LIMIT 7
    ''').fetchall()
    
    conn.close()
    
    return {
        "total_scans": total_scans,
        "critical_alerts": critical_alerts,
        "active_farmers": active_farmers,
        "districts_monitored": districts,
        "recent_alerts": [dict(row) for row in alerts],
        "recent_scans": [dict(row) for row in recent_scans],
        "disease_distribution": {row['disease']: row['count'] for row in distribution},
        "daily_scans": {row['day']: row['count'] for row in daily}
    }

if __name__ == "__main__":
    init_db()
    # Create default admin for testing
    create_officer("admin", "admin123")
