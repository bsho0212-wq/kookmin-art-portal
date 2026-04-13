import re
import os

with open("main.py", "r", encoding="utf-8") as f:
    c = f.read()

# Supabase imports & init
c = c.replace("from fastapi import", "from supabase import create_client, Client\nfrom fastapi import")
supa_init = """
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://kwwokwoyqygbcrcsyyob.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt3d29rd295cXlnYmNyY3N5eW9iIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTk4ODIyNCwiZXhwIjoyMDkxNTY0MjI0fQ.8eP2BSCzu5AMlamlsi2-2pKmmEPAyD4-ljbwyMk-TSU")
BUCKET_NAME = "kookmin"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
"""
c = c.replace("app = FastAPI()", supa_init + "\napp = FastAPI()")

# Clean local mount & fs stuff
c = re.sub(r'# 폴더 설정.*?app\.mount\("/uploads", StaticFiles\(directory=UPLOAD_DIR\), name="uploads"\)', '', c, flags=re.DOTALL)
c = c.replace("def ensure_dir(path: str) -> None:\n    os.makedirs(path, exist_ok=True)", "def ensure_dir(path: str) -> None:\n    pass")

# save_upload
c = re.sub(r'def save_upload\(file: UploadFile \| None, subdir: str\) -> str \| None:.*?return f"/uploads/\{subdir\}/\{filename\}"', """def save_upload(file: UploadFile | None, subdir: str) -> str | None:
    if not file or not file.filename: return None
    path = f"{subdir}/{safe_filename(file.filename)}"
    try:
        supabase.storage.from_(BUCKET_NAME).upload(path, file.file.read(), {"content-type": file.content_type})
        return supabase.storage.from_(BUCKET_NAME).get_public_url(path)
    except: return None""", c, flags=re.DOTALL)

# delete_uploaded_file
c = re.sub(r'def delete_uploaded_file\(file_url: str \| None\) -> None:.*?os\.remove\(absolute_path\)', """def delete_uploaded_file(file_url: str | None) -> None:
    if not file_url: return
    prefix = f"/storage/v1/object/public/{BUCKET_NAME}/"
    if prefix in file_url:
        try: supabase.storage.from_(BUCKET_NAME).remove([file_url.split(prefix)[-1]])
        except: pass""", c, flags=re.DOTALL)

# load_data & save_data
c = re.sub(r'def load_data\(\) -> dict:.*?return data', """def load_data() -> dict:
    try:
        raw = json.loads(supabase.storage.from_(BUCKET_NAME).download("site_data.json").decode('utf-8'))
    except:
        raw = {}
    data = default_data()
    for k in data.keys():
        if raw.get(k) is not None: data[k] = raw[k]
    return data""", c, flags=re.DOTALL)

c = re.sub(r'def save_data\(data: dict \| None = None\) -> None:.*?json\.dump\(payload, f, ensure_ascii=False, indent=2\)', """def save_data(data: dict | None = None) -> None:
    p = data or {"notices": notices, "documents": documents, "partners": partners, "meetings": meetings, "regulations": regulations, "suggestions": suggestions, "home_content": home_content, "council_members": council_members}
    try:
        supabase.storage.from_(BUCKET_NAME).remove(["site_data.json"])
        supabase.storage.from_(BUCKET_NAME).upload("site_data.json", json.dumps(p, ensure_ascii=False, indent=2).encode('utf-8'), {"content-type": "application/json"})
    except: pass""", c, flags=re.DOTALL)

# Home content defaults
c = c.replace('"hero_title": "예술대학 학생들이 자주 찾는 공지와 자료를 한곳에서 확인할 수 있도록 정리했습니다."', '"hero_title": "국민대학교 예술대학 학생들을 위한 통합 안내 포털입니다."')
c = c.replace('"hero_description": "이 페이지에서는 공지, 행정 문서, 대표자 명단, 신문고처럼 학생들이 자주 확인하는 정보를 빠르게 찾아볼 수 있습니다. 필요한 메뉴를 바로 누르면 각 페이지에서 자세한 내용을 확인할 수 있습니다."', '"hero_description": "학우 여러분이 학교생활에 필요한 공지사항, 문서 양식, 회의 결과 등을 한곳에서 쉽고 빠르게 확인할 수 있습니다."')
c = c.replace('"office_status_value": "재실중"', '"office_status_value": "부재중"')
c = c.replace('"vision_title": "전공 간 교류가 많아질수록 더 좋은 예술대학"', '"vision_title": "예술대학 학생회"')
c = c.replace('"vision_description": "예술대학은 전공 간 교류가 활발할수록 더 다양한 협업과 작업이 가능하다는 방향을 지향합니다. 학생회는 그 교류가 자연스럽게 일어날 수 있도록 정보와 소통의 기반을 정리합니다."', '"vision_description": "학우 여러분의 원활한 학교생활과 다양한 전공 간의 교류를 위해 학생회가 함께합니다."')

