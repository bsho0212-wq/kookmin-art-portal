import re

with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

bad_exec = """ARTS_EXECUTIVE_GROUPS = {
    "비대위원장단": [
        {"role": "비대위원장", "name": "미정"},
        {"role": "부비대위원장", "name": "미정"},
    ],
    "연합기획국": [
        {"role": "국원", "name": "미정"},
        {"role": "국원", "name": "미정"},
        {"role": "국원", "name": "미정"},
    ],
    "홍보국": [
        {"role": "국원", "name": "미정"},
        {"role": "국원", "name": "미정"},
        {"role": "국원", "name": "미정"},
    ],
    "행정사무국": [
        {"role": "국원", "name": "미정"},
        {"role": "국원", "name": "미정"},
    ],
    "복지소통국": [
        {"role": "국원", "name": "미정"},
        {"role": "국원", "name": "미정"},
    ],
}"""

good_exec = """ARTS_EXECUTIVE_GROUPS = {
    "비대위원장단": [
        {"role": "비대위원장", "name": "미정"},
        {"role": "부비대위원장", "name": "미정"},
    ],
    "연합기획국": [
        {"role": "국장", "name": "미정"},
        {"role": "국원", "name": "미정"},
        {"role": "국원", "name": "미정"},
    ],
    "홍보국": [
        {"role": "국장", "name": "미정"},
        {"role": "국원", "name": "미정"},
        {"role": "국원", "name": "미정"},
    ],
    "행정사무국": [
        {"role": "국장", "name": "미정"},
        {"role": "국원", "name": "미정"},
    ],
    "복지소통국": [
        {"role": "국장", "name": "미정"},
        {"role": "국원", "name": "미정"},
    ],
}"""

code = code.replace(bad_exec, good_exec)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(code)
