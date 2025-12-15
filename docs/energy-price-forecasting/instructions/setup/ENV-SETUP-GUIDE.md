# Energy Price Forecasting System - Environment Variables Template

## How to Set Up Your .env File

### Step 1: Create the .env file
Create a file named `.env` in the `src/energy-price-forecasting/` directory.

**Location:** `src/energy-price-forecasting/.env`

### Step 2: Add Your API Keys

Copy and paste this content into your `.env` file:

```
# EIA (U.S. Energy Information Administration) API Key
EIA_API_KEY=your_eia_api_key_here

# FRED (Federal Reserve Economic Data) API Key
FRED_API_KEY=your_fred_api_key_here
```

### Step 3: Get Your API Keys

#### EIA API Key (Free)
1. Go to: https://www.eia.gov/opendata/register.php
2. Fill out the registration form
3. You'll receive your API key via email immediately
4. Copy the key and replace `your_eia_api_key_here` in your .env file

#### FRED API Key (Free)
1. Go to: https://fred.stlouisfed.org/docs/api/api_key.html
2. Click "Request API Key"
3. Create a free account or login
4. You'll get your API key instantly
5. Copy the key and replace `your_fred_api_key_here` in your .env file

#### Yahoo Finance
- **No API key needed!** Yahoo Finance is completely free and doesn't require authentication.

---

## Example .env File (with fake keys)

```
EIA_API_KEY=abcd1234efgh5678ijkl9012mnop3456
FRED_API_KEY=1234567890abcdef1234567890abcdef
```

---

## Verification

Your `.env` file should look like this:

**File:** `src/energy-price-forecasting/.env`
```
EIA_API_KEY=<your-actual-key>
FRED_API_KEY=<your-actual-key>
```

**Important Notes:**
- No quotes needed around the keys
- No spaces around the `=` sign
- Keep this file secure and never commit it to git (it's in `.gitignore`)
- The `.env` file is loaded automatically by the example scripts using `python-dotenv`

---

## How the .env File is Used

The example scripts automatically load the `.env` file using this code:

```python
from dotenv import load_dotenv
load_dotenv()  # Loads .env from current or parent directories
```

The API clients then read the environment variables:

```python
# In eia_client.py
api_key = api_key or os.getenv("EIA_API_KEY")

# In fred_client.py
api_key = api_key or os.getenv("FRED_API_KEY")
```

---

## Troubleshooting

### Error: "EIA API key is required"
- Check that your `.env` file exists in `src/energy-price-forecasting/`
- Check that the variable name is exactly `EIA_API_KEY` (case-sensitive)
- Check that there are no spaces around the `=` sign
- Check that your API key is valid (test it on the EIA website)

### Error: "FRED API key is required"
- Same troubleshooting steps as above, but for `FRED_API_KEY`

### Where to place the .env file?
**Only ONE location:** `src/energy-price-forecasting/.env`

This is the project root where:
- `requirements.txt` is located
- `setup.py` is located
- `data_ingestion/` folder is located
- `examples/` folder is located

---

## Testing After Setup

After creating your `.env` file with valid API keys, test each example:

```powershell
cd src\energy-price-forecasting\examples

# Test EIA (requires EIA_API_KEY)
python fetch_wti_example.py

# Test FRED (requires FRED_API_KEY)
python fetch_fred_example.py

# Test Yahoo Finance (no API key needed)
python fetch_yahoo_finance_example.py
```

If you see data output, your setup is correct! ✅

