import os
import ast
import re
import glob

def scan_routers():
    print("=== 1. AUDITING ROUTERS IN src/app/routers/ ===")
    routers = glob.glob("src/app/routers/*.py")
    all_routes = []
    for r in routers:
        name = os.path.basename(r)
        with open(r, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()
        routes = re.findall(r"@router\.(get|post|put|delete|patch)\(\s*[\"']([^\"']+)[\"']", code)
        all_routes.extend([(name, method, path) for method, path in routes])
        print(f"  {name:25s} -> {len(routes):2d} routes")
    print(f"Total API routes across all routers: {len(all_routes)}")

def scan_domain_stubs():
    print("\n=== 2. AUDITING DOMAIN MODULES FOR STUBS & PLACEHOLDERS ===")
    domain_files = glob.glob("src/domain/*.py") + glob.glob("src/domain/**/*.py", recursive=True)
    findings = []
    for d in domain_files:
        rel_path = os.path.relpath(d, ".")
        with open(d, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                        findings.append((rel_path, node.name, "Empty pass function"))
                    elif len(node.body) == 1 and isinstance(node.body[0], ast.Return):
                        ret_val = node.body[0].value
                        if isinstance(ret_val, ast.Constant) and str(ret_val.value).upper() in ("MOCK", "TODO"):
                            findings.append((rel_path, node.name, f"Hardcoded constant {ret_val.value}"))
        except Exception as e:
            findings.append((rel_path, "PARSE_ERROR", str(e)))

        mock_matches = re.findall(r"(TODO|FIXME|MOCK_DATA|dummy_data|fake_data)", content, re.IGNORECASE)
        if mock_matches:
            findings.append((rel_path, "TEXT_MATCH", f"Contains markers: {set(mock_matches)}"))

    print(f"Findings in domain ({len(findings)} items):")
    for f in findings:
        print(f"  [{f[0]}] {f[1]}: {f[2]}")

def scan_infrastructure():
    print("\n=== 3. AUDITING INFRASTRUCTURE & CORE FOR REAL INTEGRATION ===")
    infra_files = glob.glob("src/infrastructure/*.py") + glob.glob("src/core/*.py")
    infra_findings = []
    for fpath in infra_files:
        rel_path = os.path.relpath(fpath, ".")
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if "TODO" in content or "FIXME" in content:
            infra_findings.append((rel_path, "Contains TODO/FIXME"))
    print(f"Infrastructure/Core findings ({len(infra_findings)} items):")
    for f in infra_findings:
        print(f"  [{f[0]}]: {f[1]}")

def scan_frontend():
    print("\n=== 4. AUDITING FRONTEND CLIENT VS API ENDPOINTS ===")
    frontend_files = glob.glob("frontend/src/**/*.js", recursive=True) + glob.glob("frontend/src/**/*.jsx", recursive=True) + glob.glob("frontend/src/**/*.ts", recursive=True) + glob.glob("frontend/src/**/*.tsx", recursive=True)
    frontend_api_calls = []
    for fpath in frontend_files:
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        calls = re.findall(r"fetch\(\s*[\"']([^\"']+)[\"']|axios\.\w+\(\s*[\"']([^\"']+)[\"']", content)
        for c in calls:
            endpoint = c[0] or c[1]
            if endpoint:
                frontend_api_calls.append(endpoint)
    print(f"Total frontend components: {len(frontend_files)}")
    print(f"Total distinct API fetch targets found: {len(set(frontend_api_calls))}")
    for target in sorted(set(frontend_api_calls))[:15]:
        print(f"  Frontend calls: {target}")

if __name__ == "__main__":
    scan_routers()
    scan_domain_stubs()
    scan_infrastructure()
    scan_frontend()
