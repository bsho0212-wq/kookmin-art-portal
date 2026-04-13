import re

with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

new_routes = """@app.post("/partners/new")
async def create_partner(
    request: Request,
    name: str = Form(...),
    category: str = Form("기타"),
    benefit: str = Form(...),
    address: str = Form(""),
    map_link: str = Form(""),
    condition: str = Form(""),
    image: UploadFile = File(None),
):
    redirect = require_admin(request)
    if redirect: return redirect
    
    img_path = save_upload(image, "partners")

    partners.insert(0, {
        "name": name,
        "category": category,
        "benefit": benefit,
        "address": address,
        "map_link": map_link,
        "condition": condition,
        "image": img_path,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    save_data()
    return RedirectResponse("/partners", status_code=302)


@app.get("/partners/{partner_index}/edit", response_class=HTMLResponse)
async def partner_edit_form(request: Request, partner_index: int):
    redirect = require_admin(request)
    if redirect: return redirect
    partner = get_item(partners, partner_index)
    if partner is None:
        return render_layout("제휴 수정", '<div class="card empty">존재하지 않는 제휴 정보입니다.</div>')
    return render_partner_edit_form_page(partner, partner_index)


@app.post("/partners/{partner_index}/edit")
async def update_partner(
    request: Request,
    partner_index: int,
    name: str = Form(...),
    category: str = Form("기타"),
    benefit: str = Form(...),
    address: str = Form(""),
    map_link: str = Form(""),
    condition: str = Form(""),
    image: UploadFile = File(None),
):
    redirect = require_admin(request)
    if redirect: return redirect
    partner = get_item(partners, partner_index)
    if partner is not None:
        if image and image.filename:
            delete_uploaded_file(partner.get("image"))
            partner["image"] = save_upload(image, "partners")
        partner.update({
            "name": name,
            "category": category,
            "benefit": benefit,
            "address": address,
            "map_link": map_link,
            "condition": condition,
        })
        save_data()
    return RedirectResponse("/partners", status_code=302)


@app.post("/partners/{partner_index}/delete")
async def delete_partner(request: Request, partner_index: int):
    redirect = require_admin(request)
    if redirect: return redirect
    partner = get_item(partners, partner_index)
    if partner is not None:
        delete_uploaded_file(partner.get("image"))
        partners.pop(partner_index)
        save_data()
    return RedirectResponse("/partners", status_code=302)"""

code = re.sub(r'@app\.post\("/partners/new"\).*?return RedirectResponse\("/partners", status_code=302\)', new_routes, code, flags=re.DOTALL)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Partner routes done")
