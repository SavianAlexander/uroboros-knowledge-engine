import os, glob

for p in glob.glob('src/**/*.py', recursive=True):
    try:
        text = open(p, encoding='utf-8').read()
        if '.error("Swallowed error' in text or '.error(f"Swallowed error' in text:
            text = text.replace('.error("Swallowed error', '.warning("Swallowed error')
            text = text.replace('.error(f"Swallowed error', '.warning(f"Swallowed error')
            open(p, 'w', encoding='utf-8').write(text)
            print("Fixed", p)
    except Exception:
        pass
