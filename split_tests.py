import os
import re

with open("tests/test_e2e_t3_cross_feature.py", "r") as f:
    content = f.read()

# We want to extract the setUpClass, setUp, tearDown, and the 5 test methods.
# And recreate 5 files.

# The header is everything up to 'class TestE2ETier3CrossFeature(unittest.TestCase):'
header = content.split('class TestE2ETier3CrossFeature(unittest.TestCase):')[0]

# Add get_free_port to header
header += """import socket

def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port

"""

base_class_setup = """class TestE2ETier3Chain{chain_num}(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        main.is_testing = True
        port = get_free_port()
        cls.client = TestClient(main.app, base_url=f"http://127.0.0.1:{{port}}")

    def _cleanup_db_files(self, db_file):
        for suffix in ["", "-wal", "-shm"]:
            fpath = db_file + suffix
            if os.path.exists(fpath):
                for _ in range(50):
                    try:
                        os.remove(fpath)
                    except FileNotFoundError:
                        break
                    except PermissionError:
                        pass
                    if not os.path.exists(fpath):
                        break
                    time.sleep(0.05)

    def setUp(self):
        import time
        test_name = self.id().split('.')[-1]
        self.db_file = f"e2e_t3_chain{chain_num}_{{test_name}}_{{int(time.time()*1000)}}.db"
        self.sandbox_dir = Path(f"test_sandbox_t3_chain{chain_num}_{{test_name}}_{{int(time.time()*1000)}}").resolve()
        self.sandbox_dir_str = str(self.sandbox_dir)

        # Update global references
        know.DB_FILE = self.db_file
        import src.infrastructure.database as db
        db.DB_FILE = self.db_file
        main.ACTIVE_DIR = self.sandbox_dir_str

        # Cleanup & Init DB
        self._cleanup_db_files(self.db_file)
        know.init_db()

        # Init fresh sandbox directory
        if self.sandbox_dir.exists():
            try:
                shutil.rmtree(self.sandbox_dir)
            except Exception as e:
                import logging; logging.error(f"Swallowed error: {{e}}")
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        if hasattr(self, "sandbox_dir") and self.sandbox_dir.exists():
            try:
                shutil.rmtree(self.sandbox_dir)
            except Exception as e:
                import logging; logging.error(f"Swallowed error: {{e}}")
        if hasattr(self, "db_file"):
            self._cleanup_db_files(self.db_file)
"""

chains = []
for i in range(1, 6):
    pattern = f"    def test_chain{i}.*?(?=    def test_chain|$|if __name__ ==)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        chains.append(match.group(0))

for i, chain_code in enumerate(chains, 1):
    if i == 5:
        # replace port 8092 in chain 5
        chain_code = chain_code.replace('peer_addr = "http://127.0.0.1:8092"', 'peer_addr = f"http://127.0.0.1:{get_free_port()}"')
        
    file_content = header + base_class_setup.format(chain_num=i) + chain_code + """
if __name__ == "__main__":
    unittest.main()
"""
    with open(f"tests/test_e2e_t3_chain{i}.py", "w") as f:
        f.write(file_content)

os.remove("tests/test_e2e_t3_cross_feature.py")
print("Done splitting.")
