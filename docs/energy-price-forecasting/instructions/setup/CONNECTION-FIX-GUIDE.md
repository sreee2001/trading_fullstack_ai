# Database Connection Issue - Fix Guide

## Problem Identified

The connection is timing out when trying to connect from Windows Python to WSL Docker PostgreSQL, even though:
- ✅ Port 5432 is reachable (socket test passed)
- ✅ PostgreSQL is running and responding (WSL test passed)
- ✅ PostgreSQL is listening on all addresses

## Root Cause

This is a **WSL2 networking + psycopg3 compatibility issue**. The psycopg3 library might be trying multiple connection attempts (IPv4/IPv6) and timing out.

## ✅ **SOLUTION: Use localhost with Port Forwarding**

You need to run ONE PowerShell command as Administrator to enable port forwarding.

### **Steps:**

#### 1. Open PowerShell as Administrator
- Press `Windows Key`
- Type "PowerShell"
- Right-click "Windows PowerShell"
- Select **"Run as administrator"**

#### 2. Run This ONE Command:
```powershell
netsh interface portproxy add v4tov4 listenport=5432 listenaddress=0.0.0.0 connectport=5432 connectaddress=127.0.0.1
```

#### 3. Verify It Worked:
```powershell
netsh interface portproxy show all
```

You should see:
```
Listen on ipv4:             Connect to ipv4:
Address         Port        Address         Port
--------------- ----------  --------------- ----------
0.0.0.0         5432        127.0.0.1       5432
```

#### 4. Update .env File:
Change DB_HOST back to localhost:
```bash
# FROM:
DB_HOST=172.31.236.192

# TO:
DB_HOST=localhost
```

#### 5. Test Connection:
```bash
cd C:\Users\Srikanth\source\repos\trading_fullstack_ai\src\energy-price-forecasting
python test_connection.py
```

Should see:
```
✅ SUCCESS! Connected to database
```

---

## Alternative: Use Docker Desktop

If port forwarding doesn't work, the **cleanest solution** is Docker Desktop for Windows:

1. Install Docker Desktop (if not already)
2. Open Docker Desktop
3. Settings → Resources → WSL Integration
4. Enable integration with your WSL distribution
5. Restart Docker
6. Use `DB_HOST=localhost` in .env

This makes Docker ports directly available to Windows without any port forwarding!

---

## What to Do Next

**Please run the Administrator PowerShell command above**, then let me know if it works!

If you prefer Docker Desktop instead, let me know and I'll guide you through that setup.



