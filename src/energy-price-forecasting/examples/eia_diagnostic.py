"""
EIA API Diagnostic Script

This script tests the EIA API to diagnose why we're not getting data back.
It will try multiple approaches to identify the issue.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import requests
import json

# Get API key
api_key = os.getenv("EIA_API_KEY")

if not api_key:
    print("[ERROR] EIA_API_KEY not found in environment")
    sys.exit(1)

print("="*70)
print("EIA API Diagnostic Script")
print("="*70)
print(f"\n[INFO] API Key found: {api_key[:10]}... (showing first 10 chars)")

# Test 1: Check API key validity with a simple request
print("\n" + "="*70)
print("[TEST 1] Testing API Key Validity")
print("="*70)

test_url = "https://api.eia.gov/v2/"
response = requests.get(test_url, params={"api_key": api_key})
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    print("[SUCCESS] API key is valid!")
else:
    print(f"[ERROR] API returned status {response.status_code}")
    print(f"Response: {response.text[:500]}")

# Test 2: Try to get petroleum data routes
print("\n" + "="*70)
print("[TEST 2] Exploring Petroleum API Routes")
print("="*70)

routes_url = "https://api.eia.gov/v2/petroleum/"
response = requests.get(routes_url, params={"api_key": api_key})
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    try:
        data = response.json()
        print(f"[SUCCESS] Available routes:")
        if "response" in data and "routes" in data["response"]:
            for route in data["response"]["routes"][:10]:  # Show first 10
                print(f"  - {route.get('id', 'N/A')}: {route.get('name', 'N/A')}")
        else:
            print(f"Response structure: {json.dumps(data, indent=2)[:500]}")
    except Exception as e:
        print(f"[ERROR] Failed to parse response: {e}")
        print(f"Raw response: {response.text[:500]}")
else:
    print(f"[ERROR] Failed with status {response.status_code}")
    print(f"Response: {response.text[:500]}")

# Test 3: Try specific WTI endpoint
print("\n" + "="*70)
print("[TEST 3] Testing WTI Crude Oil Spot Price Endpoint")
print("="*70)

# Try the endpoint structure from our client
wti_url = "https://api.eia.gov/v2/petroleum/pri/spt/data/"
params = {
    "api_key": api_key,
    "frequency": "daily",
    "data[0]": "value",
    "facets[series][]": "PET.RWTC.D",
    "start": "2024-01-01",
    "end": "2024-01-31",
    "sort[0][column]": "period",
    "sort[0][direction]": "asc",
    "offset": 0,
    "length": 100
}

print(f"URL: {wti_url}")
print(f"Parameters: {json.dumps(params, indent=2)}")

response = requests.get(wti_url, params=params)
print(f"\nStatus Code: {response.status_code}")

if response.status_code == 200:
    try:
        data = response.json()
        print(f"[SUCCESS] Response received!")
        print(f"\nResponse structure:")
        print(json.dumps(data, indent=2)[:1000])  # Show first 1000 chars
        
        if "response" in data:
            resp_data = data["response"]
            if "data" in resp_data:
                records = resp_data["data"]
                print(f"\n[INFO] Number of records: {len(records)}")
                if len(records) > 0:
                    print(f"[INFO] First record: {json.dumps(records[0], indent=2)}")
                else:
                    print("[WARNING] No data records returned!")
                    print(f"[INFO] Full response: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"[ERROR] Failed to parse JSON: {e}")
        print(f"Raw response: {response.text[:1000]}")
else:
    print(f"[ERROR] Request failed with status {response.status_code}")
    print(f"Response: {response.text[:500]}")

# Test 4: Try alternative date range (older data)
print("\n" + "="*70)
print("[TEST 4] Testing with Older Date Range (2023)")
print("="*70)

params["start"] = "2023-01-01"
params["end"] = "2023-01-31"

response = requests.get(wti_url, params=params)
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    try:
        data = response.json()
        if "response" in data and "data" in data["response"]:
            records = data["response"]["data"]
            print(f"[INFO] Number of records: {len(records)}")
            if len(records) > 0:
                print(f"[SUCCESS] Got data for 2023!")
                print(f"First record: {json.dumps(records[0], indent=2)}")
            else:
                print("[WARNING] Still no data for 2023")
        else:
            print(f"[WARNING] Unexpected response structure: {json.dumps(data, indent=2)[:500]}")
    except Exception as e:
        print(f"[ERROR] Failed to parse: {e}")

# Test 5: Try without facets (different query structure)
print("\n" + "="*70)
print("[TEST 5] Testing Alternative Query Structure")
print("="*70)

alt_params = {
    "api_key": api_key,
    "frequency": "daily",
    "data[]": "value",
    "start": "2023-01-01",
    "end": "2023-01-31",
    "length": 100
}

response = requests.get(wti_url, params=alt_params)
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    try:
        data = response.json()
        if "response" in data and "data" in data["response"]:
            records = data["response"]["data"]
            print(f"[INFO] Number of records: {len(records)}")
            if len(records) > 0:
                print(f"[SUCCESS] Alternative structure worked!")
                print(f"First record: {json.dumps(records[0], indent=2)}")
        else:
            print(f"Response: {json.dumps(data, indent=2)[:500]}")
    except Exception as e:
        print(f"[ERROR] {e}")

print("\n" + "="*70)
print("[DIAGNOSTIC COMPLETE]")
print("="*70)
print("\nIf you see data in any of the tests above, we can update the client accordingly.")
print("If no tests return data, the issue may be with:")
print("  1. The series ID (PET.RWTC.D) may have changed")
print("  2. The endpoint structure may have been updated by EIA")
print("  3. Data availability issues on EIA's side")
print("\nNext step: Visit https://www.eia.gov/opendata/browser/ to find the current")
print("series ID and endpoint structure for WTI crude oil spot prices.")

