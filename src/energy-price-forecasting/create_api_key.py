#!/usr/bin/env python3
"""
Script to create an API key for the dashboard.
"""

from api.auth.api_key_manager import get_api_key_manager

def main():
    manager = get_api_key_manager()
    
    print("\n" + "="*60)
    print("Creating API Key for Dashboard")
    print("="*60)
    
    try:
        api_key, key_id = manager.create_api_key(
            name="Dashboard Key",
            user_id="dashboard_user"
        )
        
        print(f"\n✅ API KEY CREATED SUCCESSFULLY!")
        print(f"\n{'='*60}")
        print(f"API Key: {api_key}")
        print(f"Key ID: {key_id}")
        print(f"{'='*60}")
        print("\n📋 Next Steps:")
        print("1. Copy the API key above")
        print("2. Open the dashboard at http://localhost:5173")
        print("3. Click 'Enter API Key' in the header")
        print("4. Paste the key and click 'Save'")
        print("\n   OR")
        print("\n5. Create dashboard/.env file with:")
        print(f"   VITE_API_KEY={api_key}")
        print("\n" + "="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error creating API key: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure the database is running: docker ps")
        print("2. Check if api_keys table exists:")
        print("   docker exec energy_forecasting_db psql -U energy_user -d energy_forecasting -c '\\dt api_keys'")
        print("3. If table doesn't exist, run:")
        print("   Get-Content database/init.sql | docker exec -i energy_forecasting_db psql -U energy_user -d energy_forecasting")
        raise

if __name__ == "__main__":
    main()



