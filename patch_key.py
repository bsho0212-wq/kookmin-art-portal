with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

old_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt3d29rd295cXlnYmNyY3N5eW9iIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU5ODgyMjQsImV4cCI6MjA5MTU2NDIyNH0.q08r-pVhgw_7P0z-yjlj99yTrqGnvqJZzVLDPsvMgos'
new_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt3d29rd295cXlnYmNyY3N5eW9iIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTk4ODIyNCwiZXhwIjoyMDkxNTY0MjI0fQ.8eP2BSCzu5AMlamlsi2-2pKmmEPAyD4-ljbwyMk-TSU'

content = content.replace(old_key, new_key)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Key updated")
