import os
import re

def inject_loggers(directories):
    count = 0
    for d in directories:
        for root, dirs, files in os.walk(d):
            if any(ignore in root for ignore in ['node_modules', '.git', 'frontend', '.venv']):
                continue
                
            for file in files:
                if not file.endswith('.py'):
                    continue
                    
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.read().split('\n')
                    
                new_lines = []
                modified = False
                i = 0
                while i < len(lines):
                    line = lines[i]
                    new_lines.append(line)
                    
                    if line.strip() == 'except Exception:' or (line.strip().startswith('except Exception as') and line.strip().endswith(':')):
                        # It's a bare exception block! Let's inject a log line.
                        # We need to figure out the indentation of the NEXT line.
                        next_i = i + 1
                        while next_i < len(lines) and (not lines[next_i].strip() or lines[next_i].strip().startswith('#')):
                            new_lines.append(lines[next_i])
                            next_i += 1
                            
                        if next_i < len(lines):
                            indent = lines[next_i][:len(lines[next_i]) - len(lines[next_i].lstrip())]
                            # Inject logger
                            if line.strip() == 'except Exception:':
                                inject = f'{indent}import logging; logging.getLogger(__name__).exception("Swallowed error in {file}")'
                            else:
                                var_name = line.strip().split(' as ')[1][:-1]
                                inject = f'{indent}import logging; logging.getLogger(__name__).exception(f"Swallowed error in {file}: {{{var_name}}}")'
                            
                            # If the next line is exactly the one we are about to inject, skip
                            if "logging.getLogger(__name__).exception" not in lines[next_i] and "logging.error" not in lines[next_i]:
                                new_lines.append(inject)
                                count += 1
                                modified = True
                        
                        i = next_i - 1 # will be incremented
                    i += 1
                
                if modified:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(new_lines))

    print(f"Injected {count} loggers.")

if __name__ == '__main__':
    inject_loggers(['src', 'scripts', 'tests', '.'])
