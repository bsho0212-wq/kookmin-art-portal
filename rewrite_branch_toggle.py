import re

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

old_branch = """branch_cards.append(f'<div style="margin-bottom: 24px;"><h4 style="font-size:18px; font-weight:700; margin-bottom:12px;">{h(k)} <span style="font-size:14px; font-weight:normal; color:var(--muted);">({len(v)}명)</span></h4>{desc_html}<div class="executive-member-list">{rws}</div></div>')"""

# We can use a nested details tag. We can style it similar to guide-detail or just use guide-detail.
# If we use guide-detail, it has white background and border, which is fine inside the detail-body since the background there is transparent/grayish.
# Actually, the user liked it when they were toggles. Let's use guide-detail class again, but maybe not open by default to save space, or open by default if we want.
new_branch = """branch_cards.append(f'<details class="guide-detail" open style="margin-bottom: 12px;"><summary style="font-size:16px; padding:16px;">{h(k)} <span style="font-size:14px; font-weight:normal; color:var(--muted);">({len(v)}명)</span></summary><div class="detail-body" style="padding-top:0px;">{desc_html}<div class="executive-member-list">{rws}</div></div></details>')"""

content = content.replace(old_branch, new_branch)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)

