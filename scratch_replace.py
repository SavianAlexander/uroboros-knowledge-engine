import os

files = [
    "src/infrastructure/ocr.py",
    "src/app/routers/tags.py",
    "src/core/state.py"
]

for p in files:
    if os.path.exists(p):
        text = open(p, encoding="utf-8").read()
        text = text.replace('.exception(f"Swallowed error in ocr.py', '.error(f"Swallowed error in ocr.py')
        text = text.replace('.exception(f"Swallowed error in tags.py', '.error(f"Swallowed error in tags.py')
        text = text.replace('.exception("Swallowed error in tags.py', '.error("Swallowed error in tags.py')
        text = text.replace('.exception(f"Swallowed error in state.py', '.error(f"Swallowed error in state.py')
        text = text.replace('.exception("Swallowed error in state.py', '.error("Swallowed error in state.py')
        open(p, 'w', encoding="utf-8").write(text)
        print(f"Updated {p}")
