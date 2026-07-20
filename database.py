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
            segment_id TEXT,
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
    # Add segment_id to scans if missing
    try:
        c.execute("ALTER TABLE scans ADD COLUMN segment_id TEXT")
    except Exception:
        pass
    
    # 4. AEO Table (Extension Officers)
    c.execute('''
        CREATE TABLE IF NOT EXISTS aeo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id TEXT UNIQUE NOT NULL,
            ghana_card TEXT UNIQUE NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            hashed_password TEXT NOT NULL,
            must_change_password INTEGER DEFAULT 1,
            is_active INTEGER DEFAULT 1,
            email TEXT,
            district TEXT
        )
    ''')
    
    # --- Safe migration: add email and district columns if DB already existed ---
    for col in ["email", "district"]:
        try:
            c.execute(f"ALTER TABLE aeo ADD COLUMN {col} TEXT")
        except Exception:
            pass  # Column already exists
    
    # --- Safe migration: add biometric and profile tracking columns ---
    for col, col_type in [
        ("biometric_id", "TEXT"),
        ("biometric_public_key", "TEXT"), 
        ("profile_completed", "INTEGER DEFAULT 0"),
        ("last_login", "TIMESTAMP"),
        ("profile_picture", "TEXT")
    ]:
        try:
            c.execute(f"ALTER TABLE aeo ADD COLUMN {col} {col_type}")
        except Exception:
            pass  # Column already exists

    # 5. Super Admin Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS superadmin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 5. Super Admin Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS superadmin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 6. Audit Log Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            entity TEXT NOT NULL,
            entity_id INTEGER NOT NULL,
            performed_by INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            details TEXT
        )
    ''')
    
    # 7. Alerts Table (for broadcast alerts to farmers)
    c.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_type TEXT NOT NULL,
            title TEXT,
            message TEXT NOT NULL,
            priority TEXT,
            target_type TEXT,
            target_audience TEXT NOT NULL,
            target_phone TEXT,
            district TEXT,
            sent_by INTEGER NOT NULL,
            recipient_count INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sent_by) REFERENCES aeo(id)
        )
    ''')
    
    # --- Safe migration: add new columns to alerts table ---
    for col, col_type in [
        ("title", "TEXT"),
        ("priority", "TEXT"),
        ("target_type", "TEXT"),
        ("target_phone", "TEXT")
    ]:
        try:
            c.execute(f"ALTER TABLE alerts ADD COLUMN {col} {col_type}")
        except Exception:
            pass  # Column already exists
    
    # 8. Support Tickets Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS support_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            priority TEXT NOT NULL,
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            contact TEXT,
            submitted_by INTEGER NOT NULL,
            status TEXT DEFAULT 'open',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            resolved_at DATETIME,
            resolved_by INTEGER,
            FOREIGN KEY (submitted_by) REFERENCES aeo(id)
        )
    ''')
    
    # --- Safe migration: add additional columns to farmers table for manual registration ---
    for col in ["ghana_card", "district", "crops", "registration_method", "registered_by"]:
        try:
            c.execute(f"ALTER TABLE farmers ADD COLUMN {col} TEXT")
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

def register_farmer_scan(device_id, crop, disease, confidence, location, status, segment_id=None):
    conn = get_db_connection()
    c = conn.cursor()

    # Ensure farmer exists (upsert-like logic)
    c.execute("INSERT OR IGNORE INTO farmers (device_id) VALUES (?)", (device_id,))
    c.execute("UPDATE farmers SET last_seen = CURRENT_TIMESTAMP WHERE device_id = ?", (device_id,))

    # Record scan with segment_id
    c.execute('''
        INSERT INTO scans (farmer_device_id, crop, disease, confidence, location, status, segment_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (device_id, crop, disease, confidence, location, status, segment_id))

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

def count_scans_for_segment(device_id: str, segment_id: str) -> int:
    """Count scans for a specific device in a specific GPS segment"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM scans WHERE farmer_device_id = ? AND segment_id = ?', (device_id, segment_id))
    count = c.fetchone()[0]
    conn.close()
    return count


def count_total_scans(device_id: str) -> int:
    """Count total scans for a device across all segments"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM scans WHERE farmer_device_id = ?', (device_id,))
    count = c.fetchone()[0]
    conn.close()
    return count


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


# ---------------------------------------------------------------------------
# AEO Management Functions
# ---------------------------------------------------------------------------

def create_aeo(staff_id: str, ghana_card: str, phone: str, name: str, password: str):
    """Create a new AEO account with a temporary password.
    Password is hashed; must_change_password flag is set.
    """
    conn = get_db_connection()
    c = conn.cursor()
    hashed = pwd_context.hash(password)
    c.execute('''
        INSERT INTO aeo (staff_id, ghana_card, phone, name, hashed_password, must_change_password, is_active)
        VALUES (?, ?, ?, ?, ?, 1, 1)
    ''', (staff_id, ghana_card, phone, name, hashed))
    aeo_id = c.lastrowid
    conn.commit()
    conn.close()
    return aeo_id

