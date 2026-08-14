#!/usr/bin/env python3
"""
EVE Online Fleet Interactive Web Auth Hub & ESI Intelligence Server.

Hosts a local browser dashboard at http://localhost:8088/ where you can easily
click to connect each fleet account/character one by one via official CCP SSO,
view real-time connected pilots, extract full ESI telemetry, and index everything into knowledge.db.

Ponytail: Zero-dependency stdlib implementation (urllib, http.server, webbrowser, json, time, os, sys, subprocess).
"""

import os
import sys
import json
import time
import argparse
import subprocess
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

# Windows console UTF-8 support
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.eve_sso import (
    token_manager,
    generate_auth_url,
    exchange_code_for_token,
    pop_session,
    DEFAULT_CLIENT_ID,
    DEFAULT_CLIENT_SECRET,
    DEFAULT_SCOPES
)
from src.infrastructure.eve_esi import CharacterDataExtractor
from src.infrastructure.eve_vault_sync import synthesize_character_markdown, sync_and_index_all_characters

DEFAULT_CALLBACK_PORT = 8088
DEFAULT_CALLBACK_URL = f"http://localhost:{DEFAULT_CALLBACK_PORT}/callback"
BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"


def open_browser(url: str):
    """Open URL in Brave browser if available, else system default."""
    if os.path.exists(BRAVE_PATH):
        try:
            subprocess.Popen([BRAVE_PATH, url])
            return
        except Exception:
            pass
    webbrowser.open(url)


