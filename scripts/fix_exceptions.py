import os

def fix_exceptions(directories):
    count = 0
    for d in directories:
        for root, dirs, files in os.walk(d):
            if 'node_modules' in root or '.git' in root or 'frontend' in root or '.venv' in root:
                continue
                
            for file in files:
                if not file.endswith('.py'):
                    continue
                    
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                original_content = content
                
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.strip() == 'except Exception:':
                        if i + 1 < len(lines) and lines[i+1].strip() == 'pass':
                            indent = line[:len(line) - len(line.lstrip())]
                            lines[i] = f'{indent}except Exception as e:'
                            pass_indent = lines[i+1][:len(lines[i+1]) - len(lines[i+1].lstrip())]
                            lines[i+1] = f'{pass_indent}import logging; logging.getLogger(__name__).exception(f"Swallowed error in {file}: {{e}}")'
                            count += 1
                    elif line.strip().startswith('except Exception as ') and line.strip().endswith(':'):
                        if i + 1 < len(lines) and lines[i+1].strip() == 'pass':
                            var_name = line.strip().split(' as ')[1][:-1]
                            pass_indent = lines[i+1][:len(lines[i+1]) - len(lines[i+1].lstrip())]
                            lines[i+1] = f'{pass_indent}import logging; logging.getLogger(__name__).exception(f"Swallowed error in {file}: {{{var_name}}}")'
                            count += 1

                new_content = '\n'.join(lines)
                if new_content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)

    print(f"Fixed {count} instances of swallowed exceptions.")

if __name__ == '__main__':
    fix_exceptions(['src', 'scripts', 'tests', '.'])
