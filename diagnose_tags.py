
import re

try:
    with open('templates/exams/exams.html', 'rb') as f:
        content = f.read()
        
    s_content = content.decode('utf-8')
    
    # Find all {{ ... }} tags
    matches = re.finditer(r'\{\{.*?\}\}', s_content, re.DOTALL)
    
    found_split = False
    for m in matches:
        tag = m.group(0)
        if '\n' in tag or '\r' in tag:
            print(f"FOUND SPLIT TAG at index {m.start()}: {repr(tag)}")
            found_split = True
            
    if not found_split:
        print("No split tags found.")
        
except Exception as e:
    print(f"Error: {e}")
