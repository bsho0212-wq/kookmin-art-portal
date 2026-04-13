import re

with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

# Restore `app = FastAPI()` 
if "\napp = FastAPI()" not in code:
    code = code.replace("from fastapi import FastAPI, File, Form, Request, UploadFile", "from fastapi import FastAPI, File, Form, Request, UploadFile\napp = FastAPI()")

with open("main.py", "w", encoding="utf-8") as f:
    f.write(code)

