import re
import os

def check_mermaid_in_file(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    blocks = re.findall(r"```mermaid(.*?)```", content, re.DOTALL)
    for block in blocks:
        lines = block.strip().split("\n")
        for line_num, line in enumerate(lines, 1):
            line_str = line.strip()
            # Check 1: subgraph with spaces and no quotes / id
            if line_str.startswith("subgraph") and " " in line_str[8:].strip() and "[" not in line_str and '"' not in line_str:
                print(f"[SUBGRAPH SPACE] {filepath}:{line_num} -> {line_str}")
            
            # Check 2: square bracket containing unquoted parens like [Foo (Bar)]
            # Match if there are parens inside [] without quotes
            m = re.search(r'\[([^"\n]*?\([^\n]*?\)[^"\n]*?)\]', line_str)
            if m:
                print(f"[UNQUOTED PARENS IN BRACKET] {filepath}:{line_num} -> {line_str}")
            
            # Check 3: edge with unquoted brackets or comparison operators
            m_edge = re.search(r'--\s*([^"\n]*?[<>=$$$$][^"\n]*?)\s*-->', line_str)
            if m_edge:
                print(f"[UNQUOTED SPECIAL IN EDGE] {filepath}:{line_num} -> {line_str}")

def main():
    for root, dirs, files in os.walk("."):
        if any(ignored in root for ignored in [".git", "node_modules", ".gemini", "dist", "build"]):
            continue
        for file in files:
            if file.endswith(".md") or file.endswith(".py"):
                check_mermaid_in_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
