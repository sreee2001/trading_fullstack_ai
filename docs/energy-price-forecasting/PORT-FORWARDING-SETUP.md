# Port Forwarding Setup Guide

## ⚠️ Port Forwarding Requires Administrator Access

The command to set up port forwarding requires **Administrator privileges**, which I cannot execute directly.

---

## ✅ **SOLUTION: Use WSL IP Address Instead**

This is actually **simpler** and **works immediately** without needing Administrator access!

### **Your WSL IP Address:**
```
172.31.236.192
```

---

## 📝 **REQUIRED: Edit .env File**

The `.env` file is protected (gitignored), so you need to edit it manually.

### **Step 1: Open the .env file**

**Location:**
```
C:\Users\Srikanth\source\repos\trading_fullstack_ai\src\energy-price-forecasting\.env
```

If the file doesn't exist, create it by copying from `env.example`:
```bash
cd C:\Users\Srikanth\source\repos\trading_fullstack_ai\src\energy-price-forecasting
copy env.example .env
```

### **Step 2: Update Database Host**

Change this line:
```bash
# OLD (doesn't work with WSL Docker):
DB_HOST=localhost

# NEW (use WSL IP):
DB_HOST=172.31.236.192
```

### **Complete .env Configuration:**

Here's what your `.env` file should contain:

```bash
# =============================================================================
# API Keys
# =============================================================================

# EIA API Key (Required for EIA data)
# Get your key at: https://www.eia.gov/opendata/register.php
EIA_API_KEY=your_actual_eia_key_here

# FRED API Key (Required for FRED data)
# Get your key at: https://fred.stlouisfed.org/docs/api/api_key.html
FRED_API_KEY=your_actual_fred_key_here

# =============================================================================
# Database Configuration (UPDATED FOR WSL)
# =============================================================================

# Use WSL IP address instead of localhost
DB_HOST=172.31.236.192
DB_PORT=5432
DB_NAME=energy_forecasting
DB_USER=energy_user
DB_PASSWORD=energy_password

# =============================================================================
# Application Configuration
# =============================================================================

# Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Database connection pool settings
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
```

**IMPORTANT:** Replace `your_actual_eia_key_here` and `your_actual_fred_key_here` with your real API keys!

---

## 🧪 **Step 3: Test the Connection**

After updating the `.env` file:

```bash
cd C:\Users\Srikanth\source\repos\trading_fullstack_ai\src\energy-price-forecasting
python examples/database_example.py
```

**Expected Output:**
```
[1/6] Initializing database connection...
SUCCESS: Database connection established
[2/6] Checking TimescaleDB extension...
SUCCESS: TimescaleDB is available
...
```

---

## ⚠️ **If WSL IP Changes**

WSL2 IPs can change after system restart. If the connection stops working:

1. Get new WSL IP:
   ```bash
   wsl hostname -I
   ```

2. Update `.env` file with new IP

### **Alternative: Make it Permanent (Optional)**

To keep a consistent WSL IP, you can configure WSL2 networking, but that's more complex. For now, the IP-based approach works fine.

---

## 🔄 **Alternative: Port Forwarding (If You Want to Try)**

If you prefer to use `localhost` instead of the IP address, you need to run this command **as Administrator**:

### **Step 1: Open PowerShell as Administrator**
1. Press Windows key
2. Type "PowerShell"
3. Right-click "Windows PowerShell"
4. Select "Run as administrator"

### **Step 2: Run Port Forwarding Command**
```powershell
netsh interface portproxy add v4tov4 listenport=5432 listenaddress=0.0.0.0 connectport=5432 connectaddress=127.0.0.1
```

### **Step 3: Verify**
```powershell
netsh interface portproxy show all
```

### **Step 4: Update .env**
```bash
DB_HOST=localhost  # Can use localhost now
```

### **To Remove Port Forwarding Later:**
```powershell
netsh interface portproxy delete v4tov4 listenport=5432 listenaddress=0.0.0.0
```

---

## ✅ **Recommended Approach**

**Use the WSL IP address** (`172.31.236.192`) - it's simpler and works immediately!

1. ✅ No Administrator access needed
2. ✅ Works right away
3. ✅ Easy to update if IP changes

---

## 📋 **Quick Checklist**

- [ ] Create/edit `.env` file at: `src/energy-price-forecasting/.env`
- [ ] Set `DB_HOST=172.31.236.192`
- [ ] Set `DB_PORT=5432`
- [ ] Set `DB_NAME=energy_forecasting`
- [ ] Set `DB_USER=energy_user`
- [ ] Set `DB_PASSWORD=energy_password`
- [ ] Add your EIA and FRED API keys
- [ ] Save the file
- [ ] Run: `python examples/database_example.py`
- [ ] Should see "SUCCESS: Database connection established"

---

## 🆘 **If It Still Doesn't Work**

Let me know and I can:
1. Help troubleshoot the specific error
2. Try alternative connection methods
3. Set up Docker Desktop instead (cleanest solution)

**After you update the .env file, just say "test it" and I'll run the connection test!** 🚀

