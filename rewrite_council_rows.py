import re

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update major_member_row format
old_row = """rws = "".join(f'<div class="major-member-row" style="align-items:flex-start;"><div><div style="display:flex; align-items:center; gap:8px;"><div class="major-member-role">{h(m.get("role"))}</div><div class="major-member-name">{h(m.get("name"))}</div></div><div style="font-size:13px; color:var(--muted); margin-top:4px;">{h(m.get("email")) or ""}</div></div>{"<a class=\\"btn btn-light\\" style=\\"align-self:center;\\" href=\\"/council/"+str(i)+"/edit\\">수정</a>" if is_adm else ""}</div>' for i, m in mems)"""
new_row = """rws = "".join(f'<div class="major-member-row" style="align-items:flex-start;"><div><div style="font-size:13px; color:var(--muted); margin-bottom:4px;">{h(m.get("role"))}</div><div style="font-size:20px; font-weight:800; margin-bottom:4px; color:var(--text);">{h(m.get("name"))}</div><div style="font-size:13px; color:var(--muted);">{h(m.get("email")) or ""}</div></div>{"<a class=\\"btn btn-light\\" style=\\"align-self:center;\\" href=\\"/council/"+str(i)+"/edit\\">수정</a>" if is_adm else ""}</div>' for i, m in mems)"""

content = content.replace(old_row, new_row)

# 2. Update cluster_cards to NOT be toggles, but just normal divs
old_cluster = """cluster_cards.append(f'<details class="guide-detail"><summary>{h(c_name)}</summary><div class="detail-body" style="padding-top:16px;"><div class="major-cluster-meta">{", ".join(divs)}</div><div class="major-grid">{"".join(m_units) if m_units else "<div class=\\"card empty\\">없음</div>"}</div></div></details>')"""
new_cluster = """cluster_cards.append(f'<div style="margin-bottom: 24px;"><h4 style="font-size:18px; font-weight:700; margin-bottom:12px;">{h(c_name)} <span style="font-size:14px; font-weight:normal; color:var(--muted);">({", ".join(divs)})</span></h4><div class="major-grid">{"".join(m_units) if m_units else "<div class=\\"card empty\\">없음</div>"}</div></div>')"""

content = content.replace(old_cluster, new_cluster)

# 3. Update branch_cards similarly (remove inner toggles)
old_branch = """branch_cards.append(f'<details class="guide-detail" open><summary>{h(k)} ({len(v)}명)</summary><div class="detail-body" style="padding-top:16px;">{desc_html}<div class="executive-member-list">{rws}</div></div></details>')"""
new_branch = """branch_cards.append(f'<div style="margin-bottom: 24px; background:white; padding:20px; border-radius:16px; box-shadow:var(--shadow-soft);"><h4 style="font-size:18px; font-weight:700; margin-bottom:12px;">{h(k)} <span style="font-size:14px; font-weight:normal; color:var(--muted);">({len(v)}명)</span></h4>{desc_html}<div class="executive-member-list">{rws}</div></div>')"""

content = content.replace(old_branch, new_branch)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)

