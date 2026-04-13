import re

with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update ARTS_EXECUTIVE_GROUPS default data to use "국장" instead of "국원" for the first member
new_exec_groups = """ARTS_EXECUTIVE_GROUPS = {
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
}"""

code = re.sub(r'ARTS_EXECUTIVE_GROUPS = \{.*?"복지소통국": \[.*?\]\n\}', new_exec_groups, code, flags=re.DOTALL)

# 2. Add descriptions for each bureau
descriptions = {
    "연합기획국": "교내 교류 활성화 및 행사, 행정을 기획하고 활동하는 부서입니다.",
    "홍보국": "학생회 활동을 홍보하고 학생들이 참여할 수 있는 행사, 복지 등을 안내하는 부서입니다.",
    "행정사무국": "예산 처리 및 기획안 작성 등 문서 업무를 담당하고 아이디어를 실제화하기 위해 노력하는 부서입니다.",
    "복지소통국": "복지 상태를 점검하고 필요한 복지를 기획·검토하며, 학생들과 적극적으로 소통하여 의견을 수렴하는 부서입니다."
}

# 3. Update the render_council_page function to include the descriptions
# Currently inside render_council_page:
# branch_cards.append(f'<details class="guide-detail" open><summary>{h(k)} ({len(v)}명)</summary><div class="detail-body" style="padding-top:16px;"><div class="executive-member-list">{rws}</div></div></details>')

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
        rws = "".join(f'<div class="executive-member-row"><span class="executive-member-role">{h(m.get("role"))}</span><span class="executive-member-name">{h(m.get("name"))}</span></div>' for m in s_exec(v))
        desc_html = f'<p class="muted" style="margin-bottom:12px; font-size:14px; line-height:1.6;">{desc_map.get(k, "")}</p>' if k in desc_map else ""
        branch_cards.append(f'<details class="guide-detail" open><summary>{h(k)} ({len(v)}명)</summary><div class="detail-body" style="padding-top:16px;">{desc_html}<div class="executive-member-list">{rws}</div></div></details>')
"""

code = re.sub(r'branch_cards = \[\]\n    for k, v in ARTS_EXECUTIVE_GROUPS\.items\(\):\n.*?branch_cards\.append\(.*?\)', new_branch_logic, code, flags=re.DOTALL)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Council desc updated.")
