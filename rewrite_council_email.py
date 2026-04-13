import re

with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

# Modify the render_council_page logic to show emails below the member's name
new_branch_logic = """
    desc_map = {
        "연합기획국": "교내 교류 활성화 및 행사, 행정을 기획하고 활동하는 부서입니다.",
        "홍보국": "학생회 활동을 홍보하고 학생들이 참여할 수 있는 행사, 복지 등을 안내하는 부서입니다.",
        "행정사무국": "예산 처리 및 기획안 작성 등 문서 업무를 담당하고 아이디어를 실제화하기 위해 노력하는 부서입니다.",
        "복지소통국": "복지 상태를 점검하고 필요한 복지를 기획·검토하며, 학생들과 적극적으로 소통하여 의견을 수렴하는 부서입니다."
    }

    branch_cards = []
    for k, v in ARTS_EXECUTIVE_GROUPS.items():
        if k == "비대위원장단": continue
        rws = "".join(f'<div class="executive-member-row"><div style="display:flex; flex-direction:column; gap:4px;"><div style="display:flex; align-items:center; gap:8px;"><span class="executive-member-role">{h(m.get("role"))}</span><span class="executive-member-name">{h(m.get("name"))}</span></div><span style="font-size:13px; color:var(--muted);">{h(m.get("email")) or ""}</span></div></div>' for m in s_exec(v))
        desc_html = f'<p class="muted" style="margin-bottom:12px; font-size:14px; line-height:1.6;">{desc_map.get(k, "")}</p>' if k in desc_map else ""
        branch_cards.append(f'<details class="guide-detail" open><summary>{h(k)} ({len(v)}명)</summary><div class="detail-body" style="padding-top:16px;">{desc_html}<div class="executive-member-list">{rws}</div></div></details>')
    
    ldr = "".join(f'<div class="executive-top-member"><div style="display:flex; flex-direction:column; gap:4px; text-align:left;"><div style="display:flex; align-items:center; gap:8px;"><span class="executive-top-role">{h(m.get("role"))}</span><span class="executive-top-name">{h(m.get("name"))}</span></div><span style="font-size:13px; color:rgba(255,255,255,0.7);">{h(m.get("email")) or ""}</span></div></div>' for m in s_exec(ARTS_EXECUTIVE_GROUPS.get("비대위원장단", [])))
    
    major_clusters = [("공연예술학부", ["영화전공", "연극전공", "무용전공"]),("미술학부", ["회화전공", "입체미술전공"]),("음악학부", ["관현악전공", "피아노전공", "성악전공", "작곡전공"])]
    cluster_cards = []
    for c_name, divs in major_clusters:
        m_units = []
        for d in divs:
            mems = [(i, m) for i, m in enumerate(council_members) if m.get("division") == d]
            if not mems: continue
            rws = "".join(f'<div class="major-member-row" style="align-items:flex-start;"><div><div style="display:flex; align-items:center; gap:8px;"><div class="major-member-role">{h(m.get("role"))}</div><div class="major-member-name">{h(m.get("name"))}</div></div><div style="font-size:13px; color:var(--muted); margin-top:4px;">{h(m.get("email")) or ""}</div></div>{"<a class=\\"btn btn-light\\" style=\\"align-self:center;\\" href=\\"/council/"+str(i)+"/edit\\">수정</a>" if is_adm else ""}</div>' for i, m in mems)
            m_units.append(f'<section class="major-unit"><h4>{h(d)}</h4><div class="major-member-pair">{rws}</div></section>')
        cluster_cards.append(f'<details class="guide-detail"><summary>{h(c_name)}</summary><div class="detail-body" style="padding-top:16px;"><div class="major-cluster-meta">{", ".join(divs)}</div><div class="major-grid">{"".join(m_units) if m_units else "<div class=\\"card empty\\">없음</div>"}</div></div></details>')
"""

code = re.sub(r'    desc_map = \{.*?cluster_cards\.append\(.*?\)', new_branch_logic, code, flags=re.DOTALL)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Council email updated.")
