import os, glob

for p in glob.glob('src/**/*.py', recursive=True):
    try:
        text = open(p, encoding='utf-8').read()
        lines = text.split('\n')
        changed = False
        for i, line in enumerate(lines):
            if 'Swallowed error' in line and '.error(' in line:
                lines[i] = line.replace('.error(', '.warning(')
                changed = True
        
        if changed:
            open(p, 'w', encoding='utf-8').write('\n'.join(lines))
            print("Fixed", p)
    except Exception as e:
        print("Error on", p, e)
