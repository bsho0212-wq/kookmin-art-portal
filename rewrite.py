import re
import os

with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update HOME_CONTENT_DEFAULTS text & student-friendly texts
code = code.replace(
    '"hero_title": "예술대학 학생들이 자주 찾는 공지와 자료를 한곳에서 확인할 수 있도록 정리했습니다."',
    '"hero_title": "국민대학교 예술대학 학생들을 위한 통합 안내 포털입니다."'
)
code = code.replace(
    '"hero_description": "이 페이지에서는 공지, 행정 문서, 대표자 명단, 신문고처럼 학생들이 자주 확인하는 정보를 빠르게 찾아볼 수 있습니다. 필요한 메뉴를 바로 누르면 각 페이지에서 자세한 내용을 확인할 수 있습니다."',
    '"hero_description": "학우 여러분이 학교생활에 필요한 공지사항, 문서 양식, 회의 결과 등을 한곳에서 쉽고 빠르게 확인할 수 있습니다."'
)
code = code.replace(
    '"vision_title": "전공 간 교류가 많아질수록 더 좋은 예술대학"',
    '"vision_title": "예술대학 학생회"'
)
code = code.replace(
    '"vision_description": "예술대학은 전공 간 교류가 활발할수록 더 다양한 협업과 작업이 가능하다는 방향을 지향합니다. 학생회는 그 교류가 자연스럽게 일어날 수 있도록 정보와 소통의 기반을 정리합니다."',
    '"vision_description": "학우 여러분의 원활한 학교생활과 다양한 전공 간의 교류를 위해 학생회가 함께합니다."'
)

# Fix office status (5)
code = code.replace(
    '"office_status_value": "재실중"',
    '"office_status_value": "부재중"'
)

# 2. Rewrite render_home_page completely to remove Council, add Recent Notices
def replace_func(match):
    return """def render_home_page() -> HTMLResponse:
    recent_notices = notices[:3]
    notice_cards = "".join(
        f'''
        <div class="member-card">
            <div class="member-role">{h(n.get("category"))}</div>
            <p class="member-name" style="font-size:18px;">{h(n.get("title"))}</p>
            <p class="member-meta">{h(n.get("created_at"))}</p>
        </div>
        '''
        for n in recent_notices
    )
    if not notice_cards:
        notice_cards = '<div class="card empty">등록된 최근 공지사항이 없습니다.</div>'

    body = f\"\"\"
    <div class="hero-grid">
        <section class="hero">
            <div class="eyebrow">Kookmin Univ. College of Arts</div>
            <h2>{h(home_content.get("hero_title"))}</h2>
            <p>{h(home_content.get("hero_description"))}</p>
            <div class="quick-tags">
                <span class="quick-tag">KMU Blue</span>
                <span class="quick-tag">KMU Yellow</span>
                <span class="quick-tag">KMU Sky Blue</span>
                <span class="quick-tag">KMU Green</span>
                <span class="quick-tag">KMU Orange</span>
                <span class="quick-tag">KMU Gray</span>
            </div>
            <div class="color-band">
                <span style="background:#004f9f"></span>
                <span style="background:#f3c53d"></span>
                <span style="background:#f0923a"></span>
                <span style="background:#a1daf8"></span>
                <span style="background:#95c13d"></span>
                <span style="background:#18a572"></span>
            </div>
            <div class="actions">
                <a class="btn" href="/notices">공지사항 보기</a>
                <a class="btn btn-light" href="/archive">통합 자료 보기</a>
            </div>
        </section>
        <div class="hero-side">
            <div class="metric-card">
                <h3>{h(home_content.get("office_status_title"))}</h3>
                <p class="metric-value">{h(home_content.get("office_status_value"))}</p>
                <div class="metric-meta">{h(home_content.get("office_status_meta"))}</div>
            </div>
            <div class="card">
                <div class="eyebrow">Vision</div>
                <h3>{h(home_content.get("vision_title"))}</h3>
                <p class="muted">{h(home_content.get("vision_description"))}</p>
            </div>
        </div>
    </div>

    <div class="intro-grid">
        <section class="card">
            <div class="section-title">
                <div>
                    <div class="eyebrow">Recent Notices</div>
                    <h2>최근 공지사항</h2>
                </div>
                <a class="btn btn-light" href="/notices">전체 공지</a>
            </div>
            <p class="muted">가장 최근에 올라온 공지사항을 빠르게 확인하세요.</p>
            <div class="directory-grid">
                {notice_cards}
            </div>
        </section>
        <section class="card">
            <div class="eyebrow">Platform Focus</div>
            <h2>이 포털이 우선하는 것</h2>
            <p class="muted">자주 쓰는 기능을 빠르게 찾을 수 있도록 메뉴를 간소화했습니다.</p>
        </section>
    </div>

    <div class="grid">
        <div class="card feature-card"><div><div class="eyebrow">Archive</div><h2>통합 자료</h2><p class="muted">공지사항, 문서자료실, 제휴업체, 회의 공고, 규정을 확인할 수 있습니다.</p></div><a class="btn" href="/archive">열기</a></div>
        <div class="card feature-card"><div><div class="eyebrow">Council</div><h2>대의원 소개</h2><p class="muted">예술대학 학생회 및 전공별 대표자 명단을 확인합니다.</p></div><a class="btn" href="/council">열기</a></div>
        <div class="card feature-card"><div><div class="eyebrow">Voice</div><h2>신문고</h2><p class="muted">건의사항이나 문의를 남길 수 있습니다.</p></div><a class="btn" href="/suggest">열기</a></div>
        <div class="card feature-card"><div><div class="eyebrow">Admin</div><h2>관리자</h2><p class="muted">운영자 전용 페이지입니다.</p></div><a class="btn" href="/admin/login">열기</a></div>
    </div>
    \"\"\"
    return render_layout("국민대학교 예술대학 학생 포털", body)"""

code = re.sub(r'def render_home_page\(\) -> HTMLResponse:.*?(?=def render_archive_page\(\) -> HTMLResponse:)', replace_func, code, flags=re.DOTALL)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(code)
print("Step 1 & 2 Done")