# Replace render_home_page
home_str = """def render_home_page() -> HTMLResponse:
    notice_cards = "".join(f'<div class="member-card"><div class="member-role">{h(n.get("category"))}</div><p class="member-name" style="font-size:18px;">{h(n.get("title"))}</p><p class="member-meta">{h(n.get("created_at"))}</p></div>' for n in notices[:3])
    if not notice_cards: notice_cards = '<div class="card empty">등록된 최근 공지사항이 없습니다.</div>'
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
            <div class="metric-card"><h3>{h(home_content.get("office_status_title"))}</h3><p class="metric-value">{h(home_content.get("office_status_value"))}</p><div class="metric-meta">{h(home_content.get("office_status_meta"))}</div></div>
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
"""
c = re.sub(r'def render_home_page\(\) -> HTMLResponse:.*?(?=def render_archive_page\(\) -> HTMLResponse:)', home_str, c, flags=re.DOTALL)

# Council Page
c = c.replace('def council_page(request: Request):\n    return render_council_page()', 'def council_page(request: Request):\n    return render_council_page(request)')
council_str = """def render_council_page(request: Request) -> HTMLResponse:
    is_adm = is_admin(request)
    def s_exec(m_list):
        return sorted(m_list, key=lambda m: 0 if "장" in m.get("role","") and "부" not in m.get("role","") else 1 if "부" in m.get("role","") and "장" in m.get("role","") else 2)
    
    branch_cards = []
    for k, v in ARTS_EXECUTIVE_GROUPS.items():
        if k == "비대위원장단": continue
        rws = "".join(f'<div class="executive-member-row"><span class="executive-member-role">{h(m.get("role"))}</span><span class="executive-member-name">{h(m.get("name"))}</span></div>' for m in s_exec(v))
        branch_cards.append(f'<details class="guide-detail" open><summary>{h(k)} ({len(v)}명)</summary><div class="detail-body" style="padding-top:16px;"><div class="executive-member-list">{rws}</div></div></details>')
    
    ldr = "".join(f'<div class="executive-top-member"><span class="executive-top-role">{h(m.get("role"))}</span><span class="executive-top-name">{h(m.get("name"))}</span></div>' for m in s_exec(ARTS_EXECUTIVE_GROUPS.get("비대위원장단", [])))
    
    major_clusters = [("공연예술학부", ["영화전공", "연극전공", "무용전공"]),("미술학부", ["회화전공", "입체미술전공"]),("음악학부", ["관현악전공", "피아노전공", "성악전공", "작곡전공"])]
    cluster_cards = []
    for c_name, divs in major_clusters:
        m_units = []
        for d in divs:
            mems = [(i, m) for i, m in enumerate(council_members) if m.get("division") == d]
            if not mems: continue
            rws = "".join(f'<div class="major-member-row"><div><div class="major-member-role">{h(m.get("role"))}</div><div class="major-member-name">{h(m.get("name"))}</div></div>{"<a class=\\"btn btn-light\\" href=\\"/council/"+str(i)+"/edit\\">수정</a>" if is_adm else ""}</div>' for i, m in mems)
            m_units.append(f'<section class="major-unit"><h4>{h(d)}</h4><div class="major-member-pair">{rws}</div></section>')
        cluster_cards.append(f'<details class="guide-detail"><summary>{h(c_name)}</summary><div class="detail-body" style="padding-top:16px;"><div class="major-cluster-meta">{", ".join(divs)}</div><div class="major-grid">{"".join(m_units) if m_units else "<div class=\\"card empty\\">없음</div>"}</div></div></details>')
    
    body = f'''<div class="hero"><div class="eyebrow">Council Directory</div><h2>예술대학 학생회 및 대표자 안내</h2><p>학우 여러분을 위해 일하는 예술대학 학생회와 각 전공 대표자 명단입니다.</p><div class="council-section-anchor"><a class="btn btn-light" href="#arts-executive">학생회 명단</a><a class="btn btn-light" href="#council-members">대표자 명단</a>{"<a class=\\"btn\\" href=\\"/council/new\\">대표자 추가</a>" if is_adm else ""}</div></div><section id="arts-executive" class="council-block" style="margin-top:18px;"><div class="card council-block-head"><div><div class="eyebrow">Arts Student Council</div><h2>예술대학 학생회</h2></div></div><p class="muted">예술대학 소속 학생들을 위해 행정, 기획, 소통을 담당하는 학생회 명단입니다.</p><div class="executive-hierarchy"><section class="executive-top" style="margin-bottom:16px;"><div class="eyebrow" style="color:rgba(255,255,255,0.74);">Leadership</div><h3>비대위원장단</h3><p>예술대학 학생회를 총괄합니다.</p><div class="executive-top-members">{ldr}</div></section><div class="guide-accordion">{"".join(branch_cards)}</div></div></section><section id="council-members" class="council-block" style="margin-top:24px;"><div class="card council-block-head"><div><div class="eyebrow">Representative List</div><h2>전공별 대표자</h2></div></div><p class="muted">각 전공을 대표하여 의견을 조율하고 활동하는 대표자 명단입니다.</p><div class="guide-accordion">{"".join(cluster_cards)}</div></section>'''
    return render_layout("대의원 소개", body)
"""
c = re.sub(r'def render_council_page\(\) -> HTMLResponse:.*?(?=def render_council_form_page)', council_str, c, flags=re.DOTALL)