def get_aeo_by_identifier(identifier: str):
    """Retrieve AEO record by staff_id, ghana_card, or phone."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT * FROM aeo WHERE staff_id = ? OR ghana_card = ? OR phone = ?
    ''', (identifier, identifier, identifier))
    aeo = c.fetchone()
    conn.close()
    return aeo

def update_aeo(aeo_id: int, name: str = None, phone: str = None, is_active: int = None):
    """Update mutable fields of an AEO record. Only provided fields are changed."""
    conn = get_db_connection()
    c = conn.cursor()
    fields = []
    params = []
    if name is not None:
        fields.append('name = ?')
        params.append(name)
    if phone is not None:
        fields.append('phone = ?')
        params.append(phone)
    if is_active is not None:
        fields.append('is_active = ?')
        params.append(is_active)
    if not fields:
        conn.close()
        return False
    params.append(aeo_id)
    query = f"UPDATE aeo SET {', '.join(fields)} WHERE id = ?"
    c.execute(query, tuple(params))
    conn.commit()
    conn.close()
    return True

def delete_aeo(aeo_id: int):
    """Deactivate (soft delete) an AEO account."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('UPDATE aeo SET is_active = 0 WHERE id = ?', (aeo_id,))
    conn.commit()
    conn.close()
    return True

def reset_aeo_password(aeo_id: int, new_password: str):
    """Set a new temporary password for an AEO and mark must_change_password."""
    conn = get_db_connection()
    c = conn.cursor()
    hashed = pwd_context.hash(new_password)
    c.execute('''
        UPDATE aeo SET hashed_password = ?, must_change_password = 1 WHERE id = ?
    ''', (hashed, aeo_id))
    conn.commit()
    conn.close()
    return True

def change_aeo_password(aeo_id: int, new_password: str):
    """Change password after first login and clear must_change_password flag."""
    conn = get_db_connection()
    c = conn.cursor()
    hashed = pwd_context.hash(new_password)
    c.execute('''
        UPDATE aeo SET hashed_password = ?, must_change_password = 0 WHERE id = ?
    ''', (hashed, aeo_id))
    conn.commit()
    conn.close()
    return True

def log_audit(action: str, entity: str, entity_id: int, performed_by: int, details: str = None):
    """Insert an audit log entry.
    action: e.g., 'create', 'update', 'delete', 'reset_password'
    entity: e.g., 'aeo'
    """
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO audit_log (action, entity, entity_id, performed_by, details)
        VALUES (?, ?, ?, ?, ?)
    ''', (action, entity, entity_id, performed_by, details))
    conn.commit()
    conn.close()
    return True


# ---------------------------------------------------------------------------
# Super Admin Management Functions
# ---------------------------------------------------------------------------

def create_superadmin(username: str, password: str, full_name: str):
    """Create a new super admin account."""
    conn = get_db_connection()
    c = conn.cursor()
    hashed = pwd_context.hash(password)
    try:
        c.execute('''
            INSERT INTO superadmin (username, hashed_password, full_name, is_active)
            VALUES (?, ?, ?, 1)
        ''', (username, hashed, full_name))
        superadmin_id = c.lastrowid
        conn.commit()
        conn.close()
        return superadmin_id
    except sqlite3.IntegrityError:
        conn.close()
        return None


def get_superadmin_by_username(username: str):
    """Retrieve super admin record by username."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM superadmin WHERE username = ?', (username,))
    superadmin = c.fetchone()
    conn.close()
    return superadmin


def verify_superadmin(username: str, password: str):
    """Verify super admin credentials and return user record if valid."""
    superadmin = get_superadmin_by_username(username)
    if not superadmin:
        return None
    
    if not superadmin['is_active']:
        return None
    
    if pwd_context.verify(password, superadmin['hashed_password']):
        return superadmin
    
    return None


def update_superadmin(superadmin_id: int, full_name: str = None, is_active: int = None):
    """Update mutable fields of a super admin record."""
    conn = get_db_connection()
    c = conn.cursor()
    fields = []
    params = []
    
    if full_name is not None:
        fields.append('full_name = ?')
        params.append(full_name)
    if is_active is not None:
        fields.append('is_active = ?')
        params.append(is_active)
    
    if not fields:
        conn.close()
        return False
    
    params.append(superadmin_id)
    c.execute(f"UPDATE superadmin SET {', '.join(fields)} WHERE id = ?", params)
    conn.commit()
    conn.close()
    return True

if __name__ == "__main__":
    init_db()
    # Create default admin for testing
    create_officer("admin", "admin123")
