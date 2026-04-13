import re

with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

# Pass request to partners route
code = code.replace(
    'def partner_list(request: Request):\n    return render_partners_page()',
    'def partner_list(request: Request):\n    return render_partners_page(request)'
)

# Render partners page
new_partners = """def render_partners_page(request: Request) -> HTMLResponse:
    is_adm = is_admin(request)
    admin_actions_top = '<a class="btn" href="/partners/new">제휴 등록</a>' if is_adm else ''
    
    items = []
    for idx, p in enumerate(partners):
        link_html = f'<a class="btn btn-light" style="margin-top:10px; width:100%;" href="{h(p.get("map_link"))}" target="_blank">네이버 지도 보기</a>' if p.get("map_link") else ""
        manage_html = f'''
            <div style="margin-top:10px; display:flex; gap:10px;">
                <a class="btn btn-light" href="/partners/{idx}/edit">수정</a>
                <form class="inline-form" action="/partners/{idx}/delete" method="post">
                    <button class="btn btn-light" type="submit">삭제</button>
                </form>
            </div>
        ''' if is_adm else ''
        
        img_src = p.get('image') or "https://via.placeholder.com/400x300?text=No+Image"
        
        items.append(f'''
        <details class="guide-detail partner-card" style="margin-bottom:0; display:flex; flex-direction:column; height:100%;">
            <summary style="padding:0; flex-direction:column; align-items:flex-start; text-align:left; border-bottom:none;">
                <div style="width:100%; aspect-ratio:4/3; background:url('{img_src}') center/cover no-repeat;"></div>
                <div style="padding:16px;">
                    <div class="eyebrow">{h(p.get('category'))}</div>
                    <h3 style="margin:0; font-size:18px;">{h(p.get('name'))}</h3>
                </div>
            </summary>
            <div class="detail-body" style="border-top:1px solid var(--line); padding-top:16px;">
                <p><strong>혜택:</strong><br>{h(p.get('benefit')).replace(chr(10), '<br>')}</p>
                <p><strong>주소:</strong> {h(p.get('address'))}</p>
                <p><strong>이용 조건:</strong> {h(p.get('condition'))}</p>
                {link_html}
                {manage_html}
            </div>
        </details>
        ''')
    
    empty_state = '<div class="card empty">등록된 제휴업체가 없습니다.</div>' if not items else ''
    
    body = f\"\"\"
    <style>
        .partner-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
        }}
        .partner-card summary::after {{ display: none; }} /* hide + / - icon for cleaner look */
        @media (max-width: 1024px) {{
            .partner-grid {{ grid-template-columns: repeat(3, 1fr); }}
        }}
        @media (max-width: 768px) {{
            .partner-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
        @media (max-width: 480px) {{
            .partner-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
    <div class="hero">
        <div class="eyebrow">Partnerships</div>
        <h2>제휴업체</h2>
        <p>예술대학 학우분들을 위해 맺어진 제휴 혜택입니다. 장소를 클릭해 자세한 혜택과 위치를 확인하세요.</p>
        <div class="actions">
            {admin_actions_top}
        </div>
    </div>
    <div class="partner-grid">
        {''.join(items)}
    </div>
    {empty_state}
    \"\"\"
    return render_layout("제휴업체", body)"""

code = re.sub(r'def render_partners_page\(\) -> HTMLResponse:.*?(?=def render_partner_form_page)', new_partners, code, flags=re.DOTALL)

# Render partner forms
new_partner_form = """def render_partner_form_page() -> HTMLResponse:
    body = \"\"\"
    <div class="card">
        <h2>제휴업체 등록</h2>
        <form action="/partners/new" method="post" enctype="multipart/form-data">
            <label>업체명<input type="text" name="name" required></label>
            <label>카테고리<input type="text" name="category" value="기타"></label>
            <label>대표 사진<input type="file" name="image" accept="image/*"></label>
            <label>혜택 내용<textarea name="benefit" required></textarea></label>
            <label>주소<input type="text" name="address"></label>
            <label>네이버 지도 링크<input type="text" name="map_link"></label>
            <label>이용 조건<textarea name="condition"></textarea></label>
            <button class="btn" type="submit">등록</button>
        </form>
    </div>
    \"\"\"
    return render_layout("제휴업체 등록", body)"""

code = re.sub(r'def render_partner_form_page\(\) -> HTMLResponse:.*?(?=def render_meetings_page)', new_partner_form + "\n\n", code, flags=re.DOTALL)

new_partner_edit = """def render_partner_edit_form_page(partner: dict, index: int) -> HTMLResponse:
    body = f\"\"\"
    <div class="card">
        <div class="section-title">
            <h2>제휴 수정</h2>
            <a class="btn btn-light" href="/partners">목록으로</a>
        </div>
        <form action="/partners/{index}/edit" method="post" enctype="multipart/form-data">
            <label>업체명<input type="text" name="name" value="{h(partner.get('name'))}" required></label>
            <label>카테고리<input type="text" name="category" value="{h(partner.get('category'))}"></label>
            <label>새 대표 사진<input type="file" name="image" accept="image/*"></label>
            <p class="muted">사진을 새로 올리지 않으면 기존 사진을 유지합니다.</p>
            <label>혜택 내용<textarea name="benefit" required>{h(partner.get('benefit'))}</textarea></label>
            <label>주소<input type="text" name="address" value="{h(partner.get('address'))}"></label>
            <label>네이버 지도 링크<input type="text" name="map_link" value="{h(partner.get('map_link'))}"></label>
            <label>이용 조건<textarea name="condition">{h(partner.get('condition'))}</textarea></label>
            <div class="actions">
                <button class="btn" type="submit">수정 저장</button>
            </div>
        </form>
    </div>
    \"\"\"
    return render_layout("제휴 수정", body)"""

code = re.sub(r'def render_partner_edit_form_page\(partner: dict, index: int\) -> HTMLResponse:.*?(?=def render_notices_page)', new_partner_edit + "\n\n\n", code, flags=re.DOTALL)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Partners UI done")
