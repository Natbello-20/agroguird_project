# Super Admin Access Guide

## 🔐 Super Admin Portal

The Super Admin portal is a secure administrative interface for managing AEO (Agricultural Extension Officer) accounts in the AgroGuard system.

---

## 🌐 Access URL

**Super Admin Login Page:**
```
http://localhost:8000/superadmin/login
```

Or if deployed:
```
https://your-domain.com/superadmin/login
```

---

## 👤 Default Credentials

| Field | Value |
|-------|-------|
| **Username** | `superadmin` |
| **Password** | `SuperAdmin@123` |

⚠️ **IMPORTANT:** Change these credentials immediately after first login in a production environment!

---

## 📋 Super Admin Capabilities

### 1. Create AEO Accounts
- Staff ID assignment
- Ghana Card verification
- Phone number registration
- Temporary password generation
- Auto-flagged for password change on first login

### 2. Monitor System
- View total AEO accounts
- Track active accounts
- Review recent administrative actions

### 3. Audit Trail
All actions are automatically logged in the `audit_log` table with:
- Action type
- Entity affected
- Timestamp
- Performing admin ID
- Additional details

---

## 🎯 How to Create an AEO Account

1. **Login** at `/superadmin/login` with super admin credentials
2. **Navigate** to the dashboard (auto-redirected after login)
3. **Fill in the form** with AEO details:
   - Staff ID (e.g., `AEO001`)
   - Ghana Card Number (e.g., `GHA-123456789-0`)
   - Phone Number (e.g., `0241234567`)
   - Full Name (e.g., `John Mensah`)
   - Temporary Password (minimum 8 characters)
4. **Click** "Create AEO Account"
5. **Success!** The AEO can now login at `/aeo/login`

---

## 🔗 Quick Links

| Page | URL | Description |
|------|-----|-------------|
| **Super Admin Login** | `/superadmin/login` | Admin portal access |
| **Super Admin Dashboard** | `/superadmin/dashboard` | AEO management interface |
| **AEO Login** | `/aeo/login` | Extension officer login (API) |
| **Officer Login** | `/login` | Regular officer web login |
| **Farmer Scan** | `/` | Public farmer disease scan page |

---

## 🔒 Security Notes

### Authentication
- All super admin routes are protected with JWT tokens
- Tokens contain `"type": "superadmin"` claim
- The `get_superadmin_user` dependency enforces super admin access

### Password Security
- Passwords are hashed with bcrypt (cost factor 12)
- Temporary passwords must be changed on first AEO login
- No plain text passwords are ever stored

### Cookie Settings
- HTTP-only cookies prevent XSS attacks
- JWT tokens expire after 24 hours (configurable)
- Logout clears authentication cookies

---

## 🔄 User Hierarchy

```
┌─────────────────┐
│  Super Admin    │  ← Full system control
└────────┬────────┘
         │
    ┌────▼────┐
    │   AEO   │  ← Manages farmers in their district
    └────┬────┘
         │
    ┌────▼────┐
    │ Farmer  │  ← Anonymous scan submissions
    └─────────┘
```

---

## 📡 API Endpoints

### Super Admin Authentication
```http
POST /api/superadmin/login
Content-Type: application/x-www-form-urlencoded

username=superadmin&password=SuperAdmin@123
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user_id": 1,
  "user_type": "superadmin"
}
```

### Create AEO Account
```http
POST /superadmin/aeo/create
Authorization: Bearer {token}
Content-Type: application/json

{
  "staff_id": "AEO001",
  "ghana_card": "GHA-123456789-0",
  "phone": "0241234567",
  "name": "John Mensah",
  "temporary_password": "TempPass@123"
}
```

**Response:**
```json
{
  "id": 1,
  "staff_id": "AEO001",
  "ghana_card": "GHA-123456789-0",
  "phone": "0241234567",
  "name": "John Mensah",
  "must_change_password": true,
  "is_active": true
}
```

---

## 🛠️ Development

### Starting the Server
```bash
python -m uvicorn main:app --reload
```

### Database Tables
The super admin system uses:
- `superadmin` - Super admin accounts
- `aeo` - AEO accounts
- `audit_log` - Action tracking
- `users` - Regular officers
- `farmers` - Farmer device IDs
- `scans` - Disease scan records

### Testing Super Admin Creation
```python
import database

# Create a super admin
admin_id = database.create_superadmin(
    username="testadmin",
    password="Test@1234",
    full_name="Test Administrator"
)

# Verify credentials
admin = database.verify_superadmin("testadmin", "Test@1234")
print(admin)
```

---

## 📞 Support

For issues or questions:
- Check the audit log for action history
- Review server logs for authentication errors
- Ensure database migrations ran successfully

---

**Built with AgroGuard** 🌱 | Protecting Ghanaian crops through intelligent technology