# Documents
c = c.replace('def document_list(request: Request):\n    return render_documents_page()', 'def document_list(request: Request):\n    return render_documents_page(request)')
doc_str = """def render_documents_page(request: Request) -> HTMLResponse:
    is_adm = is_admin(request)
    items = []
    for idx, d in enumerate(documents):
        dn = f'<a class="btn" href="{h(d.get("file"))}">다운로드</a>' if d.get("file") else ''
        mg = f'<a class="btn btn-light" href="/documents/{idx}/edit">수정</a><form class="inline-form" action="/documents/{idx}/delete" method="post"><button class="btn btn-light" type="submit">삭제</button></form>' if is_adm else ''
        items.append(f'<div class="card"><div class="section-title"><h2>{h(d.get("title"))}</h2><span class="pill">{h(d.get("category"))}</span></div><p>{h(d.get("description"))}</p><div class="meta">등록일 {h(d.get("created_at"))}</div><div class="actions">{dn}{mg}</div></div>')
    body = f'''<div class="hero"><div class="eyebrow">Document Archive</div><h2>문서자료실</h2><p>학우 여러분이 학교생활이나 행정 처리 중 필요한 문서 양식을 내려받을 수 있는 공간입니다.</p><div class="actions">{"<a class=\\"btn\\" href=\\"/documents/new\\">문서 업로드</a>" if is_adm else ""}</div></div>{"".join(items) if items else "<div class=\\"card empty\\">없음</div>"}'''
    return render_layout("문서자료실", body)
"""
c = re.sub(r'def render_documents_page\(\) -> HTMLResponse:.*?(?=def render_document_form_page)', doc_str, c, flags=re.DOTALL)