class FleetHubHTTPHandler(BaseHTTPRequestHandler):
    """Local Dashboard & SSO Callback Handler."""

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # 1. Main Dashboard
        if path == "/" or path == "/index.html":
            params = urllib.parse.parse_qs(parsed.query)
            added_pilot = params.get("added", [None])[0]
            self._render_dashboard(added_pilot=added_pilot)
            return

        # 2. Trigger SSO Redirect
        if path == "/auth":
            auth_url, verifier, state = generate_auth_url(
                client_id=DEFAULT_CLIENT_ID,
                callback_url=DEFAULT_CALLBACK_URL,
                scopes=DEFAULT_SCOPES
            )
            self.send_response(302)
            self.send_header("Location", auth_url)
            self.end_headers()
            return

        # 3. OAuth Callback from CCP
        if path == "/callback":
            params = urllib.parse.parse_qs(parsed.query)
            state = params.get("state", [""])[0]
            code = params.get("code", [""])[0]
            error = params.get("error", [""])[0]

            if error:
                self._send_html_page(
                    title="Authorization Error",
                    html_body=f"<h1>❌ Authorization Failed</h1><p>CCP returned error: <code>{error}</code></p><p><a href='/'>← Back to Fleet Hub</a></p>",
                    status=400
                )
                return

            if not code:
                self._send_html_page(
                    title="Missing Code",
                    html_body="<h1>❌ Missing Code</h1><p>No authorization code received from CCP.</p><p><a href='/'>← Back to Fleet Hub</a></p>",
                    status=400
                )
                return

            session_info = pop_session(state) if state else {}
            client_id = session_info.get("client_id", DEFAULT_CLIENT_ID)
            code_verifier = session_info.get("code_verifier")

            try:
                token_entry = exchange_code_for_token(
                    client_id=client_id,
                    code=code,
                    code_verifier=code_verifier,
                    callback_url=DEFAULT_CALLBACK_URL,
                    client_secret=DEFAULT_CLIENT_SECRET
                )
                char_id = token_entry.get("character_id")
                char_name = token_entry.get("character_name")

                # Extract telemetry and index
                print(f"\n📡 [ESI SYNC] Fetching full telemetry for {char_name} (ID: {char_id})...")
                extractor = CharacterDataExtractor(char_id)
                profile = extractor.extract_full_profile()
                files = synthesize_character_markdown(profile)

                from batch_index import index_single_file
                for fp in files:
                    index_single_file(fp)

                print(f"🎉 [SYNC COMPLETE] Linked {char_name}: {len(files)} dossier files indexed into knowledge.db.")

                # Redirect back to dashboard with success banner
                safe_name = urllib.parse.quote(char_name)
                self.send_response(302)
                self.send_header("Location", f"/?added={safe_name}")
                self.end_headers()
                return
            except Exception as ex:
                print(f"❌ Error in token exchange/ESI sync: {ex}")
                self._send_html_page(
                    title="Sync Error",
                    html_body=f"<h1>❌ Error Processing Pilot</h1><p>Error: <code>{ex}</code></p><p><a href='/'>← Back to Fleet Hub</a></p>",
                    status=500
                )
                return

        self.send_response(404)
        self.end_headers()

    def _render_dashboard(self, added_pilot=None):
        chars = token_manager.list_characters()
        
        banner_html = ""
        if added_pilot:
            banner_html = f"""
            <div class="banner-success">
                ✨ Successfully authorized & indexed pilot: <strong>{added_pilot}</strong>!
            </div>
            """

        rows_html = ""
        if not chars:
            rows_html = """
            <tr>
                <td colspan="5" style="text-align: center; color: #8b949e; padding: 24px;">
                    No characters linked yet. Click the button below to connect your first account/pilot!
                </td>
            </tr>
            """
        else:
            for idx, c in enumerate(chars):
                cid = c.get("character_id")
                cname = c.get("character_name", f"Pilot {cid}")
                updated = time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(c.get('updated_at', time.time())))
                portrait_url = f"https://images.evetech.net/characters/{cid}/portrait?size=64"
                rows_html += f"""
                <tr>
                    <td style="display: flex; align-items: center; gap: 12px;">
                        <img src="{portrait_url}" style="width: 36px; height: 36px; border-radius: 50%; border: 1px solid #30363d;">
                        <strong>{cname}</strong>
                    </td>
                    <td><code>{cid}</code></td>
                    <td><span class="badge-online">🟢 Authorized</span></td>
                    <td>{len(c.get('scopes', []))} scopes</td>
                    <td style="color: #8b949e;">{updated}</td>
                </tr>
                """

        html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Uroboros EVE Fleet Intelligence Hub</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #0d1117;
      color: #c9d1d9;
      margin: 0;
      padding: 32px 16px;
      display: flex;
      justify-content: center;
    }}
    .container {{
      max-width: 860px;
      width: 100%;
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 12px;
      padding: 32px;
      box-shadow: 0 12px 32px rgba(0,0,0,0.6);
    }}
    h1 {{
      font-size: 24px;
      color: #58a6ff;
      margin-top: 0;
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    p.subtitle {{
      color: #8b949e;
      font-size: 14px;
      margin-bottom: 24px;
    }}
    .banner-success {{
      background: rgba(46, 160, 67, 0.15);
      border: 1px solid #2ea043;
      color: #3fb950;
      padding: 12px 16px;
      border-radius: 8px;
      margin-bottom: 20px;
      font-size: 14px;
    }}
    .btn-connect {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      background: #238636;
      color: #ffffff;
      font-size: 16px;
      font-weight: 600;
      text-decoration: none;
      padding: 14px 28px;
      border-radius: 8px;
      border: 1px solid rgba(255,255,255,0.1);
      transition: background 0.2s;
      cursor: pointer;
      width: 100%;
      text-align: center;
      margin-bottom: 28px;
    }}
    .btn-connect:hover {{
      background: #2ea043;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 12px;
      font-size: 14px;
    }}
    th {{
      text-align: left;
      padding: 12px;
      color: #8b949e;
      border-bottom: 1px solid #30363d;
      font-weight: 600;
    }}
    td {{
      padding: 14px 12px;
      border-bottom: 1px solid #21262d;
    }}
    .badge-online {{
      color: #3fb950;
      font-weight: 500;
      font-size: 12px;
      background: rgba(46, 160, 67, 0.1);
      padding: 2px 8px;
      border-radius: 12px;
      border: 1px solid rgba(46, 160, 67, 0.3);
    }}
    .info-box {{
      background: #0d1117;
      border: 1px solid #30363d;
      border-radius: 8px;
      padding: 16px;
      margin-top: 24px;
      font-size: 13px;
      color: #8b949e;
    }}
    code {{
      background: #21262d;
      padding: 2px 6px;
      border-radius: 4px;
      color: #f0883e;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>🚀 Uroboros EVE Fleet Intelligence Hub</h1>
    <p class="subtitle">Secure multi-character EVE SSO link & ESI telemetry synchronization into the Knowledge Vault.</p>
    
    {banner_html}

    <a href="/auth" class="btn-connect">
      ➕ Connect Account / Character (Official CCP SSO)
    </a>

    <h3 style="font-size: 16px; color: #c9d1d9; margin-bottom: 8px;">Linked Fleet Pilots ({len(chars)})</h3>
    <table>
      <thead>
        <tr>
          <th>Pilot Name</th>
          <th>Character ID</th>
          <th>Status</th>
          <th>Permissions</th>
          <th>Last Synced</th>
        </tr>
      </thead>
      <tbody>
        {rows_html}
      </tbody>
    </table>

    <div class="info-box">
      <strong>💡 How to link multiple accounts:</strong>
      <ol style="margin: 8px 0 0 16px; padding: 0;">
        <li>Click <strong>"Connect Account / Character"</strong> above.</li>
        <li>Log into your EVE account on CCP's official page, choose your pilot, and click <strong>Authorize</strong>.</li>
        <li>It will instantly redirect back here, displaying your authorized pilot in the table!</li>
        <li>Repeat for your next account/alt character until your entire fleet is linked.</li>
      </ol>
    </div>
  </div>
</body>
</html>"""
        self._send_html_page("Fleet Hub", html)

    def _send_html_page(self, title: str, html_body: str, status: int = 200):
        if not html_body.strip().startswith("<!DOCTYPE html>"):
            html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <style>
    body {{ font-family: sans-serif; background: #0d1117; color: #c9d1d9; padding: 40px; text-align: center; }}
    a {{ color: #58a6ff; text-decoration: none; }}
  </style>
</head>
<body>{html_body}</body>
</html>"""
        else:
            html = html_body

        encoded = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def start_server():
    """Start local Fleet Hub server."""
    print("=" * 70)
    print("🚀 UROBOROS EVE FLEET INTELLIGENCE HUB LIVE")
    print(f"🌐 Dashboard URL: http://localhost:{DEFAULT_CALLBACK_PORT}/")
    print(f"🔑 Using Client ID: {DEFAULT_CLIENT_ID}")
    print("=" * 70)

    server = HTTPServer(("localhost", DEFAULT_CALLBACK_PORT), FleetHubHTTPHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Stopped Fleet Hub Server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    start_server()
