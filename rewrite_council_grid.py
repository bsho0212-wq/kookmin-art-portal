import re

with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Find the section where we generate the branch cards (예술대학 학생회 각 국 렌더링 부분)
# Currently it looks something like this:
# branch_cards.append(f'<details class="guide-detail" open><summary>{h(k)} ({len(v)}명)</summary><div class="detail-body" style="padding-top:16px;"><div class="executive-member-list">{rws}</div></div></details>')
#
# We want to change the executive hierarchy so the branches sit in a 2-column grid.

new_council_str = """def render_council_page(request: Request) -> HTMLResponse:
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
        <h2>예술대학 학생회 및 대표자 안내</h2>
        <p>학우 여러분을 위해 일하는 예술대학 학생회와 각 전공 대표자 명단입니다.</p>
        <div class="council-section-anchor">
            <a class="btn btn-light" href="#arts-executive">학생회 명단</a>
            <a class="btn btn-light" href="#council-members">대표자 명단</a>
            {"<a class=\\"btn\\" href=\\"/council/new\\">대표자 추가</a>" if is_adm else ""}
        </div>
    </div>
    
    <section id="arts-executive" class="council-block" style="margin-top:18px;">
        <div class="card council-block-head">
            <div>
                <div class="eyebrow">Arts Student Council</div>
                <h2>예술대학 학생회</h2>
            </div>
        </div>
        <p class="muted">예술대학 소속 학생들을 위해 행정, 기획, 소통을 담당하는 학생회 명단입니다.</p>
        <div class="executive-hierarchy">
            <section class="executive-top" style="margin-bottom:16px;">
                <div class="eyebrow" style="color:rgba(255,255,255,0.74);">Leadership</div>
                <h3>비대위원장단</h3>
                <p>예술대학 학생회를 총괄합니다.</p>
                <div class="executive-top-members">{ldr}</div>
            </section>
            <div class="exec-grid">{"".join(branch_cards)}</div>
        </div>
    </section>
    
    <section id="council-members" class="council-block" style="margin-top:24px;">
        <div class="card council-block-head">
            <div>
                <div class="eyebrow">Representative List</div>
                <h2>전공별 대표자</h2>
            </div>
        </div>
        <p class="muted">각 전공을 대표하여 의견을 조율하고 활동하는 대표자 명단입니다.</p>
        <div class="guide-accordion">{"".join(cluster_cards)}</div>
    </section>'''
    return render_layout("대의원 소개", body)"""

code = re.sub(r'def render_council_page\(\w*:?.*?\) -> HTMLResponse:.*?(?=def render_council_form_page)', new_council_str + '\n\n', code, flags=re.DOTALL)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Council grid updated.")
