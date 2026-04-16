import hashlib
import html
import json
import os
import re
import shutil
from datetime import datetime, timezone, timedelta

import uvicorn
from supabase import create_client, Client
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware



SUPABASE_URL = os.getenv("SUPABASE_URL", "https://kwwokwoyqygbcrcsyyob.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt3d29rd295cXlnYmNyY3N5eW9iIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTk4ODIyNCwiZXhwIjoyMDkxNTY0MjI0fQ.8eP2BSCzu5AMlamlsi2-2pKmmEPAyD4-ljbwyMk-TSU")
BUCKET_NAME = "kookmin"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "kookmin-art-admin-session-secret-change-me"),
    same_site="lax",
    https_only=False,
)


def ensure_dir(path: str) -> None:
    pass



def safe_filename(filename: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]", "_", filename)
    return f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{cleaned}"



def save_upload(file: UploadFile | None, subdir: str) -> str | None:
    if not file or not file.filename: return None
    path = f"{subdir}/{safe_filename(file.filename)}"
    ctype = file.content_type
    if not ctype or ctype == "application/octet-stream" or ctype == "text/plain":
        import mimetypes
        ctype = mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
    try:
        supabase.storage.from_(BUCKET_NAME).upload(path, file.file.read(), {"content-type": ctype})
        return supabase.storage.from_(BUCKET_NAME).get_public_url(path)
    except: return None





DEFAULT_COUNCIL_MEMBERS = [
    {"division": "영화전공", "group_type": "학생회", "role": "학생회장", "name": "미정", "email": ""},
    {"division": "영화전공", "group_type": "학생회", "role": "부학생회장", "name": "미정", "email": ""},
    {"division": "연극전공", "group_type": "학생회", "role": "학생회장", "name": "미정", "email": ""},
    {"division": "연극전공", "group_type": "학생회", "role": "부학생회장", "name": "미정", "email": ""},
    {"division": "무용전공", "group_type": "학생회", "role": "학생회장", "name": "미정", "email": ""},
    {"division": "무용전공", "group_type": "학생회", "role": "부학생회장", "name": "미정", "email": ""},
    {"division": "회화전공", "group_type": "학생회", "role": "학생회장", "name": "미정", "email": ""},
    {"division": "회화전공", "group_type": "학생회", "role": "부학생회장", "name": "미정", "email": ""},
    {"division": "입체미술전공", "group_type": "학생회", "role": "학생회장", "name": "미정", "email": ""},
    {"division": "입체미술전공", "group_type": "학생회", "role": "부학생회장", "name": "미정", "email": ""},
    {"division": "관현악전공", "group_type": "학생회", "role": "학생회장", "name": "미정", "email": ""},
    {"division": "관현악전공", "group_type": "학생회", "role": "부학생회장", "name": "미정", "email": ""},
    {"division": "피아노전공", "group_type": "학생회", "role": "학생회장", "name": "미정", "email": ""},
    {"division": "피아노전공", "group_type": "학생회", "role": "부학생회장", "name": "미정", "email": ""},
    {"division": "작곡전공", "group_type": "학생회", "role": "학생회장", "name": "미정", "email": ""},
    {"division": "작곡전공", "group_type": "학생회", "role": "부학생회장", "name": "미정", "email": ""},
    {"division": "성악전공", "group_type": "학생회", "role": "학생회장", "name": "미정", "email": ""},
    {"division": "성악전공", "group_type": "학생회", "role": "부학생회장", "name": "미정", "email": ""},
]

ARTS_EXECUTIVE_GROUPS = {
    "비대위원장단": [
        {"role": "비대위원장", "name": "미정"},
        {"role": "부비대위원장", "name": "미정"},
    ],
    "연합기획국": [
        {"role": "국장", "name": "미정"},
        {"role": "국원", "name": "미정"},
        {"role": "국원", "name": "미정"},
    ],
    "홍보국": [
        {"role": "국장", "name": "미정"},
        {"role": "국원", "name": "미정"},
        {"role": "국원", "name": "미정"},
    ],
    "행정사무국": [
        {"role": "국장", "name": "미정"},
        {"role": "국원", "name": "미정"},
    ],
    "복지소통국": [
        {"role": "국장", "name": "미정"},
        {"role": "국원", "name": "미정"},
    ],
}

# 홈 화면 콘텐츠 기본값
HOME_CONTENT_DEFAULTS = {
    "hero_title": "국민대학교 예술대학 학생들을 위한 통합 안내 포털입니다.",
    "hero_description": "학우 여러분이 학교생활에 필요한 공지사항, 문서 양식, 회의 결과 등을 한곳에서 쉽고 빠르게 확인할 수 있습니다.",
    "office_status_title": "학생회실 재실 여부",
    "office_status_value": "부재중",
    "office_status_meta": "매주 평일 09:00–16:00",
    "vision_title": "예술대학 학생회",
    "vision_description": "학우 여러분의 원활한 학교생활과 다양한 전공 간의 교류를 위해 학생회가 함께합니다.",
    "main_notice_description": "전체학생대표자회의 소집, 주요 일정 공지, 학생회 전달사항처럼 먼저 확인해야 하는 공지를 모아보는 영역입니다.",
}


def default_data() -> dict:
    return {
        "notices": [],
        "documents": [],
        "partners": [],
        "meetings": [],
        "regulations": [],
        "suggestions": [],
        "home_content": dict(HOME_CONTENT_DEFAULTS),
        "council_members": [dict(member) for member in DEFAULT_COUNCIL_MEMBERS],
        "arts_executive_groups": dict(ARTS_EXECUTIVE_GROUPS),
        "arts_council_type": "학생회",
    }


def load_data() -> dict:
    try:
        raw = json.loads(supabase.storage.from_(BUCKET_NAME).download("site_data.json").decode('utf-8'))
    except:
        raw = {}
    data = default_data()
    for k in data.keys():
        if raw.get(k) is not None: data[k] = raw[k]
    return data

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (json.JSONDecodeError, OSError):
        raw = {}

    data = default_data()
    for key in data.keys():
        value = raw.get(key)
        if isinstance(value, list):
            data[key] = value
    return data


def save_data(data: dict | None = None) -> None:
    p = data or {"notices": notices, "documents": documents, "partners": partners, "meetings": meetings, "regulations": regulations, "suggestions": suggestions, "home_content": home_content, "council_members": council_members, "arts_executive_groups": arts_executive_groups, "arts_council_type": arts_council_type}
    try:
        supabase.storage.from_(BUCKET_NAME).remove(["site_data.json"])
        supabase.storage.from_(BUCKET_NAME).upload("site_data.json", json.dumps(p, ensure_ascii=False, indent=2).encode('utf-8'), {"content-type": "application/json"})
    except: pass


loaded_data = load_data()
notices = loaded_data["notices"]
documents = loaded_data["documents"]
partners = loaded_data["partners"]
meetings = loaded_data["meetings"]
regulations = loaded_data["regulations"]
suggestions = loaded_data["suggestions"]
council_members = loaded_data["council_members"]
home_content = {**HOME_CONTENT_DEFAULTS, **loaded_data.get("home_content", {})}
arts_executive_groups = loaded_data.get("arts_executive_groups", dict(ARTS_EXECUTIVE_GROUPS))
arts_council_type = loaded_data.get("arts_council_type", "학생회")



def h(value: str | None) -> str:
    return html.escape(value or "")



def get_item(items: list[dict], index: int) -> dict | None:
    if 0 <= index < len(items):
        return items[index]
    return None


def is_admin(request: Request) -> bool:
    return bool(request.session.get("is_admin"))



def get_admin_password_hash() -> str:
    raw_password = os.getenv("ADMIN_PASSWORD", "1234")
    return hashlib.sha256(raw_password.encode("utf-8")).hexdigest()



def verify_admin_password(password: str) -> bool:
    submitted_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return submitted_hash == get_admin_password_hash()



def require_admin(request: Request) -> RedirectResponse | None:
    if is_admin(request):
        return None
    return RedirectResponse("/admin/login", status_code=302)



