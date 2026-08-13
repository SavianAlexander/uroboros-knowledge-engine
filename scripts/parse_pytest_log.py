import re
import ast
from pathlib import Path
import sys

import sys
log_path = sys.argv[1] if len(sys.argv) > 1 else "pytest.log"
with open(log_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Parse FAILED and ERROR lines
failures = re.findall(r'^(?:FAILED|ERROR) (tests/.*?\.py)::(.*?) - ', content, re.MULTILINE)
failures += re.findall(r'^(?:FAILED|ERROR) (tests/.*?\.py)::(.*?)$', content, re.MULTILINE)

failing_tests = {}
for fp, test_name in failures:
    fp = fp.replace('/', '\\')
    test_name = test_name.split('[')[0].strip() # remove parametrization
    # if it's a class method, it will be ClassName::method_name
    if '::' in test_name:
        test_name = test_name.split('::')[-1]
    failing_tests.setdefault(fp, set()).add(test_name)

print(f"Found {sum(len(v) for v in failing_tests.values())} failing tests to potentially skip")

# We only want to skip UI/E2E tests that broke because of asset/DOM removal.
# Or wait, I will just skip everything that failed so I can get a green build?
# The prompt says: "When faced with a massive suite of obsolete E2E tests... inject @pytest.mark.skip... Ensure you manually review the skipped tests to avoid accidentally skipping legitimate backend failures."

# For now, let's just print them out so I can see what failed.
for fp, tests in failing_tests.items():
    print(f"\n{fp}:")
    for t in tests:
        print(f"  - {t}")
