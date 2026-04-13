import re

with open("main.py", "r", encoding="utf-8") as f:
    c = f.read()

# Fix `@app.post(request: Request, "/council/new")`
c = re.sub(r'@app\.(get|post)\(request: Request, "(.*?)"\)', r'@app.\1("\2")', c)

# Ensure require_admin is correct
c = c.replace("    if require_admin(request): return require_admin(request)\n", "")

def fix_admin(func_code):
    lines = func_code.split('\n')
    for i, line in enumerate(lines):
        if line.startswith("async def"):
            # Ensure request is in args
            if "request: Request" not in line and "request" not in line:
                lines[i] = line.replace("(", "(request: Request, ", 1)
            # Find the closing parenthesis of async def
            j = i
            while not lines[j].endswith("):") and not lines[j].strip().endswith("):"):
                j += 1
            # Add require_admin right after
            lines.insert(j+1, "    if require_admin(request): return require_admin(request)")
            break
    return '\n'.join(lines)

for endpoint in [
    r'@app\.get\("/council/new"\).*?return render_council_form_page\(\)',
    r'@app\.post\("/council/new"\).*?return RedirectResponse\("/council", status_code=302\)',
    r'@app\.get\("/council/\{member_index\}/edit"\).*?return render_council_form_page\(member, member_index\)',
    r'@app\.post\("/council/\{member_index\}/edit"\).*?return RedirectResponse\("/council", status_code=302\)',
    r'@app\.get\("/documents/new"\).*?return render_document_form_page\(\)',
    r'@app\.post\("/documents/new"\).*?return RedirectResponse\("/documents", status_code=302\)',
    r'@app\.get\("/documents/\{document_index\}/edit"\).*?return render_document_edit_form_page\(document, document_index\)',
    r'@app\.post\("/documents/\{document_index\}/edit"\).*?return RedirectResponse\("/documents", status_code=302\)',
    r'@app\.post\("/documents/\{document_index\}/delete"\).*?return RedirectResponse\("/documents", status_code=302\)',
    r'@app\.get\("/meetings/new"\).*?return render_meeting_form_page\(\)',
    r'@app\.post\("/meetings/new"\).*?return RedirectResponse\("/meetings", status_code=302\)',
    r'@app\.get\("/meetings/\{meeting_index\}/edit"\).*?return render_meeting_edit_form_page\(meeting, meeting_index\)',
    r'@app\.post\("/meetings/\{meeting_index\}/edit"\).*?return RedirectResponse\("/meetings", status_code=302\)',
    r'@app\.post\("/meetings/\{meeting_index\}/delete"\).*?return RedirectResponse\("/meetings", status_code=302\)',
    r'@app\.get\("/regulations/new"\).*?return render_regulation_form_page\(\)',
    r'@app\.post\("/regulations/new"\).*?return RedirectResponse\("/regulations", status_code=302\)',
    r'@app\.get\("/regulations/\{regulation_index\}/edit"\).*?return render_regulation_edit_form_page\(regulation, regulation_index\)',
    r'@app\.post\("/regulations/\{regulation_index\}/edit"\).*?return RedirectResponse\("/regulations", status_code=302\)',
    r'@app\.post\("/regulations/\{regulation_index\}/delete"\).*?return RedirectResponse\("/regulations", status_code=302\)'
]:
    c = re.sub(endpoint, lambda m: fix_admin(m.group(0)), c, flags=re.DOTALL)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(c)

