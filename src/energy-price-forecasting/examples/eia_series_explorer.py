"""
EIA API Series Explorer

This script helps find the correct series IDs and filters for petroleum price data.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import requests
import json
import pandas as pd

api_key = os.getenv("EIA_API_KEY")

if not api_key:
    print("[ERROR] EIA_API_KEY not found")
    sys.exit(1)

print("="*70)
print("EIA API Series Explorer - Finding WTI/Natural Gas Series")
print("="*70)

# Get data without series filter to see what's available
url = "https://api.eia.gov/v2/petroleum/pri/spt/data/"
params = {
    "api_key": api_key,
    "frequency": "daily",
    "data[]": "value",
    "start": "2024-01-01",
    "end": "2024-01-31",
    "length": 5000  # Get more records
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    records = data.get("response", {}).get("data", [])
    
    print(f"\n[INFO] Retrieved {len(records)} total records")
    
    if records:
        # Convert to DataFrame for analysis
        df = pd.DataFrame(records)
        
        # Show available series
        print("\n[AVAILABLE SERIES]")
        print("-" * 70)
        if "series" in df.columns:
            series_counts = df.groupby(["series", "series-description"]).size().reset_index(name="count")
            print(series_counts.to_string(index=False))
        
        # Filter for WTI
        print("\n" + "="*70)
        print("[WTI CRUDE OIL] Series")
        print("="*70)
        if "series-description" in df.columns:
            wti_df = df[df["series-description"].str.contains("WTI|West Texas", case=False, na=False)]
            if not wti_df.empty:
                print(f"Found {len(wti_df)} WTI records")
                print(f"\nSeries code: {wti_df['series'].iloc[0]}")
                print(f"Description: {wti_df['series-description'].iloc[0]}")
                print(f"\nSample data:")
                print(wti_df[["period", "value", "series", "series-description"]].head(10).to_string(index=False))
            else:
                print("[WARNING] No WTI series found in current data")
                print(f"\nAvailable descriptions:")
                print(df["series-description"].unique())
        
        # Filter for Natural Gas
        print("\n" + "="*70)
        print("[NATURAL GAS] Series")
        print("="*70)
        ng_df = df[df["series-description"].str.contains("Natural Gas|Henry Hub", case=False, na=False)]
        if not ng_df.empty:
            print(f"Found {len(ng_df)} Natural Gas records")
            print(f"\nSeries code: {ng_df['series'].iloc[0]}")
            print(f"Description: {ng_df['series-description'].iloc[0]}")
            print(f"\nSample data:")
            print(ng_df[["period", "value", "series", "series-description"]].head(10).to_string(index=False))
        else:
            print("[WARNING] No Natural Gas series found")

        # Show all unique series for reference
        print("\n" + "="*70)
        print("[ALL UNIQUE SERIES CODES]")
        print("="*70)
        if "series" in df.columns and "series-description" in df.columns:
            unique_series = df[["series", "series-description"]].drop_duplicates()
            print(unique_series.to_string(index=False))
        
else:
    print(f"[ERROR] API returned status {response.status_code}")
    print(response.text[:500])

print("\n" + "="*70)
print("[EXPLORATION COMPLETE]")
print("="*70)

