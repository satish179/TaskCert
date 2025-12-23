import re
import os

filepath = r"c:\Python\Scripts\application - Copy\templates\exams\exams.html"

if not os.path.exists(filepath):
    print(f"Error: File not found at {filepath}")
    exit(1)

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

original_len = len(content)
print(f"Read {original_len} bytes.")

# Regex 1: exam.name
# Pattern: {{ exam.name <whitespace/newlines> }}
# We want to match explicitly the split case to be sure
pattern1 = r'\{\{\s*exam\.name\s*\}\}'
new_content, n1 = re.subn(pattern1, '{{ exam.name }}', content, flags=re.DOTALL)
print(f"exam.name replacements: {n1}")
content = new_content

# Regex 2: exam.questions.count
# Pattern: {{ <whitespace> exam.questions.count <whitespace> }}
pattern2 = r'\{\{\s*exam\.questions\.count\s*\}\}'
new_content, n2 = re.subn(pattern2, '{{ exam.questions.count }}', content, flags=re.DOTALL)
print(f"exam.questions.count replacements: {n2}")
content = new_content

# Regex 3: attempt_counts
# Pattern: {{ <whitespace> attempt_counts... <whitespace> }}
pattern3 = r'\{\{\s*attempt_counts\|dict_get:exam\.id\|default:"0"\s*\}\}'
new_content, n3 = re.subn(pattern3, '{{ attempt_counts|dict_get:exam.id|default:"0" }}', content, flags=re.DOTALL)
print(f"attempt_counts replacements: {n3}")
content = new_content

if len(content) == original_len:
    print("Warning: Content length unchanged (might be fine if only whitespace removed, but suspicious if no replacements)")

if n1 + n2 + n3 == 0:
    print("ERROR: No replacements made! Regex failed to match.")
    # Debug: print snippet around line 404
    start_idx = content.find('exam.name')
    if start_idx != -1:
        print(f"Snippet around exam.name:\n{content[start_idx-20:start_idx+50]!r}")
else:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updates written to file.")
