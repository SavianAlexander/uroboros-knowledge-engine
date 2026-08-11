import os

# 1. Fix analytics_engine.py indices
p_analytics = "src/domain/analytics_engine.py"
if os.path.exists(p_analytics):
    text = open(p_analytics, encoding="utf-8").read()
    
    # Replace dict-like indexing with tuple indexing
    text = text.replace('r["query"]', 'r[0]')
    text = text.replace('r["count"]', 'r[1]')
    text = text.replace('r["mode"]', 'r[1]')
    text = text.replace('r["executed_at"]', 'r[2]')
    text = text.replace('r["result_count"]', 'r[3]')
    text = text.replace('r["dt"]', 'r[0]')
    
    # Replace .exception with .warning
    text = text.replace('.exception("Swallowed error', '.warning("Swallowed error')
    
    open(p_analytics, 'w', encoding="utf-8").write(text)
    print("Fixed analytics_engine.py")

# 2. Change .error to .warning for Swallowed error loggers across the board
files = [
    "src/infrastructure/ocr.py",
    "src/app/routers/tags.py",
    "src/core/state.py",
    "src/domain/analytics_engine.py"
]

for p in files:
    if os.path.exists(p):
        text = open(p, encoding="utf-8").read()
        
        # Replace .error("Swallowed error with .warning("Swallowed error
        text = text.replace('.error("Swallowed error', '.warning("Swallowed error')
        text = text.replace('.error(f"Swallowed error', '.warning(f"Swallowed error')
        
        open(p, 'w', encoding="utf-8").write(text)
        print(f"Fixed loggers in {p}")


text = open('src/core/embeddings.py', encoding='utf-8').read(); open('src/core/embeddings.py', 'w', encoding='utf-8').write(text.replace('logging.error(f"Failed to generate embedding', 'logging.warning(f"Failed to generate embedding'))

