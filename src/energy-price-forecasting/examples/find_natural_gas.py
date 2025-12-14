"""Find Natural Gas series in EIA API"""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()
import requests
import pandas as pd

api_key = os.getenv("EIA_API_KEY")

# Try natural gas endpoint
url = "https://api.eia.gov/v2/natural-gas/pri/sum/data/"
params = {
    "api_key": api_key,
    "frequency": "daily",
    "data[]": "value",
    "start": "2024-01-01",
    "end": "2024-01-31",
    "length": 1000
}

print("Testing Natural Gas endpoint...")
response = requests.get(url, params=params)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    records = data.get("response", {}).get("data", [])
    print(f"Records: {len(records)}")
    
    if records:
        df = pd.DataFrame(records)
        print(f"\nColumns: {df.columns.tolist()}")
        
        # Look for Henry Hub
        if "series-description" in df.columns:
            henry_hub = df[df["series-description"].str.contains("Henry Hub", case=False, na=False)]
            if not henry_hub.empty:
                print(f"\nFound Henry Hub Natural Gas!")
                print(f"Series code: {henry_hub['series'].iloc[0]}")
                print(f"Description: {henry_hub['series-description'].iloc[0]}")
                print(f"\nSample data:")
                print(henry_hub[["period", "value", "series"]].head().to_string(index=False))
            else:
                print("\nAll series:")
                print(df[["series", "series-description"]].drop_duplicates().to_string(index=False))
else:
    print(f"Error: {response.text[:500]}")

