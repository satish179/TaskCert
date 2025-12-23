#!/usr/bin/env python3
"""Fix split Django template tags in exams.html"""

filepath = r"c:\Python\Scripts\application - Copy\templates\exams\exams.html"

# Read the file
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: exam.name (lines 404-405)
content = content.replace(
    '<h5 style="color: var(--primary); font-weight: 700;"><i class="fas fa-graduation-cap"></i> {{ exam.name\n                    }}</h5>',
    '<h5 style="color: var(--primary); font-weight: 700;"><i class="fas fa-graduation-cap"></i> {{ exam.name }}</h5>'
)

# Fix 2: exam.questions.count (lines 414-415)
content = content.replace(
    '<i class="fas fa-list text-primary center-icon" style="width:20px"></i> <span><strong>{{\n                                exam.questions.count }}</strong> Questions</span>',
    '<i class="fas fa-list text-primary center-icon" style="width:20px"></i> <span><strong>{{ exam.questions.count }}</strong> Questions</span>'
)

# Fix 3: attempt_counts (lines 430-431)
content = content.replace(
    '<span class="badge bg-light text-primary border"><i class="fas fa-rotate"></i> Attempts: {{\n                        attempt_counts|dict_get:exam.id|default:"0" }}</span>',
    '<span class="badge bg-light text-primary border"><i class="fas fa-rotate"></i> Attempts: {{ attempt_counts|dict_get:exam.id|default:"0" }}</span>'
)

# Write back
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed 3 split template tags in exams.html")
