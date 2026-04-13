import re

with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update render_admin_dashboard
new_dashboard = """def render_admin_dashboard(request: Request) -> HTMLResponse:
    login_state = "로그인 상태" if is_admin(request) else "비로그인 상태"
    logout_button = '<form class="inline-form" action="/admin/logout" method="post"><button class="btn btn-light" type="submit">로그아웃</button></form>' if is_admin(request) else '<a class="btn btn-light" href="/admin/login">로그인</a>'
    
    status_val = home_content.get("office_status_value", "부재중")
    status_select = f'''
        <form action="/admin/home_status" method="post" style="display:flex; gap:10px; align-items:center;">
            <select name="status" style="width:auto; padding:8px 12px;">
                <option value="재실중" {'selected' if status_val == '재실중' else ''}>재실중</option>
                <option value="부재중" {'selected' if status_val == '부재중' else ''}>부재중</option>
            </select>
            <button class="btn" type="submit" style="padding:8px 16px;">상태 변경</button>
        </form>
    '''
    
    body = f\"\"\"
    <div class="hero">
        <div class="eyebrow">Admin Overview</div>
        <h2>관리자 대시보드</h2>
        <p>현재 등록 현황과 운영 데이터를 확인할 수 있습니다. 공지 작성, 수정, 삭제는 관리자 로그인 상태에서만 가능합니다.</p>
        <div class="actions">
            <span class="pill">{login_state}</span>
            {logout_button}
        </div>
    </div>
    <div class="card">
        <h3>학생회실 재실 상태 관리</h3>
        {status_select}
    </div>
    <div class="grid">
        <div class="metric-card"><h3>공지사항</h3><p class="metric-value">{len(notices)}</p><div class="metric-meta">등록된 공지 수</div></div>
        <div class="metric-card"><h3>문서자료실</h3><p class="metric-value">{len(documents)}</p><div class="metric-meta">업로드된 문서 수</div></div>
        <div class="metric-card"><h3>제휴업체</h3><p class="metric-value">{len(partners)}</p><div class="metric-meta">활성 제휴 정보</div></div>
        <div class="metric-card"><h3>회의공고</h3><p class="metric-value">{len(meetings)}</p><div class="metric-meta">소집 공고 수</div></div>
        <div class="metric-card"><h3>규정</h3><p class="metric-value">{len(regulations)}</p><div class="metric-meta">등록 규정 수</div></div>
        <div class="metric-card"><h3>신문고</h3><p class="metric-value">{len(suggestions)}</p><div class="metric-meta">접수 건수</div></div>
    </div>
    \"\"\"
    return render_layout("관리자", body)"""

code = re.sub(r'def render_admin_dashboard\(request: Request\) -> HTMLResponse:.*?(?=@app\.get\("/",)', new_dashboard + "\n\n\n", code, flags=re.DOTALL)

# 2. Add /admin/home_status endpoint
new_route = """
@app.post("/admin/home_status")
async def update_home_status(request: Request, status: str = Form(...)):
    redirect = require_admin(request)
    if redirect: return redirect
    home_content["office_status_value"] = status
    save_data()
    return RedirectResponse("/admin", status_code=302)
"""

code = code.replace('@app.get("/", response_class=HTMLResponse)', new_route + '\n@app.get("/", response_class=HTMLResponse)')

with open("main.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Admin dashboard done")
