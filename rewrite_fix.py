with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

bad = """branch_cards.append(f'<details class="guide-detail" open><summary>{h(k)} ({len(v)}명)</summary><div class="detail-body" style="padding-top:16px;">{desc_html}<div class="executive-member-list">{rws}</div></div></details>')
} ({len(v)}명)</summary><div class="detail-body" style="padding-top:16px;"><div class="executive-member-list">{rws}</div></div></details>')"""

good = """branch_cards.append(f'<details class="guide-detail" open><summary>{h(k)} ({len(v)}명)</summary><div class="detail-body" style="padding-top:16px;">{desc_html}<div class="executive-member-list">{rws}</div></div></details>')"""

code = code.replace(bad, good)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(code)
