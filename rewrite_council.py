import re

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update major_member_row format
old_row = """rws = "".join(f'<div class="major-member-row" style="align-items:flex-start;"><div><div style="display:flex; align-items:center; gap:8px;"><div class="major-member-role">{h(m.get("role"))}</div><div class="major-member-name">{h(m.get("name"))}</div></div><div style="font-size:13px; color:var(--muted); margin-top:4px;">{h(m.get("email")) or ""}</div></div>{"<a class=\\"btn btn-light\\" style=\\"align-self:center;\\" href=\\"/council/"+str(i)+"/edit\\">수정</a>" if is_adm else ""}</div>' for i, m in mems)"""
new_row = """rws = "".join(f'<div class="major-member-row" style="align-items:flex-start;"><div><div style="font-size:13px; color:var(--muted); margin-bottom:4px;">{h(m.get("role"))}</div><div style="font-size:20px; font-weight:800; margin-bottom:4px; color:var(--text);">{h(m.get("name"))}</div><div style="font-size:13px; color:var(--muted);">{h(m.get("email")) or ""}</div></div>{"<a class=\\"btn btn-light\\" style=\\"align-self:center;\\" href=\\"/council/"+str(i)+"/edit\\">수정</a>" if is_adm else ""}</div>' for i, m in mems)"""

content = content.replace(old_row, new_row)

# 2. Update cluster_cards to NOT be toggles, but just normal divs, since we want one big toggle? 
# Wait, user said "학부별 토글이 아니라 더 큰 단위의 토글". So we should replace the inner `<details>` with `<div>`.
old_cluster = """cluster_cards.append(f'<details class="guide-detail"><summary>{h(c_name)}</summary><div class="detail-body" style="padding-top:16px;"><div class="major-cluster-meta">{", ".join(divs)}</div><div class="major-grid">{"".join(m_units) if m_units else "<div class=\\"card empty\\">없음</div>"}</div></div></details>')"""
new_cluster = """cluster_cards.append(f'<div style="margin-bottom: 24px;"><h4 style="font-size:18px; font-weight:700; margin-bottom:12px;">{h(c_name)} <span style="font-size:14px; font-weight:normal; color:var(--muted);">({", ".join(divs)})</span></h4><div class="major-grid">{"".join(m_units) if m_units else "<div class=\\"card empty\\">없음</div>"}</div></div>')"""

content = content.replace(old_cluster, new_cluster)

# 3. Update branch_cards similarly (remove inner toggles)
old_branch = """branch_cards.append(f'<details class="guide-detail" open><summary>{h(k)} ({len(v)}명)</summary><div class="detail-body" style="padding-top:16px;">{desc_html}<div class="executive-member-list">{rws}</div></div></details>')"""
new_branch = """branch_cards.append(f'<div style="margin-bottom: 24px;"><h4 style="font-size:18px; font-weight:700; margin-bottom:12px;">{h(k)} <span style="font-size:14px; font-weight:normal; color:var(--muted);">({len(v)}명)</span></h4>{desc_html}<div class="executive-member-list">{rws}</div></div>')"""

content = content.replace(old_branch, new_branch)

# 4. Wrap sections in top-level `<details>` instead of `<div class="card council-block-head">`
# Wait, let's find the section bodies
# Current Arts Executive:
old_arts_sec = """    <section id="arts-executive" class="council-block" style="margin-top:18px;">
        <div class="card council-block-head">
            <div>
                <div class="eyebrow">Arts Student Council</div>
                <h3 style="margin:6px 0 0; font-size:22px;">예술대학 학생회</h3>
                <p class="muted" style="margin:8px 0 0; font-size:14px; line-height:1.6;">본 명단은 제28대 예술대학 학생회 [P:ARTS] 구성원입니다.<br>예술대학 학생회실은 <b>예술관 103호</b>에 위치해 있습니다.</p>
            </div>
            {ldr}
            <div class="guide-accordion" style="margin-top:24px;">
                {"".join(branch_cards)}
            </div>
        </div>
    </section>"""

new_arts_sec = """    <section id="arts-executive" class="council-block" style="margin-top:18px;">
        <details class="guide-detail" open>
            <summary style="font-size:20px; font-weight:800;">
                <div>
                    <div class="eyebrow" style="margin-bottom:6px; font-size:12px;">Arts Student Council</div>
                    예술대학 학생회
                </div>
            </summary>
            <div class="detail-body" style="padding-top:16px;">
                <p class="muted" style="margin-bottom:20px; font-size:14px; line-height:1.6;">본 명단은 제28대 예술대학 학생회 [P:ARTS] 구성원입니다.<br>예술대학 학생회실은 <b>예술관 103호</b>에 위치해 있습니다.</p>
                {ldr}
                <div style="margin-top:32px;">
                    {"".join(branch_cards)}
                </div>
            </div>
        </details>
    </section>"""

content = content.replace(old_arts_sec, new_arts_sec)

# Current Major Reps:
old_major_sec = """    <section id="council-members" class="council-block" style="margin-top:18px;">
        <div class="card council-block-head">
            <div class="eyebrow">Representatives</div>
            <h3 style="margin:6px 0 0; font-size:22px;">전공별 대표자</h3>
            <div class="guide-accordion" style="margin-top:24px;">
                {"".join(cluster_cards)}
            </div>
        </div>
    </section>"""

new_major_sec = """    <section id="council-members" class="council-block" style="margin-top:18px;">
        <details class="guide-detail" open>
            <summary style="font-size:20px; font-weight:800;">
                <div>
                    <div class="eyebrow" style="margin-bottom:6px; font-size:12px;">Representatives</div>
                    전공별 대표자
                </div>
            </summary>
            <div class="detail-body" style="padding-top:16px;">
                <div style="margin-top:16px;">
                    {"".join(cluster_cards)}
                </div>
            </div>
        </details>
    </section>"""

content = content.replace(old_major_sec, new_major_sec)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)

