import re
import os

with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

# Update document_list endpoint to pass request
code = code.replace(
    'def document_list(request: Request):\n    return render_documents_page()',
    'def document_list(request: Request):\n    return render_documents_page(request)'
)

# Replace render_documents_page
new_docs = """def render_documents_page(request: Request) -> HTMLResponse:
    items = []
    is_adm = is_admin(request)
    admin_actions_top = '<a class="btn" href="/documents/new">문서 업로드</a>' if is_adm else ''
    
    for idx, d in enumerate(documents):
        download_button = f'<a class="btn" href="{h(d.get("file"))}">다운로드</a>' if d.get("file") else ''
        
        manage_html = f'''
            <a class="btn btn-light" href="/documents/{idx}/edit">수정</a>
            <form class="inline-form" action="/documents/{idx}/delete" method="post">
                <button class="btn btn-light" type="submit">삭제</button>
            </form>
        ''' if is_adm else ''
        
        items.append(f'''
        <div class="card">
            <div class="section-title">
                <h2>{h(d.get('title'))}</h2>
                <span class="pill">{h(d.get('category'))}</span>
            </div>
            <p>{h(d.get('description'))}</p>
            <div class="meta">등록일 {h(d.get('created_at'))}</div>
            <div class="actions">
                {download_button}
                {manage_html}
            </div>
        </div>
        ''')
    if not items:
        items.append('<div class="card empty">등록된 문서가 없습니다.</div>')
    body = f\"\"\"
    <div class="hero">
        <div class="eyebrow">Document Archive</div>
        <h2>문서자료실</h2>
        <p>학우 여러분이 학교생활이나 행정 처리 중 필요한 문서 양식을 내려받을 수 있는 공간입니다.</p>
        <div class="actions">
            {admin_actions_top}
        </div>
    </div>
    {''.join(items)}
    \"\"\"
    return render_layout("문서자료실", body)"""

code = re.sub(r'def render_documents_page\(\) -> HTMLResponse:.*?(?=def render_document_form_page)', new_docs, code, flags=re.DOTALL)

# Update descriptions in regulations_page
code = code.replace(
    '<h2>규정을 그냥 나열하지 않고, 학생이 실제로 행동할 수 있는 단위로 다시 풀었습니다.</h2>',
    '<h2>자주 묻는 학생회 규정과 권리를 확인하세요.</h2>'
)
code = code.replace(
    '<p>원문 규정은 그대로 유지하되, 학생이 자주 묻게 되는 질문을 먼저 클릭해서 확인할 수 있도록 재구성했습니다. 특히 전체학생대표자회의 소집, 학생의 권리, 의결기구의 차이처럼 실제 운영에서 자주 헷갈리는 부분을 먼저 읽을 수 있게 했습니다.</p>',
    '<p>어렵게 느껴질 수 있는 학생회 규정을, 학우 여러분의 권리와 궁금증을 중심으로 쉽게 풀었습니다. 필요한 상황에 맞춰 읽어보세요.</p>'
)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(code)
print("Docs & Descriptions Done")
