import re
import os

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add supabase import
content = content.replace("from fastapi import", "from supabase import create_client, Client\nfrom fastapi import")

# 2. Add Supabase initialization
supabase_init = """
# Supabase 설정
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://kwwokwoyqygbcrcsyyob.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt3d29rd295cXlnYmNyY3N5eW9iIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU5ODgyMjQsImV4cCI6MjA5MTU2NDIyNH0.q08r-pVhgw_7P0z-yjlj99yTrqGnvqJZzVLDPsvMgos")
BUCKET_NAME = "kookmin"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
"""

content = content.replace("app = FastAPI()", supabase_init + "\napp = FastAPI()")

# 3. Remove mount and local dir stuff
content = re.sub(r'# 폴더 설정.*?app\.mount\("/uploads", StaticFiles\(directory=UPLOAD_DIR\), name="uploads"\)', '', content, flags=re.DOTALL)

# 4. Modify save_upload
new_save_upload = """
def save_upload(file: UploadFile | None, subdir: str) -> str | None:
    if not file or not file.filename:
        return None
    
    filename = safe_filename(file.filename)
    path = f"{subdir}/{filename}"
    
    file_bytes = file.file.read()
    
    # Upload to Supabase Storage
    try:
        supabase.storage.from_(BUCKET_NAME).upload(path, file_bytes, {"content-type": file.content_type})
        # Get public URL
        res = supabase.storage.from_(BUCKET_NAME).get_public_url(path)
        return res
    except Exception as e:
        print(f"Upload error: {e}")
        return None
"""
content = re.sub(r'def save_upload\(.*?return f"/uploads/\{subdir\}/\{filename\}"', new_save_upload, content, flags=re.DOTALL)

# 5. Modify load_data
new_load_data = """
def load_data() -> dict:
    try:
        res = supabase.storage.from_(BUCKET_NAME).download("site_data.json")
        raw = json.loads(res.decode('utf-8'))
    except Exception as e:
        print(f"Load error: {e}")
        data = default_data()
        save_data(data)
        return data

    data = default_data()
    for key in data.keys():
        value = raw.get(key)
        if isinstance(value, list) or isinstance(value, dict):
            data[key] = value
    return data
"""
content = re.sub(r'def load_data\(\) -> dict:.*?return data', new_load_data, content, flags=re.DOTALL)

# 6. Modify save_data
new_save_data = """
def save_data(data: dict | None = None) -> None:
    payload = data or {
        "notices": notices,
        "documents": documents,
        "partners": partners,
        "meetings": meetings,
        "regulations": regulations,
        "suggestions": suggestions,
        "home_content": home_content,
        "council_members": council_members,
    }
    try:
        json_str = json.dumps(payload, ensure_ascii=False, indent=2)
        # remove old first, since supabase upload doesn't overwrite by default unless upsert=True, python client might need upsert
        supabase.storage.from_(BUCKET_NAME).remove(["site_data.json"])
        supabase.storage.from_(BUCKET_NAME).upload("site_data.json", json_str.encode('utf-8'), {"content-type": "application/json"})
    except Exception as e:
        print(f"Save error: {e}")
"""
content = re.sub(r'def save_data\(data: dict \| None = None\) -> None:.*?json\.dump\(payload, f, ensure_ascii=False, indent=2\)', new_save_data, content, flags=re.DOTALL)

# 7. Modify delete_uploaded_file
new_delete_file = """
def delete_uploaded_file(file_url: str | None) -> None:
    if not file_url:
        return
    
    # Extract path from public URL
    # URL format: https://kwwokwoyqygbcrcsyyob.supabase.co/storage/v1/object/public/kookmin/notices/filename.png
    prefix = f"/storage/v1/object/public/{BUCKET_NAME}/"
    if prefix in file_url:
        path = file_url.split(prefix)[-1]
        try:
            supabase.storage.from_(BUCKET_NAME).remove([path])
        except Exception as e:
            print(f"Delete error: {e}")
"""
content = re.sub(r'def delete_uploaded_file\(file_url: str \| None\) -> None:.*?os\.remove\(absolute_path\)', new_delete_file, content, flags=re.DOTALL)

# Also ensure_dir should be removed or made no-op since there's no local fs
content = content.replace("def ensure_dir(path: str) -> None:\n    os.makedirs(path, exist_ok=True)", "def ensure_dir(path: str) -> None:\n    pass")

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Patched main.py")
