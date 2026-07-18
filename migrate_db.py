#!/usr/bin/env python3
"""
Database Migration Script
Run this to safely update the database schema without losing data
"""

import sqlite3
import os

DB_NAME = "agroguard.db"

def migrate():
    """Run all database migrations safely"""
    
    if not os.path.exists(DB_NAME):
        print(f"❌ Database {DB_NAME} not found. Run main.py first to create it.")
        return
    
    print(f"🔄 Starting migration for {DB_NAME}...")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # ============================================================================
    # Migration 1: Add new columns to farmers table
    # ============================================================================
    print("\n📋 Migration 1: Updating farmers table...")
    for col, col_type in [
        ("ghana_card", "TEXT"),
        ("district", "TEXT"),
        ("crops", "TEXT"),
        ("registration_method", "TEXT"),
        ("registered_by", "TEXT")
    ]:
        try:
            c.execute(f"ALTER TABLE farmers ADD COLUMN {col} {col_type}")
            print(f"  ✅ Added column: {col}")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print(f"  ⏭️  Column {col} already exists")
            else:
                print(f"  ⚠️  Error adding {col}: {e}")
    
    # ============================================================================
    # Migration 2: Create alerts table
    # ============================================================================
    print("\n📋 Migration 2: Creating alerts table...")
    try:
        c.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT NOT NULL,
                target_audience TEXT NOT NULL,
                district TEXT,
                message TEXT NOT NULL,
                sent_by INTEGER NOT NULL,
                recipient_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sent_by) REFERENCES aeo(id)
            )
        ''')
        
        # Check if table was just created or already existed
        c.execute("SELECT COUNT(*) FROM alerts")
        c.fetchone()
        print("  ✅ Alerts table ready")
    except Exception as e:
        print(f"  ⚠️  Error creating alerts table: {e}")
    
    # ============================================================================
    # Migration 3: Create support_tickets table
    # ============================================================================
    print("\n📋 Migration 3: Creating support_tickets table...")
    try:
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
        
        # Check if table was just created or already existed
        c.execute("SELECT COUNT(*) FROM support_tickets")
        c.fetchone()
        print("  ✅ Support tickets table ready")
    except Exception as e:
        print(f"  ⚠️  Error creating support_tickets table: {e}")
    
    # ============================================================================
    # Migration 4: Add email and district to aeo table (if not already there)
    # ============================================================================
    print("\n📋 Migration 4: Updating aeo table...")
    for col in ["email", "district"]:
        try:
            c.execute(f"ALTER TABLE aeo ADD COLUMN {col} TEXT")
            print(f"  ✅ Added column: {col}")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print(f"  ⏭️  Column {col} already exists")
            else:
                print(f"  ⚠️  Error adding {col}: {e}")
    
    # Commit changes
    conn.commit()
    
    # ============================================================================
    # Verify migrations
    # ============================================================================
    print("\n🔍 Verifying migrations...")
    
    # Check farmers table
    c.execute("PRAGMA table_info(farmers)")
    farmers_cols = [row[1] for row in c.fetchall()]
    print(f"  Farmers table columns: {', '.join(farmers_cols)}")
    
    # Check alerts table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alerts'")
    if c.fetchone():
        c.execute("SELECT COUNT(*) FROM alerts")
        count = c.fetchone()[0]
        print(f"  ✅ Alerts table exists ({count} records)")
    else:
        print(f"  ❌ Alerts table not found")
    
    # Check support_tickets table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='support_tickets'")
    if c.fetchone():
        c.execute("SELECT COUNT(*) FROM support_tickets")
        count = c.fetchone()[0]
        print(f"  ✅ Support tickets table exists ({count} records)")
    else:
        print(f"  ❌ Support tickets table not found")
    
    # Check aeo table
    c.execute("PRAGMA table_info(aeo)")
    aeo_cols = [row[1] for row in c.fetchall()]
    print(f"  AEO table columns: {', '.join(aeo_cols)}")
    
    conn.close()
    
    print("\n✅ Migration complete! Your database is up to date.")
    print("You can now run the application: python main.py")

if __name__ == "__main__":
    migrate()