# Partners
c = c.replace('def partner_list(request: Request):\n    return render_partners_page()', 'def partner_list(request: Request):\n    return render_partners_page(request)')
ptn_str = """def render_partners_page(request: Request) -> HTMLResponse:
    is_adm = is_admin(request)
    items = []
    for idx, p in enumerate(partners):
        img_src = p.get('image') or "https://via.placeholder.com/400x300?text=No+Image"
        map_html = f'<a class="btn btn-light" style="margin-top:10px; width:100%;" href="{h(p.get("map_link"))}" target="_blank">네이버 지도 보기</a>' if p.get("map_link") else ""
        mg = f'<div style="margin-top:10px; display:flex; gap:10px;"><a class="btn btn-light" href="/partners/{idx}/edit">수정</a><form class="inline-form" action="/partners/{idx}/delete" method="post"><button class="btn btn-light" type="submit">삭제</button></form></div>' if is_adm else ''
        items.append(f'''<details class="guide-detail partner-card" style="margin-bottom:0; display:flex; flex-direction:column; height:100%;"><summary style="padding:0; flex-direction:column; align-items:flex-start; text-align:left; border-bottom:none;"><div style="width:100%; aspect-ratio:4/3; background:url('{img_src}') center/cover no-repeat;"></div><div style="padding:16px;"><div class="eyebrow">{h(p.get("category"))}</div><h3 style="margin:0; font-size:18px;">{h(p.get("name"))}</h3></div></summary><div class="detail-body" style="border-top:1px solid var(--line); padding-top:16px;"><p><strong>혜택:</strong><br>{h(p.get("benefit")).replace(chr(10), "<br>")}</p><p><strong>주소:</strong> {h(p.get("address"))}</p><p><strong>이용 조건:</strong> {h(p.get("condition"))}</p>{map_html}{mg}</div></details>''')
    body = f'''<style>.partner-grid{{display:grid; grid-template-columns:repeat(4,1fr); gap:16px;}} .partner-card summary::after{{display:none;}} @media(max-width:1024px){{.partner-grid{{grid-template-columns:repeat(3,1fr);}}}} @media(max-width:768px){{.partner-grid{{grid-template-columns:repeat(2,1fr);}}}} @media(max-width:480px){{.partner-grid{{grid-template-columns:1fr;}}}}</style><div class="hero"><div class="eyebrow">Partnerships</div><h2>제휴업체</h2><p>예술대학 학우분들을 위해 맺어진 제휴 혜택입니다. 장소를 클릭해 자세한 혜택과 위치를 확인하세요.</p><div class="actions">{"<a class=\\"btn\\" href=\\"/partners/new\\">제휴 등록</a>" if is_adm else ""}</div></div><div class="partner-grid">{"".join(items)}</div>{"<div class=\\"card empty\\">없음</div>" if not items else ""}'''
    return render_layout("제휴업체", body)

def render_partner_form_page() -> HTMLResponse:
    body = '''<div class="card"><h2>제휴업체 등록</h2><form action="/partners/new" method="post" enctype="multipart/form-data"><label>업체명<input type="text" name="name" required></label><label>카테고리<input type="text" name="category" value="기타"></label><label>대표 사진<input type="file" name="image" accept="image/*"></label><label>혜택 내용<textarea name="benefit" required></textarea></label><label>주소<input type="text" name="address"></label><label>네이버 지도 링크<input type="text" name="map_link"></label><label>이용 조건<textarea name="condition"></textarea></label><button class="btn" type="submit">등록</button></form></div>'''
    return render_layout("제휴업체 등록", body)

def render_partner_edit_form_page(partner: dict, index: int) -> HTMLResponse:
    body = f'''<div class="card"><div class="section-title"><h2>제휴 수정</h2><a class="btn btn-light" href="/partners">목록으로</a></div><form action="/partners/{index}/edit" method="post" enctype="multipart/form-data"><label>업체명<input type="text" name="name" value="{h(partner.get("name"))}" required></label><label>카테고리<input type="text" name="category" value="{h(partner.get("category"))}"></label><label>새 대표 사진<input type="file" name="image" accept="image/*"></label><label>혜택 내용<textarea name="benefit" required>{h(partner.get("benefit"))}</textarea></label><label>주소<input type="text" name="address" value="{h(partner.get("address"))}"></label><label>네이버 지도 링크<input type="text" name="map_link" value="{h(partner.get("map_link"))}"></label><label>이용 조건<textarea name="condition">{h(partner.get("condition"))}</textarea></label><button class="btn" type="submit">수정 저장</button></form></div>'''
    return render_layout("제휴 수정", body)
"""
c = re.sub(r'def render_partners_page\(\) -> HTMLResponse:.*?(?=def render_meetings_page\(\))', ptn_str, c, flags=re.DOTALL)

# Routes fix
route_str = """@app.post("/partners/new")
async def create_partner(request: Request, name: str = Form(...), category: str = Form("기타"), benefit: str = Form(...), address: str = Form(""), map_link: str = Form(""), condition: str = Form(""), image: UploadFile = File(None)):
    if require_admin(request): return require_admin(request)
    partners.insert(0, {"name": name, "category": category, "benefit": benefit, "address": address, "map_link": map_link, "condition": condition, "image": save_upload(image, "partners"), "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")})
    save_data()
    return RedirectResponse("/partners", status_code=302)

@app.get("/partners/{partner_index}/edit", response_class=HTMLResponse)
async def partner_edit_form(request: Request, partner_index: int):
    if require_admin(request): return require_admin(request)
    return render_partner_edit_form_page(partners[partner_index], partner_index)

@app.post("/partners/{partner_index}/edit")
async def update_partner(request: Request, partner_index: int, name: str = Form(...), category: str = Form("기타"), benefit: str = Form(...), address: str = Form(""), map_link: str = Form(""), condition: str = Form(""), image: UploadFile = File(None)):
    if require_admin(request): return require_admin(request)
    if image and image.filename:
        delete_uploaded_file(partners[partner_index].get("image"))
        partners[partner_index]["image"] = save_upload(image, "partners")
    partners[partner_index].update({"name": name, "category": category, "benefit": benefit, "address": address, "map_link": map_link, "condition": condition})
    save_data()
    return RedirectResponse("/partners", status_code=302)

@app.post("/partners/{partner_index}/delete")
async def delete_partner(request: Request, partner_index: int):
    if require_admin(request): return require_admin(request)
    delete_uploaded_file(partners[partner_index].get("image"))
    partners.pop(partner_index)
    save_data()
    return RedirectResponse("/partners", status_code=302)
"""
c = re.sub(r'@app\.post\("/partners/new"\).*?RedirectResponse\("/partners", status_code=302\)', route_str, c, flags=re.DOTALL)

