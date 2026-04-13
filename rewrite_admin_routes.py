import re

with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

def inject_admin_check(func_def):
    # Find the function signature, e.g. async def create_council_member(...)
    # and inject redirect = require_admin(request)
    match = re.search(r'async def ([a-zA-Z0-9_]+)\(', func_def)
    if not match:
        return func_def
    
    # ensure request: Request is in the signature if not present
    if "request: Request" not in func_def:
        func_def = re.sub(r'async def ([a-zA-Z0-9_]+)\(', r'async def \1(\n    request: Request,', func_def, 1)
        
    # inject the require_admin check after the colon
    inject = "\n    redirect = require_admin(request)\n    if redirect: return redirect\n"
    func_def = re.sub(r'(async def .*?:)', r'\1' + inject, func_def, 1, flags=re.DOTALL)
    return func_def

# List of endpoints to secure
routes_to_secure = [
    r'@app\.get\("/council/new".*?return render_council_form_page\(\)',
    r'@app\.post\("/council/new"\).*?return RedirectResponse\("/council", status_code=302\)',
    r'@app\.get\("/council/\{member_index\}/edit".*?return render_council_form_page\(member, member_index\)',
    r'@app\.post\("/council/\{member_index\}/edit"\).*?return RedirectResponse\("/council", status_code=302\)',
    
    r'@app\.get\("/documents/new".*?return render_document_form_page\(\)',
    r'@app\.post\("/documents/new"\).*?return RedirectResponse\("/documents", status_code=302\)',
    r'@app\.get\("/documents/\{document_index\}/edit".*?return render_document_edit_form_page\(document, document_index\)',
    r'@app\.post\("/documents/\{document_index\}/edit"\).*?return RedirectResponse\("/documents", status_code=302\)',
    r'@app\.post\("/documents/\{document_index\}/delete"\).*?return RedirectResponse\("/documents", status_code=302\)',
    
    r'@app\.get\("/meetings/new".*?return render_meeting_form_page\(\)',
    r'@app\.post\("/meetings/new"\).*?return RedirectResponse\("/meetings", status_code=302\)',
    r'@app\.get\("/meetings/\{meeting_index\}/edit".*?return render_meeting_edit_form_page\(meeting, meeting_index\)',
    r'@app\.post\("/meetings/\{meeting_index\}/edit"\).*?return RedirectResponse\("/meetings", status_code=302\)',
    r'@app\.post\("/meetings/\{meeting_index\}/delete"\).*?return RedirectResponse\("/meetings", status_code=302\)',

    r'@app\.get\("/regulations/new".*?return render_regulation_form_page\(\)',
    r'@app\.post\("/regulations/new"\).*?return RedirectResponse\("/regulations", status_code=302\)',
    r'@app\.get\("/regulations/\{regulation_index\}/edit".*?return render_regulation_edit_form_page\(regulation, regulation_index\)',
    r'@app\.post\("/regulations/\{regulation_index\}/edit"\).*?return RedirectResponse\("/regulations", status_code=302\)',
    r'@app\.post\("/regulations/\{regulation_index\}/delete"\).*?return RedirectResponse\("/regulations", status_code=302\)',
]

for pattern in routes_to_secure:
    # only replace if not already secured
    def replacer(m):
        text = m.group(0)
        if "require_admin" in text:
            return text
        return inject_admin_check(text)
        
    code = re.sub(pattern, replacer, code, flags=re.DOTALL)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Secured routes")
