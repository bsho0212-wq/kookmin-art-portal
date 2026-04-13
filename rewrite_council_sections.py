import re

with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

# Replace Arts Executive Section
arts_pattern = r'<section id="arts-executive" class="council-block" style="margin-top:18px;">.*?</section>'
arts_replacement = """<section id="arts-executive" class="council-block" style="margin-top:18px;">
        <details class="guide-detail" open>
            <summary style="font-size:22px; font-weight:800; padding:20px;">
                <div style="display:flex; flex-direction:column; gap:4px; align-items:flex-start;">
                    <span class="eyebrow" style="font-size:12px;">Arts Student Council</span>
                    <span>예술대학 학생회</span>
                </div>
            </summary>
            <div class="detail-body">
                <p class="muted" style="margin-bottom:20px;">예술대학 소속 학생들을 위해 행정, 기획, 소통을 담당하는 학생회 명단입니다.</p>
                <div class="executive-hierarchy">
                    <section class="executive-top" style="margin-bottom:16px;">
                        <div class="eyebrow" style="color:rgba(255,255,255,0.74);">Leadership</div>
                        <h3>비대위원장단</h3>
                        <p>예술대학 학생회를 총괄합니다.</p>
                        <div class="executive-top-members">{ldr}</div>
                    </section>
                    <div class="exec-grid" style="margin-top:24px;">{"".join(branch_cards)}</div>
                </div>
            </div>
        </details>
    </section>"""
code = re.sub(arts_pattern, arts_replacement, code, flags=re.DOTALL)

# Replace Major Reps Section
major_pattern = r'<section id="council-members" class="council-block" style="margin-top:24px;">.*?</section>'
major_replacement = """<section id="council-members" class="council-block" style="margin-top:24px;">
        <details class="guide-detail" open>
            <summary style="font-size:22px; font-weight:800; padding:20px;">
                <div style="display:flex; flex-direction:column; gap:4px; align-items:flex-start;">
                    <span class="eyebrow" style="font-size:12px;">Representative List</span>
                    <span>전공별 대표자</span>
                </div>
            </summary>
            <div class="detail-body">
                <p class="muted" style="margin-bottom:20px;">각 전공을 대표하여 의견을 조율하고 활동하는 대표자 명단입니다.</p>
                <div class="guide-accordion">{"".join(cluster_cards)}</div>
            </div>
        </details>
    </section>"""
code = re.sub(major_pattern, major_replacement, code, flags=re.DOTALL)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(code)

