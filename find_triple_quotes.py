
path = r"a:\Desktop\Projects\History-of-all-flight-crash\src\streamlit_app.py"
try:
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if '"""' in line or "'''" in line:
            print(f"{i+1}: {line.strip()}")
except Exception as e:
    print(f"Error: {e}")
