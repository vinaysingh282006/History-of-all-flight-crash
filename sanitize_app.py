
import os

file_path = r"a:\Desktop\Projects\History-of-all-flight-crash\src\streamlit_app.py"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Keep only ASCII characters
    sanitized_content = content.encode('ascii', 'ignore').decode('ascii')
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(sanitized_content)
        
    print(f"Successfully sanitized {file_path}")
    
except Exception as e:
    print(f"Error sanitizing file: {e}")
