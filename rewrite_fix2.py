with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

bad = """cluster_cards.append(f'<details class="guide-detail"><summary>{h(c_name)}</summary><div class="detail-body" style="padding-top:16px;"><div class="major-cluster-meta">{", ".join(divs)}</div><div class="major-grid">{"".join(m_units) if m_units else "<div class=\\"card empty\\">없음</div>"}</div></div></details>')
}</summary><div class="detail-body" style="padding-top:16px;"><div class="major-cluster-meta">{", ".join(divs)}</div><div class="major-grid">{"".join(m_units) if m_units else "<div class=\\"card empty\\">없음</div>"}</div></div></details>')"""

good = """cluster_cards.append(f'<details class="guide-detail"><summary>{h(c_name)}</summary><div class="detail-body" style="padding-top:16px;"><div class="major-cluster-meta">{", ".join(divs)}</div><div class="major-grid">{"".join(m_units) if m_units else "<div class=\\"card empty\\">없음</div>"}</div></div></details>')"""

code = code.replace(bad, good)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(code)