# Regulations text updates
c = c.replace('<h2>규정을 그냥 나열하지 않고, 학생이 실제로 행동할 수 있는 단위로 다시 풀었습니다.</h2>', '<h2>자주 묻는 학생회 규정과 권리를 확인하세요.</h2>')
c = c.replace('<p>원문 규정은 그대로 유지하되, 학생이 자주 묻게 되는 질문을 먼저 클릭해서 확인할 수 있도록 재구성했습니다. 특히 전체학생대표자회의 소집, 학생의 권리, 의결기구의 차이처럼 실제 운영에서 자주 헷갈리는 부분을 먼저 읽을 수 있게 했습니다.</p>', '<p>어렵게 느껴질 수 있는 학생회 규정을, 학우 여러분의 권리와 궁금증을 중심으로 쉽게 풀었습니다. 필요한 상황에 맞춰 읽어보세요.</p>')

# Admin home status
adm_str = """def render_admin_dashboard(request: Request) -> HTMLResponse:
    login_state = "로그인 상태" if is_admin(request) else "비로그인 상태"
    logout_button = '<form class="inline-form" action="/admin/logout" method="post"><button class="btn btn-light" type="submit">로그아웃</button></form>' if is_admin(request) else '<a class="btn btn-light" href="/admin/login">로그인</a>'
    status_val = home_content.get("office_status_value", "부재중")
    status_select = f'<form action="/admin/home_status" method="post" style="display:flex; gap:10px; align-items:center;"><select name="status" style="width:auto; padding:8px 12px;"><option value="재실중" {"selected" if status_val=="재실중" else ""}>재실중</option><option value="부재중" {"selected" if status_val=="부재중" else ""}>부재중</option></select><button class="btn" type="submit" style="padding:8px 16px;">상태 변경</button></form>'
    body = f'''<div class="hero"><div class="eyebrow">Admin Overview</div><h2>관리자 대시보드</h2><div class="actions"><span class="pill">{login_state}</span>{logout_button}</div></div><div class="card"><h3>학생회실 재실 상태 관리</h3>{status_select}</div><div class="grid"><div class="metric-card"><h3>공지사항</h3><p class="metric-value">{len(notices)}</p></div><div class="metric-card"><h3>문서자료실</h3><p class="metric-value">{len(documents)}</p></div></div>'''
    return render_layout("관리자", body)
"""
c = re.sub(r'def render_admin_dashboard\(request: Request\) -> HTMLResponse:.*?(?=@app\.get\("/",)', adm_str, c, flags=re.DOTALL)
c = c.replace('@app.get("/", response_class=HTMLResponse)', '@app.post("/admin/home_status")\nasync def upd_home(request: Request, status: str = Form(...)):\n    if require_admin(request): return require_admin(request)\n    home_content["office_status_value"] = status\n    save_data()\n    return RedirectResponse("/admin", status_code=302)\n\n@app.get("/", response_class=HTMLResponse)')

# Add missing admin checks on routes
def inject_admin(match):
    s = match.group(0)
    if "request" not in s: s = s.replace("(", "(request: Request, ", 1)
    return s.replace("):\n", "):\n    if require_admin(request): return require_admin(request)\n")

for r in ["/council/new", "/council/{member_index}/edit", "/council/{member_index}/delete",
          "/documents/new", "/documents/{document_index}/edit", "/documents/{document_index}/delete",
          "/meetings/new", "/meetings/{meeting_index}/edit", "/meetings/{meeting_index}/delete",
          "/regulations/new", "/regulations/{regulation_index}/edit", "/regulations/{regulation_index}/delete"]:
    c = re.sub(rf'@app\.get\("{r}".*?async def .*?\)?:', inject_admin, c, flags=re.DOTALL)
    c = re.sub(rf'@app\.post\("{r}".*?async def .*?\)?:', inject_admin, c, flags=re.DOTALL)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(c)

print("Build complete.")