def render_layout(title: str, body: str) -> HTMLResponse:
    page = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{h(title)}</title>
        <style>
            * {{ box-sizing: border-box; }}
            :root {{
                --bg: #f6f8fb;
                --bg-2: #edf3f8;
                --panel: rgba(255,255,255,0.9);
                --panel-strong: rgba(255,255,255,0.96);
                --text: #12263f;
                --muted: #5d7084;
                --line: rgba(0,79,159,0.12);
                --primary: #004f9f;
                --primary-soft: #0f3f73;
                --accent: #004f9f;
                --accent-2: #f3b13a;
                --accent-3: #a1daf8;
                --accent-4: #18a572;
                --accent-5: #95c13d;
                --accent-6: #f0923a;
                --accent-7: #5d5b5c;
                --shadow: 0 18px 40px rgba(0, 79, 159, 0.1);
                --shadow-soft: 0 8px 24px rgba(0, 79, 159, 0.07);
                --radius-lg: 26px;
            }}
            body {{
                margin: 0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
                color: var(--text);
                background: linear-gradient(180deg, #f8fbfd 0%, #f3f7fb 54%, #eef3f8 100%);
                min-height: 100vh;
            }}
            header {{
                position: sticky;
                top: 0;
                z-index: 20;
                background: linear-gradient(90deg, #004f9f 0%, #2f6fb3 48%, #18a572 100%);
                color: white;
                border-bottom: 1px solid rgba(255,255,255,0.16);
                box-shadow: 0 6px 18px rgba(0,79,159,0.1);
            }}
            .header-inner {{
                max-width: 1180px;
                margin: 0 auto;
                padding: 20px 24px 18px;
            }}
            .brand-row {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 16px;
                flex-wrap: wrap;
            }}
            .brand-label {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 7px 13px;
                border-radius: 999px;
                background: rgba(255,255,255,0.14);
                color: rgba(255,255,255,0.94);
                font-size: 12px;
                
                text-transform: uppercase;
                border: 1px solid rgba(255,255,255,0.16);
                box-shadow: none;
            }}
            header h1 {{ margin: 10px 0 0; font-size: 28px;  font-weight: 750; }}
            .brand-subtitle {{ margin: 8px 0 0; color: rgba(255,255,255,0.72); font-size: 14px; line-height: 1.6; }}
            nav {{
                margin-top: 18px;
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 10px;
            }}
            nav a {{
                color: rgba(255,255,255,0.96);
                text-decoration: none;
                padding: 13px 14px;
                border-radius: 18px;
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.12);
                transition: transform 0.16s ease, background 0.16s ease, border-color 0.16s ease;
                font-size: 14px;
                text-align: center;
            }}
            nav a:hover {{
                background: rgba(255,255,255,0.18);
                border-color: rgba(255,255,255,0.22);
                transform: translateY(-1px);
            }}
            main {{ max-width: 1180px; margin: 0 auto; padding: 28px 24px 56px; }}
            .hero {{
                padding: 40px;
                border-radius: 32px;
                background: linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(244,249,253,0.96) 100%);
                border: 1px solid rgba(0,79,159,0.08);
                box-shadow: var(--shadow);
                margin-bottom: 22px;
                position: relative;
                overflow: hidden;
            }}
            .hero::before {{
                content: "";
                position: absolute;
                inset: 0;
                background: linear-gradient(90deg, rgba(0,79,159,0.05) 0%, transparent 30%, transparent 70%, rgba(24,165,114,0.05) 100%);
                pointer-events: none;
            }}
            .hero-grid {{ display: grid; grid-template-columns: 1.6fr 0.9fr; gap: 18px; align-items: stretch; }}
            .hero-side {{ display: grid; gap: 14px; }}
            .hero h2 {{ font-size: 36px; line-height: 1.08; margin-bottom: 14px;  max-width: 760px; }}
            .hero p {{ max-width: 760px; color: var(--muted); font-size: 16px; line-height: 1.8; }}
            .metric-card {{
                background: linear-gradient(135deg, #004f9f 0%, #2f6fb3 58%, #18a572 100%);
                color: white;
                border-radius: 24px;
                padding: 22px;
                box-shadow: var(--shadow);
                position: relative;
                overflow: hidden;
            }}
            .metric-card::after {{
                content: "";
                position: absolute;
                width: 180px;
                height: 180px;
                right: -50px;
                bottom: -70px;
                background: radial-gradient(circle, rgba(255,255,255,0.18), transparent 68%);
                pointer-events: none;
            }}
            .metric-card h3 {{ margin: 0 0 8px; font-size: 14px; color: rgba(255,255,255,0.7); font-weight: 500; }}
            .metric-value {{ font-size: 34px; font-weight: 700;  margin: 0; }}
            .metric-meta {{ margin-top: 8px; color: rgba(255,255,255,0.7); font-size: 13px; }}
            .card {{
                background: var(--panel-strong);
                border: 1px solid rgba(0,79,159,0.08);
                border-radius: var(--radius-lg);
                padding: 24px;
                margin-bottom: 18px;
                box-shadow: var(--shadow-soft);
                position: relative;
                overflow: hidden;
            }}
            .feature-card {{
                background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(244,248,252,0.96) 100%);
                min-height: 210px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                transition: transform 0.16s ease, box-shadow 0.16s ease, border-color 0.16s ease;
                position: relative;
                overflow: hidden;
                border-top: 4px solid var(--accent);
            }}
            .feature-card:hover {{ transform: translateY(-4px); box-shadow: var(--shadow); border-color: rgba(0,79,159,0.16); }}
            .feature-card::before {{
                content: "";
                position: absolute;
                inset: 0;
                background: linear-gradient(135deg, rgba(161,218,248,0.08), transparent 48%, rgba(243,177,58,0.08));
                pointer-events: none;
            }}
            .directory-grid {{
                display: grid;
                gap: 14px;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            }}
            .member-card {{
                background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(243,247,251,0.96) 100%);
                border: 1px solid rgba(0,79,159,0.08);
                border-radius: 22px;
                padding: 20px;
                box-shadow: var(--shadow-soft);
                transition: transform 0.16s ease, box-shadow 0.16s ease;
                border-top: 4px solid var(--accent-4);
            }}
            .member-card:hover {{
                transform: translateY(-3px);
                box-shadow: 0 14px 28px rgba(0,79,159,0.12);
            }}
            .member-role {{
                color: var(--accent);
                font-size: 12px;
                font-weight: 800;
                
                text-transform: uppercase;
                margin-bottom: 8px;
            }}
            .member-name {{
                font-size: 24px;
                font-weight: 700;
                
                margin: 0 0 6px;
            }}
            .member-division {{
                color: var(--muted);
                margin: 0;
                line-height: 1.5;
            }}
            .member-meta {{
                color: var(--muted);
                margin: 6px 0 0;
                line-height: 1.5;
                font-size: 14px;
            }}
            .council-split {{
                display: grid;
                grid-template-columns: 1fr;
                gap: 18px;
                margin-bottom: 18px;
            }}
            .council-section-anchor {{
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                margin-top: 16px;
            }}
            .council-block {{
                display: grid;
                gap: 14px;
            }}
            .council-block-head {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 12px;
                flex-wrap: wrap;
            }}
            .major-cluster-card {{
                background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(243,247,251,0.96) 100%);
                border: 1px solid rgba(0,79,159,0.08);
                border-radius: 22px;
                padding: 20px;
                box-shadow: var(--shadow-soft);
            }}
            .major-cluster-card h3 {{
                margin: 0 0 8px;
                font-size: 22px;
                
            }}
            .major-cluster-meta {{
                color: var(--muted);
                font-size: 14px;
                margin-bottom: 14px;
            }}
            .major-grid {{
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 12px;
                align-items: start;
            }}
            .major-unit {{
                background: rgba(255,255,255,0.88);
                border: 1px solid rgba(0,79,159,0.07);
                border-radius: 18px;
                padding: 16px;
                display: grid;
                gap: 10px;
            }}
            .major-unit h4 {{
                margin: 0;
                font-size: 18px;
                
            }}
            .major-member-pair {{
                display: grid;
                gap: 8px;
            }}
            .major-member-row {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 10px;
                padding: 10px 12px;
                border-radius: 14px;
                background: rgba(0,79,159,0.04);
                border: 1px solid rgba(0,79,159,0.06);
            }}
            .major-member-role {{
                font-size: 13px;
                font-weight: 800;
                
                color: var(--accent);
                text-transform: uppercase;
            }}
            .major-member-name {{
                font-size: 15px;
                font-weight: 700;
                color: var(--text);
            }}
            .executive-hierarchy {{
                display: grid;
                gap: 18px;
            }}
            .executive-top {{
                background: linear-gradient(135deg, #004f9f 0%, #2f6fb3 100%);
                color: white;
                border-radius: 24px;
                padding: 24px;
                box-shadow: var(--shadow);
                text-align: center;
            }}
            .executive-top h3 {{
                margin: 0 0 8px;
                font-size: 24px;
                
                color: white;
            }}
            .executive-top p {{
                margin: 0;
                color: rgba(255,255,255,0.82);
            }}
            .executive-top-members {{
                display: grid;
                gap: 10px;
                margin-top: 16px;
            }}
            .executive-top-member {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 12px;
                padding: 12px 14px;
                border-radius: 16px;
                background: rgba(255,255,255,0.14);
                border: 1px solid rgba(255,255,255,0.16);
            }}
            .executive-top-role {{
                font-weight: 800;
                color: white;
            }}
            .executive-top-name {{
                font-weight: 700;
                color: rgba(255,255,255,0.92);
            }}
            .executive-branches {{
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 14px;
            }}
            .executive-branch-card {{
                background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(243,247,251,0.96) 100%);
                border: 1px solid rgba(0,79,159,0.08);
                border-radius: 22px;
                padding: 20px;
                box-shadow: var(--shadow-soft);
                display: grid;
                gap: 12px;
            }}
            .executive-branch-head {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 10px;
                flex-wrap: wrap;
            }}
            .executive-branch-head h3 {{
                margin: 0;
                font-size: 20px;
                
            }}
            .executive-member-list {{
                display: grid;
                gap: 10px;
            }}
            .executive-member-row {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 10px;
                padding: 12px 14px;
                border-radius: 16px;
                background: rgba(255,255,255,0.88);
                border: 1px solid rgba(0,79,159,0.06);
            }}
            .executive-member-role {{
                color: var(--accent);
                font-weight: 700;
            }}
            .executive-member-name {{
                font-weight: 700;
                color: var(--text);
            }}
            .inline-form {{
                display: inline;
                margin: 0;
            }}
            .intro-grid {{
                display: grid;
                grid-template-columns: 1.2fr 0.8fr;
                gap: 18px;
                margin-bottom: 22px;
            }}
            h2 {{ margin-top: 0; margin-bottom: 12px;  }}
            h3 {{ margin-top: 0; margin-bottom: 8px;  }}
            p {{ line-height: 1.7; margin-top: 0; }}
            .meta {{ color: var(--muted); font-size: 13px; }}
            .btn {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                padding: 12px 17px;
                border-radius: 999px;
                background: linear-gradient(135deg, var(--primary) 0%, #2f6fb3 100%);
                color: white;
                text-decoration: none;
                border: 1px solid rgba(0,79,159,0.08);
                cursor: pointer;
                transition: transform 0.16s ease, background 0.16s ease;
                font-weight: 650;
            }}
            .btn:hover {{ transform: translateY(-1px); background: linear-gradient(135deg, var(--primary-soft) 0%, #225e9b 100%); }}
            .btn-light {{ background: rgba(255,255,255,0.88); color: var(--text); border: 1px solid rgba(0,79,159,0.12); box-shadow: none; }}
            .btn-light:hover {{ background: rgba(242,248,253,0.96); }}
            form {{ display: grid; gap: 14px; }}
            label {{ display: grid; gap: 8px; font-weight: 600; color: var(--accent); }}
            input, textarea, select {{
                width: 100%;
                padding: 12px 14px;
                border: 1px solid rgba(0,79,159,0.12);
                border-radius: 16px;
                font: inherit;
                background: rgba(255,255,255,0.96);
                color: var(--text);
                outline: none;
                transition: border-color 0.16s ease, box-shadow 0.16s ease, background 0.16s ease;
            }}
            input[type="file"] {{
                padding: 10px 12px;
                background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(243,247,251,0.96) 100%);
                border: 1px dashed rgba(0,79,159,0.18);
                border-radius: 18px;
                cursor: pointer;
            }}
            input[type="file"]::file-selector-button {{
                margin-right: 12px;
                padding: 10px 14px;
                border: 0;
                border-radius: 999px;
                background: linear-gradient(135deg, var(--primary) 0%, #2f6fb3 100%);
                color: white;
                font: inherit;
                font-weight: 700;
                cursor: pointer;
                transition: transform 0.16s ease, opacity 0.16s ease;
            }}
            input[type="file"]::file-selector-button:hover {{
                transform: translateY(-1px);
                opacity: 0.96;
            }}
            input:focus, textarea:focus, select:focus {{ border-color: rgba(0,79,159,0.42); box-shadow: 0 0 0 4px rgba(0,79,159,0.1); background: rgba(255,255,255,0.94); }}
            textarea {{ min-height: 140px; resize: vertical; }}
            .grid {{ display: grid; gap: 18px; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }}
            .pill {{
                display: inline-flex;
                align-items: center;
                padding: 6px 12px;
                border-radius: 999px;
                background: linear-gradient(135deg, rgba(0,79,159,0.08) 0%, rgba(161,218,248,0.16) 100%);
                color: #004f9f;
                font-size: 12px;
                font-weight: 700;
                border: 1px solid rgba(0,79,159,0.08);
            }}
            .actions {{ display: flex; gap: 10px; flex-wrap: wrap; margin-top: 16px; }}
            .empty {{ color: var(--muted); }}
            .section-title {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 8px; }}
            .eyebrow {{ font-size: 12px; text-transform: uppercase;  color: #004f9f; margin-bottom: 10px; font-weight: 800; }}
            .muted {{ color: var(--muted); }}
            .regulation-guide {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 16px;
                margin-bottom: 18px;
            }}
            .guide-card {{
                background: linear-gradient(180deg, rgba(255,255,255,0.9) 0%, rgba(242,247,252,0.82) 100%);
                border: 1px solid rgba(0,79,159,0.08);
                border-radius: 22px;
                padding: 20px;
                box-shadow: var(--shadow-soft);
            }}
            .guide-card h3 {{
                margin-bottom: 10px;
            }}
            .guide-card p {{
                margin: 0;
                color: var(--muted);
            }}
            .guide-card ul {{
                margin: 10px 0 0;
                padding-left: 18px;
                color: var(--muted);
                line-height: 1.65;
            }}
            .color-band {{
                display: grid;
                grid-template-columns: repeat(6, 1fr);
                gap: 0;
                border-radius: 18px;
                overflow: hidden;
                margin-top: 18px;
                box-shadow: var(--shadow-soft);
            }}
            .color-band span {{
                display: block;
                height: 14px;
            }}
            .guide-accordion {{
                display: grid;
                gap: 14px;
                margin-bottom: 18px;
            }}
            .guide-detail {{
                background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(243,247,251,0.96) 100%);
                border: 1px solid rgba(0,79,159,0.08);
                border-radius: 20px;
                box-shadow: var(--shadow-soft);
                overflow: hidden;
            }}
            .guide-detail summary {{
                list-style: none;
                cursor: pointer;
                padding: 18px 20px;
                font-weight: 700;
                color: var(--text);
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 16px;
            }}
            .guide-detail summary::-webkit-details-marker {{
                display: none;
            }}
            .guide-detail summary::after {{
                content: "+";
                font-size: 22px;
                line-height: 1;
                color: var(--accent);
                flex-shrink: 0;
            }}
            .guide-detail[open] summary::after {{
                content: "−";
            }}
            .guide-detail .detail-body {{
                padding: 0 20px 20px;
                color: var(--muted);
                line-height: 1.75;
            }}
            .guide-detail .detail-body ul {{
                margin: 10px 0 0;
                padding-left: 18px;
            }}
            .quick-tags {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin-top: 14px;
            }}
            .quick-tag {{
                display: inline-flex;
                align-items: center;
                padding: 8px 12px;
                border-radius: 999px;
                font-size: 13px;
                font-weight: 700;
                color: var(--text);
                background: rgba(0,79,159,0.06);
                border: 1px solid rgba(0,79,159,0.08);
            }}
            @media (max-width: 900px) {{
                .hero-grid {{ grid-template-columns: 1fr; }}
                .color-band {{ grid-template-columns: repeat(3, 1fr); }}
                .hero {{ padding: 28px 24px; }}
                .hero h2 {{ font-size: 30px; }}
                .intro-grid {{ grid-template-columns: 1fr; }}
                nav {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
                .major-grid {{ grid-template-columns: 1fr; }}
                .executive-branches {{ grid-template-columns: 1fr; }}
            }}
        </style>
    </head>
    <body>
        <header>
            <div class="header-inner">
                <div class="brand-row">
                    <div>
                        <div class="brand-label">Kookmin University · College of Arts</div>
                        <h1>국민대학교 예술대학 학생 포털</h1>
                        <p class="brand-subtitle">학생자치, 행정 문서, 규정, 회의 공고, 제휴 정보, 신문고를 하나의 인터페이스로 통합합니다.</p>
                    </div>
                </div>
                <nav>
                    <a href="/">홈</a>
                    <a href="/archive">통합 자료</a>
                    <a href="/council">대의원 소개</a>
                    <a href="/suggest">신문고</a>
                </nav>
            </div>
        </header>
        <main>
            {body}
        </main>
    </body>
    </html>
    """
    return HTMLResponse(content=page)



def render_home_page() -> HTMLResponse:
    notice_cards = "".join(f'<div class="member-card"><div class="member-role">{h(n.get("category"))}</div><p class="member-name" style="font-size:18px;">{h(n.get("title"))}</p><p class="member-meta">{h(n.get("created_at"))}</p></div>' for n in notices[:3])
    if not notice_cards: notice_cards = '<div class="card empty">등록된 최근 공지사항이 없습니다.</div>'
    
    # Auto-calculate office status (KST: Weekdays 09:00~18:00 -> "재실중")
    kst = datetime.now(timezone(timedelta(hours=9)))
    is_working_hours = (kst.weekday() < 5) and (9 <= kst.hour < 18)
    
    office_val = "재실중" if is_working_hours else home_content.get("office_status_value", "부재중")
    
    body = f'''
    <div class="hero-grid">
        <section class="hero">
            <div class="eyebrow">Kookmin Univ. College of Arts</div>
            <h2>{h(home_content.get("hero_title"))}</h2>
            <p>{h(home_content.get("hero_description"))}</p>
            <div class="quick-tags"><span class="quick-tag">KMU Blue</span><span class="quick-tag">KMU Yellow</span><span class="quick-tag">KMU Sky Blue</span><span class="quick-tag">KMU Green</span><span class="quick-tag">KMU Orange</span><span class="quick-tag">KMU Gray</span></div>
            <div class="color-band"><span style="background:#004f9f"></span><span style="background:#f3c53d"></span><span style="background:#f0923a"></span><span style="background:#a1daf8"></span><span style="background:#95c13d"></span><span style="background:#18a572"></span></div>
            <div class="actions"><a class="btn" href="/notices">공지사항 보기</a><a class="btn btn-light" href="/archive">통합 자료 보기</a></div>
        </section>
        <div class="hero-side">
            <div class="metric-card"><h3>{h(home_content.get("office_status_title"))}</h3><p class="metric-value">{h(office_val)}</p><div class="metric-meta">{h(home_content.get("office_status_meta"))}</div></div>
            <div class="card"><div class="eyebrow">Vision</div><h3>{h(home_content.get("vision_title"))}</h3><p class="muted">{h(home_content.get("vision_description"))}</p></div>
        </div>
    </div>
    <div class="intro-grid">
        <section class="card">
            <div class="section-title"><div><div class="eyebrow">Recent Notices</div><h2>최근 공지사항</h2></div><a class="btn btn-light" href="/notices">전체 공지</a></div>
            <p class="muted">가장 최근에 올라온 공지사항을 빠르게 확인하세요.</p>
            <div class="directory-grid">{notice_cards}</div>
        </section>
        <section class="card"><div class="eyebrow">Platform Focus</div><h2>이 포털이 우선하는 것</h2><p class="muted">자주 쓰는 기능을 빠르게 찾을 수 있도록 메뉴를 간소화했습니다.</p></section>
    </div>
    <div class="grid">
        <div class="card feature-card"><div><div class="eyebrow">Archive</div><h2>통합 자료</h2><p class="muted">공지사항, 문서자료실, 제휴업체, 회의 공고, 규정을 확인할 수 있습니다.</p></div><a class="btn" href="/archive">열기</a></div>
        <div class="card feature-card"><div><div class="eyebrow">Council</div><h2>대의원 소개</h2><p class="muted">예술대학 학생회 및 전공별 대표자 명단을 확인합니다.</p></div><a class="btn" href="/council">열기</a></div>
        <div class="card feature-card"><div><div class="eyebrow">Voice</div><h2>신문고</h2><p class="muted">건의사항이나 문의를 남길 수 있습니다.</p></div><a class="btn" href="/suggest">열기</a></div>
        <div class="card feature-card"><div><div class="eyebrow">Admin</div><h2>관리자</h2><p class="muted">운영자 전용 페이지입니다.</p></div><a class="btn" href="/admin/login">열기</a></div>
    </div>'''
    return render_layout("국민대학교 예술대학 학생 포털", body)
def render_archive_page() -> HTMLResponse:
    archive_sections = [
        ("공지사항", "학생 대상 공지와 전달 사항을 확인합니다.", "/notices"),
        ("문서자료실", "행정 문서와 양식을 내려받습니다.", "/documents"),
        ("제휴업체", "제휴 정보와 혜택을 확인합니다.", "/partners"),
        ("대표자회의", "소집 공고와 안건을 확인합니다.", "/meetings"),
        ("규정", "현행 규정과 개정 공고를 열람합니다.", "/regulations"),
    ]
    cards = "".join(
        f'''
        <div class="card feature-card">
            <div>
                <div class="eyebrow">Archive Section</div>
                <h2>{h(title)}</h2>
                <p class="muted">{h(description)}</p>
            </div>
            <a class="btn" href="{link}">열기</a>
        </div>
        '''
        for title, description, link in archive_sections
    )
    body = f"""
    <div class="hero">
        <div class="eyebrow">Integrated Archive</div>
        <h2>학생회 관련 자료를 한곳에서 확인할 수 있는 통합 자료 페이지입니다.</h2>
        <p>공지사항, 문서자료실, 제휴업체, 회의 공고, 규정처럼 자주 확인하는 자료를 이 페이지에서 한 번에 찾아볼 수 있습니다.</p>
    </div>
    <div class="grid">
        {cards}
    </div>
    """
    return render_layout("통합 자료", body)


def render_council_page(request: Request) -> HTMLResponse:
    is_adm = is_admin(request)
    def s_exec(m_list):
        return sorted(m_list, key=lambda m: 0 if "장" in m.get("role","") and "부" not in m.get("role","") else 1 if "부" in m.get("role","") and "장" in m.get("role","") else 2)
    
    

    desc_map = {
        "연합기획국": "교내 교류 활성화 및 행사, 행정을 기획하고 활동하는 부서입니다.",
        "홍보국": "학생회 활동을 홍보하고 학생들이 참여할 수 있는 행사, 복지 등을 안내하는 부서입니다.",
        "행정사무국": "예산 처리 및 기획안 작성 등 문서 업무를 담당하고 아이디어를 실제화하기 위해 노력하는 부서입니다.",
        "복지소통국": "복지 상태를 점검하고 필요한 복지를 기획·검토하며, 학생들과 적극적으로 소통하여 의견을 수렴하는 부서입니다."
    }

    branch_cards = []
    for k, v in arts_executive_groups.items():
        if k == "비대위원장단": continue
        rws = "".join(f'<div class="executive-member-row"><div style="display:flex; flex-direction:column; gap:4px;"><div style="display:flex; align-items:center; gap:8px;"><span class="executive-member-role">{h(m.get("role"))}</span><span class="executive-member-name">{h(m.get("name"))}</span></div><span style="font-size:13px; color:var(--muted);">{h(m.get("email")) or ""}</span></div></div>' for m in s_exec(v))
        desc_html = f'<p class="muted" style="margin-bottom:12px; font-size:14px; line-height:1.6;">{desc_map.get(k, "")}</p>' if k in desc_map else ""
        branch_cards.append(f'<details name="arts-branch" class="guide-detail" style="margin-bottom: 12px;"><summary style="font-size:16px; padding:16px;">{h(k)}</summary><div class="detail-body" style="padding-top:0px;">{desc_html}<div class="executive-member-list">{rws}</div></div></details>')
    
    ldr = "".join(f'<div class="executive-top-member"><div style="display:flex; flex-direction:column; gap:4px; text-align:left;"><div style="display:flex; align-items:center; gap:8px;"><span class="executive-top-role">{h(m.get("role"))}</span><span class="executive-top-name">{h(m.get("name"))}</span></div><span style="font-size:13px; color:rgba(255,255,255,0.7);">{h(m.get("email")) or ""}</span></div></div>' for m in s_exec(arts_executive_groups.get("비대위원장단", [])))
    
    major_clusters = [("공연예술학부", ["영화전공", "연극전공", "무용전공"]),("미술학부", ["회화전공", "입체미술전공"]),("음악학부", ["관현악전공", "피아노전공", "성악전공", "작곡전공"])]
    cluster_cards = []
    for c_name, divs in major_clusters:
        m_units = []
        for d in divs:
            mems = [(i, m) for i, m in enumerate(council_members) if m.get("division") == d]
            if not mems: continue
            rws = "".join(f'<div class="major-member-row" style="align-items:flex-start;"><div><div style="font-size:13px; color:var(--muted); margin-bottom:4px;">{h(m.get("role"))}</div><div style="font-size:20px; font-weight:800; margin-bottom:4px; color:var(--text);">{h(m.get("name"))}</div><div style="font-size:13px; color:var(--muted);">{h(m.get("email")) or ""}</div></div>{"<a class=\"btn btn-light\" style=\"align-self:center;\" href=\"/council/"+str(i)+"/edit\">수정</a>" if is_adm else ""}</div>' for i, m in mems)
            m_units.append(f'<section class="major-unit"><h4>{h(d)}</h4><div class="major-member-pair">{rws}</div></section>')
        cluster_cards.append(f'<div style="margin-bottom: 24px;"><h4 style="font-size:18px; font-weight:700; margin-bottom:12px;">{h(c_name)} <span style="font-size:14px; font-weight:normal; color:var(--muted);">({", ".join(divs)})</span></h4><div class="major-grid">{"".join(m_units) if m_units else "<div class=\"card empty\">없음</div>"}</div></div>')
    
    body = f'''
    <style>
        .exec-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 14px;
        }}
        @media (max-width: 768px) {{
            .exec-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
    <div class="hero">
        <div class="eyebrow">Council Directory</div>
        <h2>예술대학 {arts_council_type} 및 대표자 안내</h2>
        <p>학우 여러분을 위해 일하는 예술대학 {arts_council_type}와 각 전공 대표자 명단입니다.</p>
        <div class="council-section-anchor">
            <a class="btn btn-light" href="#arts-executive">{arts_council_type} 명단</a>
            <a class="btn btn-light" href="#council-members">대표자 명단</a>
            {"<a class=\"btn\" href=\"/council/new\">전공 대표자 추가</a>" if is_adm else ""}
            {"<a class=\"btn btn-light\" href=\"/admin/arts-council\">예대 명단 관리</a>" if is_adm else ""}
        </div>
    </div>
    
    <section id="arts-executive" class="council-block" style="margin-top:18px;">
        <details class="guide-detail" open>
            <summary style="font-size:22px; font-weight:800; padding:20px;">
                <div style="display:flex; flex-direction:column; gap:4px; align-items:flex-start;">
                    <span class="eyebrow" style="font-size:12px;">Arts Student Council</span>
                    <span>예술대학 {arts_council_type}</span>
                </div>
            </summary>
            <div class="detail-body">
                <p class="muted" style="margin-bottom:20px;">예술대학 소속 학생들을 위해 행정, 기획, 소통을 담당하는 명단입니다.</p>
                <div class="executive-hierarchy">
                    <section class="executive-top" style="margin-bottom:16px;">
                        <h3>비대위원장단</h3>
                        <p>예술대학 학생 자치를 총괄합니다.</p>
                        <div class="executive-top-members">{ldr}</div>
                    </section>
                    <div class="exec-grid" style="margin-top:24px;">{"".join(branch_cards)}</div>
                </div>
            </div>
        </details>
    </section>
    
    <section id="council-members" class="council-block" style="margin-top:24px;">
        <details class="guide-detail" open>
            <summary style="font-size:22px; font-weight:800; padding:20px;">
                <div style="display:flex; flex-direction:column; gap:4px; align-items:flex-start;">
                    <span class="eyebrow" style="font-size:12px;">Representative List</span>
                    <span>전공별 대표자</span>
                </div>
            </summary>
            <div class="detail-body">
                <p class="muted" style="margin-bottom:20px;">각 전공을 대표하여 의견을 조율하고 활동하는 대표자 명단입니다.</p>
                <div class="guide-accordion">{"".join(cluster_cards)}</div>
            </div>
        </details>
    </section>'''
    return render_layout("대의원 소개", body)

def render_council_form_page(member: dict | None = None, index: int | None = None) -> HTMLResponse:
    member = member or {}
    action = "/council/new" if index is None else f"/council/{index}/edit"
    heading = "대표자 추가" if index is None else "대표자 수정"
    submit_label = "추가" if index is None else "수정 저장"

    body = f"""
    <div class="card">
        <div class="section-title">
            <h2>{heading}</h2>
            <a class="btn btn-light" href="/council">목록으로</a>
        </div>
        <form action="{action}" method="post">
            <label>전공
                <select name="division">
                    <option value="영화전공" {'selected' if member.get('division') == '영화전공' else ''}>영화전공</option>
                    <option value="연극전공" {'selected' if member.get('division') == '연극전공' else ''}>연극전공</option>
                    <option value="무용전공" {'selected' if member.get('division') == '무용전공' else ''}>무용전공</option>
                    <option value="회화전공" {'selected' if member.get('division') == '회화전공' else ''}>회화전공</option>
                    <option value="입체미술전공" {'selected' if member.get('division') == '입체미술전공' else ''}>입체미술전공</option>
                    <option value="관현악전공" {'selected' if member.get('division') == '관현악전공' else ''}>관현악전공</option>
                    <option value="피아노전공" {'selected' if member.get('division') == '피아노전공' else ''}>피아노전공</option>
                    <option value="작곡전공" {'selected' if member.get('division') == '작곡전공' else ''}>작곡전공</option>
                    <option value="성악전공" {'selected' if member.get('division') == '성악전공' else ''}>성악전공</option>
                </select>
            </label>
            <label>소속 유형
                <select name="group_type">
                    <option value="학생회" {'selected' if member.get('group_type') == '학생회' else ''}>학생회</option>
                    <option value="비상대책위원회" {'selected' if member.get('group_type') == '비상대책위원회' else ''}>비상대책위원회</option>
                </select>
            </label>
            <label>직책<input type="text" name="role" value="{h(member.get('role'))}" required></label>
            <label>이름<input type="text" name="name" value="{h(member.get('name'))}" required></label>
            <label>이메일<input type="email" name="email" value="{h(member.get('email'))}"></label>
            <div class="actions">
                <button class="btn" type="submit">{submit_label}</button>
            </div>
        </form>
    </div>
    """
    return render_layout(heading, body)


def render_document_edit_form_page(document: dict, index: int) -> HTMLResponse:
    body = f"""
    <div class="card">
        <div class="section-title">
            <h2>문서 수정</h2>
            <a class="btn btn-light" href="/documents">목록으로</a>
        </div>
        <form action="/documents/{index}/edit" method="post" enctype="multipart/form-data">
            <label>문서명<input type="text" name="title" value="{h(document.get('title'))}" required></label>
            <label>카테고리<input type="text" name="category" value="{h(document.get('category'))}"></label>
            <label>설명<textarea name="description">{h(document.get('description'))}</textarea></label>
            <label>새 파일 추가 (기존 파일에 덮어씌움)<input type="file" name="files" multiple="true"></label>
            <p class="muted">파일을 새로 올리지 않으면 기존 첨부파일을 유지합니다.</p>
            <div class="actions">
                <button class="btn" type="submit">수정 저장</button>
            </div>
        </form>
    </div>
    """
    return render_layout("문서 수정", body)


def render_notice_edit_form_page(notice: dict, index: int) -> HTMLResponse:
    body = f"""
    <div class="card">
        <div class="section-title">
            <h2>공지 수정</h2>
            <a class="btn btn-light" href="/notices">목록으로</a>
        </div>
        <form action="/notices/{index}/edit" method="post" enctype="multipart/form-data">
            <label>제목<input type="text" name="title" value="{h(notice.get('title'))}" required></label>
            <label>카테고리
                <select name="category">
                    <option value="일반" {'selected' if notice.get('category') == '일반' else ''}>일반</option>
                    <option value="학사" {'selected' if notice.get('category') == '학사' else ''}>학사</option>
                    <option value="행정" {'selected' if notice.get('category') == '행정' else ''}>행정</option>
                    <option value="행사" {'selected' if notice.get('category') == '행사' else ''}>행사</option>
                </select>
            </label>
            <label>내용<textarea name="content" required>{h(notice.get('content'))}</textarea></label>
            <label>새 파일 추가 (기존 파일 덮어씌움, 여러 개 선택 가능)<input type="file" name="files" multiple="true"></label>
            <p class="muted">파일을 새로 올리지 않으면 기존 첨부파일을 유지합니다.</p>
            <div class="actions">
                <button class="btn" type="submit">수정 저장</button>
            </div>
        </form>
    </div>
    """
    return render_layout("공지 수정", body)


def render_partner_edit_form_page(partner: dict, index: int) -> HTMLResponse:
    body = f"""
    <div class="card">
        <div class="section-title">
            <h2>제휴 수정</h2>
            <a class="btn btn-light" href="/partners">목록으로</a>
        </div>
        <form action="/partners/{index}/edit" method="post">
            <label>업체명<input type="text" name="name" value="{h(partner.get('name'))}" required></label>
            <label>카테고리<input type="text" name="category" value="{h(partner.get('category'))}"></label>
            <label>혜택 내용<textarea name="benefit" required>{h(partner.get('benefit'))}</textarea></label>
            <label>이용 조건<textarea name="condition">{h(partner.get('condition'))}</textarea></label>
            <label>연락처<input type="text" name="contact" value="{h(partner.get('contact'))}"></label>
            <label>링크<input type="text" name="link" value="{h(partner.get('link'))}"></label>
            <label>유효 기간<input type="text" name="valid_until" value="{h(partner.get('valid_until'))}"></label>
            <div class="actions">
                <button class="btn" type="submit">수정 저장</button>
            </div>
        </form>
    </div>
    """
    return render_layout("제휴 수정", body)



def render_notices_page(request: Request) -> HTMLResponse:
    items = []
    admin_actions = '<a class="btn" href="/notices/new">공지 작성</a>' if is_admin(request) else ''
    for idx, n in enumerate(notices):
        file_html = f'<a class="btn" href="{h(n.get("file"))}">첨부파일 열기</a>' if n.get("file") else ""
        manage_html = f'''
                <a class="btn btn-light" href="/notices/{idx}/edit">수정</a>
                <form class="inline-form" action="/notices/{idx}/delete" method="post">
                    <button class="btn btn-light" type="submit">삭제</button>
                </form>
        ''' if is_admin(request) else ''
        items.append(f"""
        <div class="card">
            <div class="section-title">
                <h2>{h(n.get('title'))}</h2>
                <span class="pill">{h(n.get('category'))}</span>
            </div>
            <p>{h(n.get('content'))}</p>
            <div class="meta">작성일 {h(n.get('created_at'))}</div>
            <div class="actions">
                {file_html}
                {manage_html}
            </div>
        </div>
        """)
    if not items:
        items.append('<div class="card empty">등록된 공지사항이 없습니다.</div>')
    body = f"""
    <div class="card">
        <div class="section-title">
            <h2>공지사항</h2>
            {admin_actions}
        </div>
    </div>
    {''.join(items)}
    """
    return render_layout("공지사항", body)



def render_notice_form_page() -> HTMLResponse:
    body = """
    <div class="card">
        <h2>공지 작성</h2>
        <form action="/notices/new" method="post" enctype="multipart/form-data">
            <label>제목<input type="text" name="title" required></label>
            <label>카테고리
                <select name="category">
                    <option value="일반">일반</option>
                    <option value="학사">학사</option>
                    <option value="행정">행정</option>
                    <option value="행사">행사</option>
                </select>
            </label>
            <label>내용<textarea name="content" required></textarea></label>
            <label>첨부파일 (여러 개 선택 가능, PDF/HWP/DOCX 등)<input type="file" name="files" multiple="true"></label>
            <button class="btn" type="submit">등록</button>
        </form>
    </div>
    """
    return render_layout("공지 작성", body)



def render_documents_page(request: Request) -> HTMLResponse:
    is_adm = is_admin(request)
    items = []
    for idx, d in enumerate(documents):
        dns = []
        if d.get("files"):
            for i, f_url in enumerate(d["files"]):
                dns.append(f'<a class="btn" href="{h(f_url)}">첨부파일 {i+1} 다운로드</a>')
        elif d.get("file"):
            dns.append(f'<a class="btn" href="{h(d.get("file"))}">다운로드</a>')
        dn = "".join(dns)
        mg = f'<a class="btn btn-light" href="/documents/{idx}/edit">수정</a><form class="inline-form" action="/documents/{idx}/delete" method="post"><button class="btn btn-light" type="submit">삭제</button></form>' if is_adm else ''
        items.append(f'<div class="card"><div class="section-title"><h2>{h(d.get("title"))}</h2><span class="pill">{h(d.get("category"))}</span></div><p>{h(d.get("description"))}</p><div class="meta">등록일 {h(d.get("created_at"))}</div><div class="actions">{dn}{mg}</div></div>')
    body = f'''<div class="hero"><div class="eyebrow">Document Archive</div><h2>문서자료실</h2><p>학우 여러분이 학교생활이나 행정 처리 중 필요한 문서 양식을 내려받을 수 있는 공간입니다.</p><div class="actions">{"<a class=\"btn\" href=\"/documents/new\">문서 업로드</a>" if is_adm else ""}</div></div>{"".join(items) if items else "<div class=\"card empty\">없음</div>"}'''
    return render_layout("문서자료실", body)
def render_document_form_page() -> HTMLResponse:
    body = """
    <div class="card">
        <h2>문서 업로드</h2>
        <form action="/documents/new" method="post" enctype="multipart/form-data">
            <label>문서명<input type="text" name="title" required></label>
            <label>카테고리<input type="text" name="category" value="행정서식"></label>
            <label>설명<textarea name="description"></textarea></label>
            <label>파일 (여러 개 선택 가능)<input type="file" name="files" multiple="true" required></label>
            <button class="btn" type="submit">업로드</button>
        </form>
    </div>
    """
    return render_layout("문서 업로드", body)


def delete_uploaded_file(file_url: str | None) -> None:
    if not file_url: return
    prefix = f"/storage/v1/object/public/{BUCKET_NAME}/"
    if prefix in file_url:
        try: supabase.storage.from_(BUCKET_NAME).remove([file_url.split(prefix)[-1]])
        except: pass


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "kookmin-art-portal"}


@app.get("/council/new", response_class=HTMLResponse)
async def council_new_form(request: Request):
    return render_council_form_page()


@app.post("/council/new")
async def create_council_member(request: Request, 
    division: str = Form(...),
    group_type: str = Form(...),
    role: str = Form(...),
    name: str = Form(...),
    email: str = Form(""),
):
    if require_admin(request): return require_admin(request)
    council_members.append({
        "division": division,
        "group_type": group_type,
        "role": role,
        "name": name,
        "email": email,
    })
    save_data()
    return RedirectResponse("/council", status_code=302)


@app.get("/council/{member_index}/edit", response_class=HTMLResponse)
async def council_edit_form(request: Request, member_index: int):
    member = get_item(council_members, member_index)
    if member is None:
        return render_layout("대표자 수정", '<div class="card empty">존재하지 않는 대표자입니다.</div>')
    return render_council_form_page(member, member_index)


@app.post("/council/{member_index}/edit")
async def update_council_member(request: Request, 
    member_index: int,
    division: str = Form(...),
    group_type: str = Form(...),
    role: str = Form(...),
    name: str = Form(...),
    email: str = Form(""),
):
    if require_admin(request): return require_admin(request)
    member = get_item(council_members, member_index)
    if member is not None:
        member.update({
            "division": division,
            "group_type": group_type,
            "role": role,
            "name": name,
            "email": email,
        })
        save_data()
    return RedirectResponse("/council", status_code=302)



def render_partners_page(request: Request) -> HTMLResponse:
    is_adm = is_admin(request)
    items = []
    for idx, p in enumerate(partners):
        img_src = p.get('image') or "https://via.placeholder.com/400x300?text=No+Image"
        map_html = f'<a class="btn btn-light" style="margin-top:10px; width:100%;" href="{h(p.get("map_link"))}" target="_blank">네이버 지도 보기</a>' if p.get("map_link") else ""
        mg = f'<div style="margin-top:10px; display:flex; gap:10px;"><a class="btn btn-light" href="/partners/{idx}/edit">수정</a><form class="inline-form" action="/partners/{idx}/delete" method="post"><button class="btn btn-light" type="submit">삭제</button></form></div>' if is_adm else ''
        items.append(f'''<details class="guide-detail partner-card" style="margin-bottom:0; display:flex; flex-direction:column; height:100%;"><summary style="padding:0; flex-direction:column; align-items:flex-start; text-align:left; border-bottom:none;"><div style="width:100%; aspect-ratio:4/3; background:url('{img_src}') center/cover no-repeat;"></div><div style="padding:16px;"><div class="eyebrow">{h(p.get("category"))}</div><h3 style="margin:0; font-size:18px;">{h(p.get("name"))}</h3></div></summary><div class="detail-body" style="border-top:1px solid var(--line); padding-top:16px;"><p><strong>혜택:</strong><br>{h(p.get("benefit")).replace(chr(10), "<br>")}</p><p><strong>주소:</strong> {h(p.get("address"))}</p><p><strong>이용 조건:</strong> {h(p.get("condition"))}</p>{map_html}{mg}</div></details>''')
    body = f'''<style>.partner-grid{{display:grid; grid-template-columns:repeat(4,1fr); gap:16px;}} .partner-card summary::after{{display:none;}} @media(max-width:1024px){{.partner-grid{{grid-template-columns:repeat(3,1fr);}}}} @media(max-width:768px){{.partner-grid{{grid-template-columns:repeat(2,1fr);}}}} @media(max-width:480px){{.partner-grid{{grid-template-columns:1fr;}}}}</style><div class="hero"><div class="eyebrow">Partnerships</div><h2>제휴업체</h2><p>예술대학 학우분들을 위해 맺어진 제휴 혜택입니다. 장소를 클릭해 자세한 혜택과 위치를 확인하세요.</p><div class="actions">{"<a class=\"btn\" href=\"/partners/new\">제휴 등록</a>" if is_adm else ""}</div></div><div class="partner-grid">{"".join(items)}</div>{"<div class=\"card empty\">없음</div>" if not items else ""}'''
    return render_layout("제휴업체", body)

def render_partner_form_page() -> HTMLResponse:
    body = '''<div class="card"><h2>제휴업체 등록</h2><form action="/partners/new" method="post" enctype="multipart/form-data"><label>업체명<input type="text" name="name" required></label><label>카테고리<input type="text" name="category" value="기타"></label><label>대표 사진<input type="file" name="image" accept="image/*"></label><label>혜택 내용<textarea name="benefit" required></textarea></label><label>주소<input type="text" name="address"></label><label>네이버 지도 링크<input type="text" name="map_link"></label><label>이용 조건<textarea name="condition"></textarea></label><button class="btn" type="submit">등록</button></form></div>'''
    return render_layout("제휴업체 등록", body)

def render_partner_edit_form_page(partner: dict, index: int) -> HTMLResponse:
    body = f'''<div class="card"><div class="section-title"><h2>제휴 수정</h2><a class="btn btn-light" href="/partners">목록으로</a></div><form action="/partners/{index}/edit" method="post" enctype="multipart/form-data"><label>업체명<input type="text" name="name" value="{h(partner.get("name"))}" required></label><label>카테고리<input type="text" name="category" value="{h(partner.get("category"))}"></label><label>새 대표 사진<input type="file" name="image" accept="image/*"></label><label>혜택 내용<textarea name="benefit" required>{h(partner.get("benefit"))}</textarea></label><label>주소<input type="text" name="address" value="{h(partner.get("address"))}"></label><label>네이버 지도 링크<input type="text" name="map_link" value="{h(partner.get("map_link"))}"></label><label>이용 조건<textarea name="condition">{h(partner.get("condition"))}</textarea></label><button class="btn" type="submit">수정 저장</button></form></div>'''
    return render_layout("제휴 수정", body)
def render_meetings_page() -> HTMLResponse:
    items = []
    for idx, m in enumerate(meetings):
        file_html = f'<a class="btn btn-light" href="{h(m.get("file"))}">첨부파일 열기</a>' if m.get("file") else ""
        items.append(f"""
        <div class="card">
            <h2>{h(m.get('title'))}</h2>
            <p><strong>일시:</strong> {h(m.get('meeting_date'))}</p>
            <p><strong>장소:</strong> {h(m.get('location'))}</p>
            <p><strong>안건:</strong> {h(m.get('agenda'))}</p>
            <p>{h(m.get('content'))}</p>
            <div class="actions">
                {file_html}
                <a class="btn btn-light" href="/meetings/{idx}/edit">수정</a>
                <form class="inline-form" action="/meetings/{idx}/delete" method="post">
                    <button class="btn btn-light" type="submit">삭제</button>
                </form>
            </div>
        </div>
        """)
    if not items:
        items.append('<div class="card empty">등록된 회의 공고가 없습니다.</div>')
    body = f"""
    <div class="card">
        <div class="section-title">
            <h2>대표자회의 소집 공고</h2>
            <a class="btn" href="/meetings/new">회의 공고 작성</a>
        </div>
    </div>
    {''.join(items)}
    """
    return render_layout("대표자회의", body)



def render_meeting_form_page() -> HTMLResponse:
    body = """
    <div class="card">
        <h2>회의 공고 작성</h2>
        <form action="/meetings/new" method="post" enctype="multipart/form-data">
            <label>제목<input type="text" name="title" required></label>
            <label>회의 일시<input type="text" name="meeting_date" required></label>
            <label>장소<input type="text" name="location" required></label>
            <label>안건<textarea name="agenda" required></textarea></label>
            <label>세부 내용<textarea name="content"></textarea></label>
            <label>첨부파일 (여러 개 선택 가능, PDF/HWP/DOCX 등)<input type="file" name="files" multiple="true"></label>
            <button class="btn" type="submit">등록</button>
        </form>
    </div>
    """
    return render_layout("회의 공고 작성", body)


def render_meeting_edit_form_page(meeting: dict, index: int) -> HTMLResponse:
    body = f"""
    <div class="card">
        <div class="section-title">
            <h2>회의 공고 수정</h2>
            <a class="btn btn-light" href="/meetings">목록으로</a>
        </div>
        <form action="/meetings/{index}/edit" method="post" enctype="multipart/form-data">
            <label>제목<input type="text" name="title" value="{h(meeting.get('title'))}" required></label>
            <label>회의 일시<input type="text" name="meeting_date" value="{h(meeting.get('meeting_date'))}" required></label>
            <label>장소<input type="text" name="location" value="{h(meeting.get('location'))}" required></label>
            <label>안건<textarea name="agenda" required>{h(meeting.get('agenda'))}</textarea></label>
            <label>세부 내용<textarea name="content">{h(meeting.get('content'))}</textarea></label>
            <label>새 파일 추가 (기존 파일 덮어씌움, 여러 개 선택 가능)<input type="file" name="files" multiple="true"></label>
            <p class="muted">파일을 새로 올리지 않으면 기존 첨부파일을 유지합니다.</p>
            <div class="actions">
                <button class="btn" type="submit">수정 저장</button>
            </div>
        </form>
    </div>
    """
    return render_layout("회의 공고 수정", body)


def render_regulation_edit_form_page(regulation: dict, index: int) -> HTMLResponse:
    body = f"""
    <div class="card">
        <div class="section-title">
            <h2>규정 수정</h2>
            <a class="btn btn-light" href="/regulations">목록으로</a>
        </div>
        <form action="/regulations/{index}/edit" method="post" enctype="multipart/form-data">
            <label>규정명<input type="text" name="title" value="{h(regulation.get('title'))}" required></label>
            <label>버전<input type="text" name="version" value="{h(regulation.get('version'))}" required></label>
            <label>시행일<input type="text" name="effective_date" value="{h(regulation.get('effective_date'))}" required></label>
            <label>설명<textarea name="description">{h(regulation.get('description'))}</textarea></label>
            <label>새 파일 추가 (기존 파일 덮어씌움, 여러 개 선택 가능)<input type="file" name="files" multiple="true"></label>
            <p class="muted">파일을 새로 올리지 않으면 기존 첨부파일을 유지합니다.</p>
            <div class="actions">
                <button class="btn" type="submit">수정 저장</button>
            </div>
        </form>
    </div>
    """
    return render_layout("규정 수정", body)


def render_regulations_page() -> HTMLResponse:
    items = []
    for idx, r in enumerate(regulations):
        file_html = f'<a class="btn btn-light" href="{h(r.get("file"))}">규정 파일 열기</a>' if r.get("file") else ""
        items.append(f"""
        <div class="card">
            <h2>{h(r.get('title'))}</h2>
            <p><strong>버전:</strong> {h(r.get('version'))}</p>
            <p><strong>시행일:</strong> {h(r.get('effective_date'))}</p>
            <p>{h(r.get('description'))}</p>
            <div class="actions">
                {file_html}
                <a class="btn btn-light" href="/regulations/{idx}/edit">수정</a>
                <form class="inline-form" action="/regulations/{idx}/delete" method="post">
                    <button class="btn btn-light" type="submit">삭제</button>
                </form>
            </div>
        </div>
        """)
    if not items:
        items.append('<div class="card empty">등록된 규정이 없습니다.</div>')
    body = f"""
    <div class="hero">
        <div class="eyebrow">Regulation Guide</div>
        <h2>자주 묻는 학생회 규정과 권리를 확인하세요.</h2>
        <p>어렵게 느껴질 수 있는 학생회 규정을, 학우 여러분의 권리와 궁금증을 중심으로 쉽게 풀었습니다. 필요한 상황에 맞춰 읽어보세요.</p>
        <div class="quick-tags">
            <span class="quick-tag">소집 공고</span>
            <span class="quick-tag">안건 상정</span>
            <span class="quick-tag">학생 권리</span>
            <span class="quick-tag">의결기구 차이</span>
            <span class="quick-tag">비상대책위원회</span>
            <span class="quick-tag">규정 개정</span>
        </div>
    </div>

    <div class="regulation-guide">
        <div class="guide-card">
            <div class="eyebrow">처음 보는 사람용</div>
            <h3>학생사회는 무엇을 하는 곳인가</h3>
            <p>학생사회는 단순히 행사를 만드는 조직이 아니라, 학생들의 의견을 모으고 예산을 심의하며 대표를 선출하고 학생 자치를 운영하는 구조입니다. 규정은 그 구조가 임의적으로 흔들리지 않도록 기준을 세우는 장치입니다.</p>
        </div>
        <div class="guide-card">
            <div class="eyebrow">왜 필요한가</div>
            <h3>규정은 갈등이 생길 때 기준이 된다</h3>
            <p>누가 결정할 수 있는지, 언제 공고해야 하는지, 어떤 안건을 어디에 올려야 하는지 같은 문제가 생길 때 규정이 기준이 됩니다. 규정을 알면 학생회가 자의적으로 움직이는지 아닌지도 판단할 수 있습니다.</p>
        </div>
        <div class="guide-card">
            <div class="eyebrow">어디부터 읽나</div>
            <h3>처음엔 세 가지만 보면 된다</h3>
            <ul>
                <li>학생의 권리와 의무</li>
                <li>학생총회 / 전체학생대표자회의 / 운영위원회의 차이</li>
                <li>선거, 비대위, 규정 개정 절차</li>
            </ul>
        </div>
    </div>

    <div class="guide-accordion">
        <details class="guide-detail" open>
            <summary>전체학생대표자회의를 소집하려면 언제 무엇을 해야 하나</summary>
            <div class="detail-body">
                <p><strong>정기회의</strong>는 매 학기 2회, 개강 후 50일 이내에 소집해야 합니다. 날짜는 개회 전에 운영위원회에서 정하고, 개회일 최소 7일 전에 날짜 공지를 해야 합니다.</p>
                <p><strong>임시회의</strong>는 재적 대의원 3분의 1 이상의 소집 요구가 있거나, 운영위원회가 회의 소집을 결의한 경우 열 수 있습니다.</p>
                <ul>
                    <li>개회 7일 전까지 소집 공고</li>
                    <li>학생회장이 운영위원회 동의를 얻어 개회 3일 전까지 안건 제안</li>
                    <li>학생회칙 개정을 제외한 안건은 대의원 3분의 1 이상 동의로 개회 전까지 상정 가능</li>
                    <li>일반안건은 재적 대의원 과반수 출석 + 출석 인원 과반수 찬성으로 의결</li>
                </ul>
            </div>
        </details>

        <details class="guide-detail">
            <summary>학생의 권리란 무엇이고, 실제로 무엇을 할 수 있나</summary>
            <div class="detail-body">
                <p>정회원은 선거권과 피선거권을 행사할 수 있고, 모든 회원은 학생회 활동 전반에 대해 알 권리를 가집니다. 권리행사가 침해될 경우 저항할 권리, 학생회의 정당한 활동으로 인한 불이익이나 처벌로부터 보호받을 권리, 차별로부터 보호받을 권리도 규정되어 있습니다.</p>
                <ul>
                    <li>학생회 선거에 투표하거나 출마할 수 있음</li>
                    <li>학생회가 무엇을 하는지 자료 공개를 요구할 수 있음</li>
                    <li>정당한 권리행사가 막힐 때 문제를 제기할 수 있음</li>
                    <li>차별이나 부당한 불이익에 대해 보호를 요구할 수 있음</li>
                </ul>
            </div>
        </details>

        <details class="guide-detail">
            <summary>학생의 의무는 무엇인가</summary>
            <div class="detail-body">
                <p>권리만 있는 것이 아니라 학생회칙을 준수하고, 민주적 자치활동에 주체적으로 참여하며, 회비를 납부하고, 타인을 차별하지 않을 의무도 규정되어 있습니다. 즉 학생사회는 몇몇 대표만의 일이 아니라 구성원 전체가 함께 유지하는 구조라는 뜻입니다.</p>
                <ul>
                    <li>학생회칙 준수</li>
                    <li>민주적 자치활동에 참여</li>
                    <li>회비 납부</li>
                    <li>차별 금지</li>
                </ul>
            </div>
        </details>

        <details class="guide-detail">
            <summary>학생총회, 전체학생대표자회의, 운영위원회는 무엇이 다른가</summary>
            <div class="detail-body">
                <p><strong>학생총회</strong>는 전체 회원으로 구성되는 최고 의결기구입니다. 가장 큰 사안을 다루고, 총회를 열기 어려우면 총투표로 대신할 수 있습니다.</p>
                <p><strong>전체학생대표자회의</strong>는 학생총회로부터 권한을 위임받은 대표자 중심의 최고 의결기구입니다. 예산 심의, 사업 심의, 회칙 개정 발의 및 의결 같은 핵심 기능을 맡습니다.</p>
                <p><strong>운영위원회</strong>는 학생총회와 전체학생대표자회의가 열리지 않는 시기에 운영되는 상설 의결기구입니다. 학생회의 제반 사업과 긴급한 사안을 신속하게 다룹니다.</p>
            </div>
        </details>

        <details class="guide-detail">
            <summary>대의원은 누구고, 왜 중요한가</summary>
            <div class="detail-body">
                <p>대의원은 학생사회를 대신해 회의에 출석하고 의결하는 대표자입니다. 예술대학 학생회장단, 각 전공 학생회장단, 비상대책위원장단 등이 대의원에 해당합니다. 중요한 예산과 회칙 개정, 사업 방향이 대의원 표결을 통해 결정되므로 실제 권한이 큰 위치입니다.</p>
                <ul>
                    <li>회의 출석 의무</li>
                    <li>공정하고 적극적으로 참여할 의무</li>
                    <li>회의가 파행되지 않도록 노력할 의무</li>
                </ul>
            </div>
        </details>

        <details class="guide-detail">
            <summary>학생회장단과 집행부는 무슨 차이인가</summary>
            <div class="detail-body">
                <p>학생회장단은 학생사회를 대표하고 집행부 전체를 총괄하는 위치입니다. 반면 집행부는 실제 사업과 사무를 수행하는 실무 조직입니다. 쉽게 말하면 회장단이 방향과 책임을 맡고, 집행부가 사업계획 수립·집행, 예산 관리, 행정 실무를 맡습니다.</p>
            </div>
        </details>

        <details class="guide-detail">
            <summary>선거는 어떻게 이해하면 되나</summary>
            <div class="detail-body">
                <p>규정은 모든 선거를 보통·평등·직접·비밀투표 원칙으로 하도록 정하고 있습니다. 즉 학생사회 대표를 뽑는 과정 역시 공정성과 대표성을 확보하기 위해 별도의 선거시행세칙에 따라 관리됩니다.</p>
                <p>학생 입장에서 중요한 것은, 선거는 단순한 인기투표가 아니라 이후 1년의 예산과 사업, 대표권을 누구에게 맡길지 정하는 절차라는 점입니다.</p>
            </div>
        </details>

        <details class="guide-detail">
            <summary>대표자가 비면 어떻게 되나</summary>
            <div class="detail-body">
                <p>선거 무산이나 학생회장단의 궐위·탄핵 등으로 대표자 공백이 생기면 비상대책위원회가 행정 공백을 막기 위해 운영됩니다. 규정상 비상대책위원회는 운영위원회와 동격의 지위와 권한을 갖습니다.</p>
                <p>즉 비대위는 임시 조직이지만, 단순 대행이 아니라 학생사회가 멈추지 않게 유지하는 장치입니다.</p>
            </div>
        </details>

        <details class="guide-detail">
            <summary>탄핵은 언제 가능한가</summary>
            <div class="detail-body">
                <p>학생회장 또는 부학생회장에 대한 탄핵은 일정 수 이상의 대의원 연서나 회원 연서가 있을 때 발의될 수 있습니다. 이후 운영위원회의 예비의결과 전체학생대표자회의 심의를 거쳐야 하고, 매우 높은 찬성 기준이 필요합니다.</p>
                <ul>
                    <li>회계부정 또는 현저한 부당행위</li>
                    <li>학생사회 목적에 위배되는 행위</li>
                    <li>업무를 방해하는 행위</li>
                </ul>
            </div>
        </details>

        <details class="guide-detail">
            <summary>규정은 어떻게 바뀌나</summary>
            <div class="detail-body">
                <p>규정 개정은 대의원 요구, 운영위원 요구, 의장 단독발의, 회원 100명 이상 연서, 규정개정위원회 발의 등으로 시작될 수 있습니다. 발의 뒤에는 공고 절차를 거치고, 전체학생대표자회의 또는 학생총투표로 개정이 이뤄집니다.</p>
                <p>즉 규정은 고정된 문서가 아니라, 학생사회 내부 합의 절차를 통해 계속 수정될 수 있는 살아 있는 기준입니다.</p>
            </div>
        </details>

        <details class="guide-detail">
            <summary>규정을 읽을 때 학생이 가장 먼저 가져야 할 관점은 무엇인가</summary>
            <div class="detail-body">
                <p>규정을 외워야 한다고 생각할 필요는 없습니다. 대신 아래 질문을 기준으로 보면 훨씬 읽기 쉬워집니다.</p>
                <ul>
                    <li>누가 결정할 수 있는가</li>
                    <li>언제까지 공고해야 하는가</li>
                    <li>어느 회의에서 의결해야 하는가</li>
                    <li>학생 개인이 요구하거나 문제제기할 수 있는 권리는 무엇인가</li>
                </ul>
                <p>이 네 가지를 중심으로 보면 규정은 추상적인 문서가 아니라, 실제 학생사회 운영을 읽는 지도처럼 보이기 시작합니다.</p>
            </div>
        </details>
    </div>

    <div class="card">
        <div class="section-title">
            <h2>규정 및 개정 공고</h2>
            <a class="btn" href="/regulations/new">규정 등록</a>
        </div>
        <p class="muted">원문 규정집은 아래 자료에서 그대로 확인할 수 있습니다. 위 안내는 이해를 돕기 위한 요약이며, 실제 효력은 원문 규정에 따릅니다.</p>
    </div>
    {''.join(items)}
    """
    return render_layout("규정", body)



def render_regulation_form_page() -> HTMLResponse:
    body = """
    <div class="card">
        <h2>규정 등록</h2>
        <form action="/regulations/new" method="post" enctype="multipart/form-data">
            <label>규정명<input type="text" name="title" required></label>
            <label>버전<input type="text" name="version" required></label>
            <label>시행일<input type="text" name="effective_date" required></label>
            <label>설명<textarea name="description"></textarea></label>
            <label>첨부파일 (여러 개 선택 가능, PDF/HWP/DOCX 등)<input type="file" name="files" multiple="true"></label>
            <button class="btn" type="submit">등록</button>
        </form>
    </div>
    """
    return render_layout("규정 등록", body)



def render_suggest_form_page() -> HTMLResponse:
    body = """
    <div class="card">
        <h2>신문고 접수</h2>
        <form action="/suggest" method="post" enctype="multipart/form-data">
            <label>제목<input type="text" name="title" required></label>
            <label>분류
                <select name="category">
                    <option value="건의">건의</option>
                    <option value="민원">민원</option>
                    <option value="신고">신고</option>
                    <option value="기타">기타</option>
                </select>
            </label>
            <label>익명 여부
                <select name="is_anonymous">
                    <option value="Y">익명</option>
                    <option value="N">실명</option>
                </select>
            </label>
            <label>내용<textarea name="content" required></textarea></label>
            <label>첨부파일<input type="file" name="attachment"></label>
            <button class="btn" type="submit">접수</button>
        </form>
    </div>
    """
    return render_layout("신문고", body)


def render_admin_login_page(error_message: str = "") -> HTMLResponse:
    error_html = f'<p class="muted" style="color:#b42318;">{h(error_message)}</p>' if error_message else ''
    body = f"""
    <div class="card" style="max-width:520px; margin:0 auto;">
        <div class="eyebrow">Admin Access</div>
        <h2>관리자 로그인</h2>
        <p class="muted">공지 작성, 수정, 삭제는 관리자만 가능합니다. 일반 사용자는 로그인 없이 공지를 열람할 수 있습니다.</p>
        {error_html}
        <form action="/admin/login" method="post">
            <label>비밀번호<input type="password" name="password" required></label>
            <button class="btn" type="submit">로그인</button>
        </form>
    </div>
    """
    return render_layout("관리자 로그인", body)



def render_admin_dashboard(request: Request) -> HTMLResponse:
    login_state = "로그인 상태" if is_admin(request) else "비로그인 상태"
    logout_button = '<form class="inline-form" action="/admin/logout" method="post"><button class="btn btn-light" type="submit">로그아웃</button></form>' if is_admin(request) else '<a class="btn btn-light" href="/admin/login">로그인</a>'
    status_val = home_content.get("office_status_value", "부재중")
    status_select = f'<form action="/admin/home_status" method="post" style="display:flex; gap:10px; align-items:center;"><select name="status" style="width:auto; padding:8px 12px;"><option value="재실중" {"selected" if status_val=="재실중" else ""}>재실중</option><option value="부재중" {"selected" if status_val=="부재중" else ""}>부재중</option></select><button class="btn" type="submit" style="padding:8px 16px;">상태 변경</button></form>'
    body = f'''<div class="hero"><div class="eyebrow">Admin Overview</div><h2>관리자 대시보드</h2><div class="actions"><span class="pill">{login_state}</span>{logout_button}</div></div><div class="card"><h3>학생회실 재실 상태 관리</h3>{status_select}</div><div class="grid"><div class="metric-card"><h3>공지사항</h3><p class="metric-value">{len(notices)}</p></div><div class="metric-card"><h3>문서자료실</h3><p class="metric-value">{len(documents)}</p></div></div>'''
    return render_layout("관리자", body)
@app.post("/admin/home_status")
async def upd_home(request: Request, status: str = Form(...)):
    home_content["office_status_value"] = status
    save_data()
    return RedirectResponse("/admin", status_code=302)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return render_home_page()


@app.get("/archive", response_class=HTMLResponse)
async def archive_page(request: Request):
    return render_archive_page()


@app.get("/council", response_class=HTMLResponse)
async def council_page(request: Request):
    return render_council_page(request)


@app.get("/notices", response_class=HTMLResponse)
async def notice_list(request: Request):
    return render_notices_page(request)


@app.get("/notices/new", response_class=HTMLResponse)
async def notice_form(request: Request):
    redirect = require_admin(request)
    if redirect:
        return redirect
    return render_notice_form_page()


@app.post("/notices/new")
async def create_notice(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    category: str = Form("일반"),
    file: UploadFile = File(None),
):
    redirect = require_admin(request)
    if redirect:
        return redirect
    file_path = save_upload(file, "notices")

    notices.insert(0, {
        "title": title,
        "content": content,
        "category": category,
        "file": file_path,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    save_data()
    return RedirectResponse("/notices", status_code=302)


@app.get("/notices/{notice_index}/edit", response_class=HTMLResponse)
async def notice_edit_form(request: Request, notice_index: int):
    redirect = require_admin(request)
    if redirect:
        return redirect
    notice = get_item(notices, notice_index)
    if notice is None:
        return render_layout("공지 수정", '<div class="card empty">존재하지 않는 공지입니다.</div>')
    return render_notice_edit_form_page(notice, notice_index)


@app.post("/notices/{notice_index}/edit")
async def update_notice(
    request: Request,
    notice_index: int,
    title: str = Form(...),
    content: str = Form(...),
    category: str = Form("일반"),
    file: UploadFile = File(None),
):
    redirect = require_admin(request)
    if redirect:
        return redirect
    notice = get_item(notices, notice_index)
    if notice is not None:
        if file and file.filename:
            delete_uploaded_file(notice.get("file"))
            notice["file"] = save_upload(file, "notices")
        notice.update({
            "title": title,
            "content": content,
            "category": category,
        })
        save_data()
    return RedirectResponse("/notices", status_code=302)


@app.post("/notices/{notice_index}/delete")
async def delete_notice(request: Request, notice_index: int):
    redirect = require_admin(request)
    if redirect:
        return redirect
    notice = get_item(notices, notice_index)
    if notice is not None:
        delete_uploaded_file(notice.get("file"))
        notices.pop(notice_index)
        save_data()
    return RedirectResponse("/notices", status_code=302)
@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    if is_admin(request):
        return RedirectResponse("/admin", status_code=302)
    return render_admin_login_page()


@app.post("/admin/login")
async def admin_login(request: Request, password: str = Form(...)):
    if verify_admin_password(password):
        request.session["is_admin"] = True
        return RedirectResponse("/admin", status_code=302)
    return render_admin_login_page("비밀번호가 올바르지 않습니다.")


@app.post("/admin/logout")
async def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)



@app.get("/documents", response_class=HTMLResponse)
async def document_list(request: Request):
    return render_documents_page(request)


@app.get("/documents/new", response_class=HTMLResponse)
async def document_form(request: Request):
    return render_document_form_page()


@app.post("/documents/new")
async def create_document(request: Request, 
    title: str = Form(...),
    category: str = Form("행정서식"),
    description: str = Form(""),
    files: list[UploadFile] = File(...),
):
    if require_admin(request): return require_admin(request)
    file_paths = []
    for f in files:
        fp = save_upload(f, "documents")
        if fp: file_paths.append(fp)

    documents.insert(0, {
        "title": title,
        "category": category,
        "description": description,
        "files": file_paths,
        "file": file_paths[0] if file_paths else None,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    save_data()
    return RedirectResponse("/documents", status_code=302)


@app.get("/partners", response_class=HTMLResponse)
async def partner_list(request: Request):
    return render_partners_page(request)


@app.get("/partners/new", response_class=HTMLResponse)
async def partner_form(request: Request):
    return render_partner_form_page()


@app.post("/partners/new")
async def create_partner(request: Request, name: str = Form(...), category: str = Form("기타"), benefit: str = Form(...), address: str = Form(""), map_link: str = Form(""), condition: str = Form(""), image: UploadFile = File(None)):
    partners.insert(0, {"name": name, "category": category, "benefit": benefit, "address": address, "map_link": map_link, "condition": condition, "image": save_upload(image, "partners"), "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")})
    save_data()
    return RedirectResponse("/partners", status_code=302)

@app.get("/partners/{partner_index}/edit", response_class=HTMLResponse)
async def partner_edit_form(request: Request, partner_index: int):
    return render_partner_edit_form_page(partners[partner_index], partner_index)

@app.post("/partners/{partner_index}/edit")
async def update_partner(request: Request, partner_index: int, name: str = Form(...), category: str = Form("기타"), benefit: str = Form(...), address: str = Form(""), map_link: str = Form(""), condition: str = Form(""), image: UploadFile = File(None)):
    if image and image.filename:
        delete_uploaded_file(partners[partner_index].get("image"))
        partners[partner_index]["image"] = save_upload(image, "partners")
    partners[partner_index].update({"name": name, "category": category, "benefit": benefit, "address": address, "map_link": map_link, "condition": condition})
    save_data()
    return RedirectResponse("/partners", status_code=302)

@app.post("/partners/{partner_index}/delete")
async def delete_partner(request: Request, partner_index: int):
    delete_uploaded_file(partners[partner_index].get("image"))
    partners.pop(partner_index)
    save_data()
    return RedirectResponse("/partners", status_code=302)



@app.get("/partners/{partner_index}/edit", response_class=HTMLResponse)
async def partner_edit_form(request: Request, partner_index: int):
    partner = get_item(partners, partner_index)
    if partner is None:
        return render_layout("제휴 수정", '<div class="card empty">존재하지 않는 제휴 정보입니다.</div>')
    return render_partner_edit_form_page(partner, partner_index)


@app.post("/partners/{partner_index}/edit")
async def update_partner(
    partner_index: int,
    name: str = Form(...),
    category: str = Form("기타"),
    benefit: str = Form(...),
    condition: str = Form(""),
    contact: str = Form(""),
    link: str = Form(""),
    valid_until: str = Form("상시"),
):
    partner = get_item(partners, partner_index)
    if partner is not None:
        partner.update({
            "name": name,
            "category": category,
            "benefit": benefit,
            "condition": condition,
            "contact": contact,
            "link": link,
            "valid_until": valid_until,
        })
        save_data()
    return RedirectResponse("/partners", status_code=302)


@app.post("/partners/{partner_index}/delete")
async def delete_partner(partner_index: int):
    partner = get_item(partners, partner_index)
    if partner is not None:
        partners.pop(partner_index)
        save_data()
    return RedirectResponse("/partners", status_code=302)


@app.get("/meetings", response_class=HTMLResponse)
async def meeting_list(request: Request):
    return render_meetings_page()


@app.get("/meetings/new", response_class=HTMLResponse)
async def meeting_form(request: Request):
    return render_meeting_form_page()



@app.post("/meetings/new")
async def create_meeting(request: Request, 
    title: str = Form(...),
    meeting_date: str = Form(...),
    location: str = Form(...),
    agenda: str = Form(...),
    content: str = Form(""),
    file: UploadFile = File(None),
):
    if require_admin(request): return require_admin(request)
    file_path = save_upload(file, "meetings")

    meetings.insert(0, {
        "title": title,
        "meeting_date": meeting_date,
        "location": location,
        "agenda": agenda,
        "content": content,
        "file": file_path,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    save_data()
    return RedirectResponse("/meetings", status_code=302)


# --- Meeting edit/delete routes ---

@app.get("/meetings/{meeting_index}/edit", response_class=HTMLResponse)
async def meeting_edit_form(request: Request, meeting_index: int):
    meeting = get_item(meetings, meeting_index)
    if meeting is None:
        return render_layout("회의 수정", '<div class="card empty">존재하지 않는 회의입니다.</div>')
    return render_meeting_edit_form_page(meeting, meeting_index)


@app.post("/meetings/{meeting_index}/edit")
async def update_meeting(request: Request, 
    meeting_index: int,
    title: str = Form(...),
    meeting_date: str = Form(...),
    location: str = Form(...),
    agenda: str = Form(...),
    content: str = Form(""),
    file: UploadFile = File(None),
):
    if require_admin(request): return require_admin(request)
    meeting = get_item(meetings, meeting_index)
    if meeting is not None:
        if file and file.filename:
            delete_uploaded_file(meeting.get("file"))
            meeting["file"] = save_upload(file, "meetings")
        meeting.update({
            "title": title,
            "meeting_date": meeting_date,
            "location": location,
            "agenda": agenda,
            "content": content,
        })
        save_data()
    return RedirectResponse("/meetings", status_code=302)


@app.post("/meetings/{meeting_index}/delete")
async def delete_meeting(request: Request, meeting_index: int):
    if require_admin(request): return require_admin(request)
    meeting = get_item(meetings, meeting_index)
    if meeting is not None:
        delete_uploaded_file(meeting.get("file"))
        meetings.pop(meeting_index)
        save_data()
    return RedirectResponse("/meetings", status_code=302)


@app.get("/regulations", response_class=HTMLResponse)
async def regulation_list(request: Request):
    return render_regulations_page()


@app.get("/regulations/new", response_class=HTMLResponse)
async def regulation_form(request: Request):
    return render_regulation_form_page()


@app.post("/regulations/new")
async def create_regulation(request: Request, 
    title: str = Form(...),
    version: str = Form(...),
    effective_date: str = Form(...),
    description: str = Form(""),
    files: list[UploadFile] = File(None),
    file: UploadFile = File(None),
):
    if require_admin(request): return require_admin(request)
    file_paths = []
    if files:
        for f in files:
            if f and f.filename:
                fp = save_upload(f, "regulations")
                if fp: file_paths.append(fp)
    elif file and file.filename:
        fp = save_upload(file, "regulations")
        if fp: file_paths.append(fp)

    regulations.insert(0, {
        "files": file_paths,
        "title": title,
        "version": version,
        "effective_date": effective_date,
        "description": description,
        "file": file_path,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    save_data()
    return RedirectResponse("/regulations", status_code=302)


# --- Regulation edit/delete routes ---

@app.get("/regulations/{regulation_index}/edit", response_class=HTMLResponse)
async def regulation_edit_form(request: Request, regulation_index: int):
    regulation = get_item(regulations, regulation_index)
    if regulation is None:
        return render_layout("규정 수정", '<div class="card empty">존재하지 않는 규정입니다.</div>')
    return render_regulation_edit_form_page(regulation, regulation_index)


@app.post("/regulations/{regulation_index}/edit")
async def update_regulation(request: Request, 
    regulation_index: int,
    title: str = Form(...),
    version: str = Form(...),
    effective_date: str = Form(...),
    description: str = Form(""),
    files: list[UploadFile] = File(None),
    file: UploadFile = File(None),
):
    if require_admin(request): return require_admin(request)
    regulation = get_item(regulations, regulation_index)
    if regulation is not None:
        new_files = files if files and files[0].filename else ([file] if file and file.filename else [])
        if new_files:
            if regulation.get("files"):
                for f in regulation["files"]: delete_uploaded_file(f)
            elif regulation.get("file"):
                delete_uploaded_file(regulation.get("file"))
            
            file_paths = []
            for f in new_files:
                if f and f.filename:
                    fp = save_upload(f, "regulations")
                    if fp: file_paths.append(fp)
            
            if file_paths:
                regulation["files"] = file_paths
                regulation["file"] = file_paths[0]
        regulation.update({
            "title": title,
            "version": version,
            "effective_date": effective_date,
            "description": description,
        })
        save_data()
    return RedirectResponse("/regulations", status_code=302)


@app.post("/regulations/{regulation_index}/delete")
async def delete_regulation(request: Request, regulation_index: int):
    if require_admin(request): return require_admin(request)
    regulation = get_item(regulations, regulation_index)
    if regulation is not None:
        if regulation.get("files"):
            for f in regulation["files"]: delete_uploaded_file(f)
        elif regulation.get("file"):
            delete_uploaded_file(regulation.get("file"))
        regulations.pop(regulation_index)
        save_data()
    return RedirectResponse("/regulations", status_code=302)


@app.get("/suggest", response_class=HTMLResponse)
async def suggest_form(request: Request):
    return render_suggest_form_page()


@app.post("/suggest")
async def create_suggestion(
    title: str = Form(...),
    content: str = Form(...),
    category: str = Form("건의"),
    is_anonymous: str = Form("Y"),
    attachment: UploadFile = File(None),
):
    attachment_path = save_upload(attachment, "suggestions")

    suggestions.insert(0, {
        "title": title,
        "content": content,
        "category": category,
        "is_anonymous": is_anonymous,
        "attachment": attachment_path,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    save_data()
    return RedirectResponse("/", status_code=302)


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    redirect = require_admin(request)
    if redirect:
        return redirect
    return render_admin_dashboard(request)

@app.get("/documents/{document_index}/edit", response_class=HTMLResponse)
async def document_edit_form(request: Request, document_index: int):
    document = get_item(documents, document_index)
    if document is None:
        return render_layout("문서 수정", '<div class="card empty">존재하지 않는 문서입니다.</div>')
    return render_document_edit_form_page(document, document_index)


@app.post("/documents/{document_index}/edit")
async def update_document(request: Request, 
    document_index: int,
    title: str = Form(...),
    category: str = Form("행정서식"),
    description: str = Form(""),
    files: list[UploadFile] = File(None),
):
    if require_admin(request): return require_admin(request)
    document = get_item(documents, document_index)
    if document is not None:
        if files and len(files) > 0 and files[0].filename:
            # Delete old files
            if document.get("files"):
                for f in document["files"]: delete_uploaded_file(f)
            elif document.get("file"):
                delete_uploaded_file(document.get("file"))
            
            file_paths = []
            for f in files:
                if f.filename:
                    fp = save_upload(f, "documents")
                    if fp: file_paths.append(fp)
            
            if file_paths:
                document["files"] = file_paths
                document["file"] = file_paths[0]
                
        document.update({
            "title": title,
            "category": category,
            "description": description,
        })
        save_data()
    return RedirectResponse("/documents", status_code=302)


@app.post("/documents/{document_index}/delete")
async def delete_document(request: Request, document_index: int):
    if require_admin(request): return require_admin(request)
    document = get_item(documents, document_index)
    if document is not None:
        if document.get("files"):
            for f in document["files"]: delete_uploaded_file(f)
        elif document.get("file"):
            delete_uploaded_file(document.get("file"))
        documents.pop(document_index)
        save_data()
    return RedirectResponse("/documents", status_code=302)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
