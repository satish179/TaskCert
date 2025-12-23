
import re
import os

file_path = 'templates/exams/exams.html'

def normalize_tag(match):
    # Get content inside {{ }}
    inner = match.group(1)
    # Collapse all whitespace to single spaces, removing newlines
    cleaned = ' '.join(inner.split())
    return f'{{{{ {cleaned} }}}}'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find {{ ... }} possibly spanning multiple lines
    # ungreedy match .*? with DOTALL
    new_content = re.sub(r'\{\{(.*?)\}\}', normalize_tag, content, flags=re.DOTALL)
    
    # Also fix any "Pass Score:" split or similar text issues if they exist
    # (The user mentioned "Code like structure" might refer to text too?)
    # But {{ }} is the main issues.
    
    if content != new_content:
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(new_content)
        print("Successfully normalized template tags.")
    else:
        print("No changes needed (regex didn't find split tags matching pattern).")

except Exception as e:
    print(f"Error: {e}")
