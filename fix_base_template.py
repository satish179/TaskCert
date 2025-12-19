
filename = r"c:\Python\Scripts\application - Copy\templates\base.html"

with open(filename, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if skip:
        skip = False
        continue
        
    # Check for the specific problematic split block
    # Line 152: <div ... {% block container_style
    # Line 153: %}style...
    
    if '{% block container_style' in line and not '%}' in line.split('container_style')[1]:
        # Found the start of the split block
        # Checks if next line completes it
        if i + 1 < len(lines) and '%}' in lines[i+1]:
            # Merge them
            line1 = line.rstrip()
            line2 = lines[i+1].lstrip()
            # line2 probably starts with %}style...
            
            merged = line1 + ' ' + line2 + '\n'
            # We want to ensure it looks like: ... {% block container_style %}style="max-width: 1400px;"{% endblock %}>
            # The current content might be messy.
            
            # Let's just hardcode the correct line for this specific div since we know what it should be.
            # It should be:
            #             <div class="{% block container_classes %}container-fluid{% endblock %}" {% block container_style %}style="max-width: 1400px;"{% endblock %}>
            
            indent = line[:line.find('<')]
            replacement = f'{indent}<div class="{{% block container_classes %}}container-fluid{{% endblock %}}" {{% block container_style %}}style="max-width: 1400px;"{{% endblock %}}>\n'
            
            new_lines.append(replacement)
            skip = True # Skip next line
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

with open(filename, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("base.html patched successfully.")
