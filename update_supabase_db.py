import os
import json
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://kwwokwoyqygbcrcsyyob.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt3d29rd295cXlnYmNyY3N5eW9iIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTk4ODIyNCwiZXhwIjoyMDkxNTY0MjI0fQ.8eP2BSCzu5AMlamlsi2-2pKmmEPAyD4-ljbwyMk-TSU")
BUCKET_NAME = "kookmin"

try:
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Download current
    res = supabase.storage.from_(BUCKET_NAME).download("site_data.json")
    data = json.loads(res.decode('utf-8'))
    
    # Check what is in executive_groups
    # If the user changed the code but site_data.json overrides it, we should update site_data.json to match the new structure, or remove it so it falls back to defaults.
    
    if "executive_groups" in data:
        print("Existing executive_groups in DB:", json.dumps(data["executive_groups"], ensure_ascii=False, indent=2))
        # Let's delete it so it uses default
        del data["executive_groups"]
        
    # Upload back
    new_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
    supabase.storage.from_(BUCKET_NAME).update("site_data.json", new_data, {"contentType": "application/json"})
    print("Successfully deleted executive_groups from DB so it uses defaults.")
except Exception as e:
    print(f"Error: {e}")

