import os
import time
import sqlite3
import requests
import datetime
import threading
from pathlib import Path

# Configuration
DB_FILE = "knowledge.db"
NEURO_DIR = r"C:\Users\Administrator\Desktop\Neuro Alexander"
DESKTOP_DIR = r"C:\Users\Administrator\Desktop"
API_URL = "http://localhost:8000/api/contemplate"
INTERVAL_SECONDS = 24 * 60 * 60  # 24 hours

def get_latest_files(limit=3):
    """Retrieve the most recently modified files from the database."""
    db_path = os.path.join(NEURO_DIR, DB_FILE)
    if not os.path.exists(db_path):
        return []
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT filepath, content FROM fts_files ORDER BY rowid DESC LIMIT ?", (limit,))
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        print(f"Chaos Monkey DB Error: {e}")
        return []

def run_chaos_monkey():
    print(f"[{datetime.datetime.now().isoformat()}] Chaos Monkey waking up...")
    
    files = get_latest_files(limit=3)
    if not files:
        print("No files found to attack. Going back to sleep.")
        return

    report_content = f"# 🐒 Chaos Monkey Vulnerability Report\n*Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
    report_content += "> [!WARNING]\n> The Chaos Monkey has analyzed your latest work in Red Team mode. Do not ignore these vulnerabilities.\n\n"

    for filepath, content in files:
        filename = os.path.basename(filepath)
        report_content += f"## Target: `{filename}`\n"
        report_content += f"**Path**: `{filepath}`\n\n"
        
        try:
            # Send to Uroboros /api/contemplate in Red Team mode
            payload = {
                "text": f"File: {filename}\nContent:\n{content[:2000]}",
                "mode": "red_team"
            }
            resp = requests.post(API_URL, json=payload, timeout=120)
            if resp.status_code == 200:
                data = resp.json()
                report_content += f"### 🔴 Red Team Attack Analysis\n"
                report_content += f"**Core Problem Vulnerability**: {data.get('core_problem', 'N/A')}\n\n"
                report_content += f"**Risk Profile**: {data.get('risk_profile', 'N/A')}\n\n"
                report_content += f"**Friction & Attack Vector**: {data.get('friction_cost', 'N/A')}\n\n"
                report_content += f"**Raw Hostile Output**:\n{data.get('raw_analysis', 'N/A')}\n\n"
            else:
                report_content += f"*API Error {resp.status_code}: {resp.text}*\n\n"
        except Exception as e:
            report_content += f"*Connection failed. Ensure Neuro Uroboros is running. Error: {str(e)}*\n\n"
            
        report_content += "---\n\n"

    report_path = os.path.join(DESKTOP_DIR, f"Chaos_Monkey_Report_{datetime.datetime.now().strftime('%Y%m%d')}.md")
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"Report generated: {report_path}")
    except Exception as e:
        print(f"Failed to write report: {e}")

def daemon_loop():
    print("Chaos Monkey Daemon started. Running every 24 hours.")
    while True:
        run_chaos_monkey()
        print(f"Going to sleep for {INTERVAL_SECONDS} seconds...")
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    daemon_loop()
