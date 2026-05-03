import os

template_dir = 'reports/templates/reports'

for filename in os.listdir(template_dir):
    if not filename.endswith('.html'):
        continue
        
    path = os.path.join(template_dir, filename)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix the missing %
    fixed_content = content.replace(' }<', ' %}<')
    fixed_content = fixed_content.replace(' } ', ' %} ')
    fixed_content = fixed_content.replace(' }<', ' %}<') # duplicate for safety
    fixed_content = fixed_content.replace('" }', '" %}')

    if content != fixed_content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

print("Fixed")
