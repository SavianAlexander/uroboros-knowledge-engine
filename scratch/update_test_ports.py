import os
import re

tests_dir = r"C:\Users\Administrator\Desktop\Neuro Alexander\tests"
count = 0
for root, _, files in os.walk(tests_dir):
    for f in files:
        if f.endswith('.py'):
            filepath = os.path.join(root, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            new_content = re.sub(r'port\s*=\s*(?:PORT|self\.port|\d{4,})', 'port=0', content)
            new_content = re.sub(r'http_port\s*=\s*\d{4,}', 'http_port=0', new_content)
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print(f"Updated {f}")
                count += 1

print(f"\nReplaced static ports with ephemeral socket port=0 in {count} test files.")
