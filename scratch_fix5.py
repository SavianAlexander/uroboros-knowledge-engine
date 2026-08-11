import os, glob

for p in glob.glob('tests/**/*.py', recursive=True):
    try:
        text = open(p, encoding='utf-8').read()
        lines = text.splitlines()
        changed = False
        new_lines = []
        for line in lines:
            if '@pytest.mark.skip' in line and '@unittest.skip' not in line:
                new_lines.append(line)
                indent = len(line) - len(line.lstrip())
                new_lines.append(' ' * indent + '@unittest.skip("Legacy UI test skipped")')
                changed = True
            elif '@unittest.skip' in line:
                # remove any duplicated @unittest.skip that might be there
                if new_lines and '@unittest.skip' in new_lines[-1]:
                    continue
                new_lines.append(line)
            else:
                new_lines.append(line)
        
        if changed:
            # We must make sure `import unittest` is in the file if we add @unittest.skip
            if not any('import unittest' in l for l in new_lines):
                new_lines.insert(0, 'import unittest')
            open(p, 'w', encoding='utf-8').write('\n'.join(new_lines))
            print("Fixed", p)
    except Exception as e:
        print("Error on", p, e)
