"""
EVE Online SSO v2 Authentication & Token Management Infrastructure.

Implements secure OAuth 2.0 PKCE & Confidential Client token lifecycle management
for multi-character EVE Swagger Interface (ESI) integration.

Ponytail: Zero-dependency standard library implementation: urllib, json, os, hashlib, secrets, base64, time, http.server.
"""

import os
import sys
import json
import time
import base64
import hashlib
import secrets
import threading
import urllib.request
import urllib.parse
import urllib.error

SSO_AUTH_URL = "https://login.eveonline.com/v2/oauth/authorize"
SSO_TOKEN_URL = "https://login.eveonline.com/v2/oauth/token"

# Configured Developer App Credentials
DEFAULT_CLIENT_ID = os.environ.get("EVE_CLIENT_ID", "56a3f0e5dcea4c73b7fa105268b0fb5d")
DEFAULT_CLIENT_SECRET = os.environ.get("EVE_CLIENT_SECRET", "eat_1Xz3ABNTKPuCDnvOlgmJIMeDnLvdOntbm_1jZd2d")

DEFAULT_SCOPES = [
    "publicData",
    "esi-calendar.respond_calendar_events.v1",
    "esi-calendar.read_calendar_events.v1",
    "esi-location.read_location.v1",
    "esi-location.read_ship_type.v1",
    "esi-mail.organize_mail.v1",
    "esi-mail.read_mail.v1",
    "esi-mail.send_mail.v1",
    "esi-skills.read_skills.v1",
    "esi-skills.read_skillqueue.v1",
    "esi-wallet.read_character_wallet.v1",
    "esi-wallet.read_corporation_wallet.v1",
    "esi-search.search_structures.v1",
    "esi-clones.read_clones.v1",
    "esi-characters.read_contacts.v1",
    "esi-universe.read_structures.v1",
    "esi-killmails.read_killmails.v1",
    "esi-corporations.read_corporation_membership.v1",
    "esi-assets.read_assets.v1",
    "esi-planets.manage_planets.v1",
    "esi-fleets.read_fleet.v1",
    "esi-fleets.write_fleet.v1",
    "esi-ui.open_window.v1",
    "esi-ui.write_waypoint.v1",
    "esi-characters.write_contacts.v1",
    "esi-fittings.read_fittings.v1",
    "esi-fittings.write_fittings.v1",
    "esi-markets.structure_markets.v1",
    "esi-corporations.read_structures.v1",
    "esi-characters.read_loyalty.v1",
    "esi-characters.read_chat_channels.v1",
    "esi-characters.read_medals.v1",
    "esi-characters.read_standings.v1",
    "esi-characters.read_agents_research.v1",
    "esi-industry.read_character_jobs.v1",
    "esi-markets.read_character_orders.v1",
    "esi-characters.read_blueprints.v1",
    "esi-characters.read_corporation_roles.v1",
    "esi-location.read_online.v1",
    "esi-contracts.read_character_contracts.v1",
    "esi-clones.read_implants.v1",
    "esi-characters.read_fatigue.v1",
    "esi-killmails.read_corporation_killmails.v1",
    "esi-corporations.track_members.v1",
    "esi-wallet.read_corporation_wallets.v1",
    "esi-characters.read_notifications.v1",
    "esi-corporations.read_divisions.v1",
    "esi-corporations.read_contacts.v1",
    "esi-assets.read_corporation_assets.v1",
    "esi-corporations.read_titles.v1",
    "esi-corporations.read_blueprints.v1",
    "esi-contracts.read_corporation_contracts.v1",
    "esi-corporations.read_standings.v1",
    "esi-corporations.read_starbases.v1",
    "esi-industry.read_corporation_jobs.v1",
    "esi-markets.read_corporation_orders.v1",
    "esi-corporations.read_container_logs.v1",
    "esi-industry.read_character_mining.v1",
    "esi-industry.read_corporation_mining.v1",
    "esi-planets.read_customs_offices.v1",
    "esi-corporations.read_facilities.v1",
    "esi-corporations.read_medals.v1",
    "esi-characters.read_titles.v1",
    "esi-alliances.read_contacts.v1",
    "esi-characters.read_fw_stats.v1",
    "esi-corporations.read_fw_stats.v1",
    "esi-corporations.read_projects.v1",
    "esi-corporations.read_freelance_jobs.v1",
    "esi-characters.read_freelance_jobs.v1",
    "esi-structures.read_corporation.v1",
    "esi-structures.read_character.v1",
    "esi-activities.read_character.v1",
    "esi-access.read_lists.v1",
    "esi.activity.char:read",
    "esi.cosmetic.char:read",
]

TOKEN_STORE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "vault",
    "Eve Online",
    "tokens.json"
)

SESSION_STORE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "vault",
    "Eve Online",
    "sessions.json"
)


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def generate_pkce():
    """Generate PKCE code_verifier and code_challenge (S256)."""
    verifier = _base64url_encode(secrets.token_bytes(32))
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = _base64url_encode(digest)
    return verifier, challenge


def load_sessions() -> dict:
    if os.path.exists(SESSION_STORE_PATH):
        try:
            with open(SESSION_STORE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_session(state: str, session_data: dict):
    sessions = load_sessions()
    sessions[state] = session_data
    os.makedirs(os.path.dirname(SESSION_STORE_PATH), exist_ok=True)
    with open(SESSION_STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(sessions, f)


def pop_session(state: str) -> dict:
    sessions = load_sessions()
    session_data = sessions.pop(state, {})
    with open(SESSION_STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(sessions, f)
    return session_data


class TokenManager:
    """Manages persistent token store for all authorized EVE characters."""

    def __init__(self, store_path=TOKEN_STORE_PATH):
        self.store_path = store_path
        os.makedirs(os.path.dirname(store_path), exist_ok=True)
        self._lock = threading.Lock()

    def load_tokens(self) -> dict:
        with self._lock:
            if os.path.exists(self.store_path):
                try:
                    with open(self.store_path, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception:
                    return {}
            return {}

    def save_tokens(self, data: dict):
        with self._lock:
            with open(self.store_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

    def add_or_update_character(self, character_id: int, token_info: dict):
        tokens = self.load_tokens()
        tokens[str(character_id)] = token_info
        self.save_tokens(tokens)

    def get_character(self, character_id: int) -> dict:
        tokens = self.load_tokens()
        return tokens.get(str(character_id))

    def list_characters(self) -> list:
        tokens = self.load_tokens()
        return list(tokens.values())

    def delete_character(self, character_id: int):
        tokens = self.load_tokens()
        if str(character_id) in tokens:
            del tokens[str(character_id)]
            self.save_tokens(tokens)


token_manager = TokenManager()


def decode_jwt_payload_unverified(token: str) -> dict:
    """Decode JWT payload without verifying signature (for extracting character_id and name)."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return {}
        padded = parts[1] + "=" * ((4 - len(parts[1]) % 4) % 4)
        raw_json = base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8")
        return json.loads(raw_json)
    except Exception:
        return {}


def exchange_code_for_token(client_id: str, code: str, code_verifier: str = None, callback_url: str = "http://localhost:8088/callback", client_secret: str = DEFAULT_CLIENT_SECRET) -> dict:
    """
    Exchange authorization code for access and refresh tokens.
    Supports both Basic Auth Confidential Client flow and PKCE Public Client flow.
    """
    payload = {
        "grant_type": "authorization_code",
        "code": code,
    }
    if code_verifier:
        payload["code_verifier"] = code_verifier

    encoded_data = urllib.parse.urlencode(payload).encode("utf-8")
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "login.eveonline.com",
        "User-Agent": "Uroboros-EVE-Intelligence/1.0",
    }
    if client_secret:
        auth_str = f"{client_id}:{client_secret}"
        headers["Authorization"] = f"Basic {base64.b64encode(auth_str.encode()).decode()}"
    else:
        payload["client_id"] = client_id
        encoded_data = urllib.parse.urlencode(payload).encode("utf-8")

    req = urllib.request.Request(
        SSO_TOKEN_URL,
        data=encoded_data,
        headers=headers,
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            token_data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as he:
        error_body = he.read().decode("utf-8", errors="replace")
        print(f"❌ CCP SSO Token Error {he.code}: {error_body}")
        
        # Fallback: Try with client_id in body if Basic Auth was rejected
        try:
            payload["client_id"] = client_id
            if client_secret:
                payload["client_secret"] = client_secret
            fb_data = urllib.parse.urlencode(payload).encode("utf-8")
            fb_req = urllib.request.Request(
                SSO_TOKEN_URL,
                data=fb_data,
                headers={"Content-Type": "application/x-www-form-urlencoded", "Host": "login.eveonline.com"}
            )
            with urllib.request.urlopen(fb_req, timeout=15) as resp:
                token_data = json.loads(resp.read().decode("utf-8"))
        except Exception as fb_ex:
            raise ValueError(f"CCP Token Exchange Failed: {error_body or fb_ex}")

    access_token = token_data.get("access_token", "")
    refresh_token = token_data.get("refresh_token", "")
    expires_in = token_data.get("expires_in", 1199)

    jwt_payload = decode_jwt_payload_unverified(access_token)
    sub = jwt_payload.get("sub", "")
    char_id = int(sub.split(":")[-1]) if ":" in sub else 0
    char_name = jwt_payload.get("name", "Unknown Pilot")
    owner_hash = jwt_payload.get("owner", "")
    scopes = jwt_payload.get("scp", [])

    entry = {
        "character_id": char_id,
        "character_name": char_name,
        "client_id": client_id,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": time.time() + expires_in,
        "owner_hash": owner_hash,
        "scopes": scopes if isinstance(scopes, list) else [scopes],
        "updated_at": time.time(),
    }
    token_manager.add_or_update_character(char_id, entry)
    return entry


def refresh_access_token(character_id: int) -> str:
    """Check and refresh access token if expired, returns valid access token."""
    entry = token_manager.get_character(character_id)
    if not entry:
        raise ValueError(f"Character ID {character_id} not found in token store.")

    if entry.get("expires_at", 0) > time.time() + 60:
        return entry.get("access_token", "")

    client_id = entry.get("client_id", DEFAULT_CLIENT_ID)
    client_secret = DEFAULT_CLIENT_SECRET
    refresh_tok = entry.get("refresh_token", "")
    if not refresh_tok:
        raise ValueError(f"No refresh token available for character {character_id}.")

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_tok,
    }
    encoded_data = urllib.parse.urlencode(payload).encode("utf-8")
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "login.eveonline.com",
        "User-Agent": "Uroboros-EVE-Intelligence/1.0",
    }
    if client_secret:
        auth_str = f"{client_id}:{client_secret}"
        headers["Authorization"] = f"Basic {base64.b64encode(auth_str.encode()).decode()}"
    else:
        payload["client_id"] = client_id
        encoded_data = urllib.parse.urlencode(payload).encode("utf-8")

    req = urllib.request.Request(
        SSO_TOKEN_URL,
        data=encoded_data,
        headers=headers,
    )

    with urllib.request.urlopen(req, timeout=15) as resp:
        token_data = json.loads(resp.read().decode("utf-8"))

    access_token = token_data.get("access_token", "")
    new_refresh = token_data.get("refresh_token", refresh_tok)
    expires_in = token_data.get("expires_in", 1199)

    entry["access_token"] = access_token
    entry["refresh_token"] = new_refresh
    entry["expires_at"] = time.time() + expires_in
    entry["updated_at"] = time.time()
    token_manager.add_or_update_character(character_id, entry)
    return access_token


def generate_auth_url(client_id: str = DEFAULT_CLIENT_ID, callback_url: str = "http://localhost:8088/callback", scopes: list = None, state: str = None) -> tuple:
    """Generate SSO v2 Authorization URL and persist session state."""
    verifier, challenge = generate_pkce()
    if not state:
        state = secrets.token_hex(16)
    if scopes is None:
        scopes = DEFAULT_SCOPES

    save_session(state, {
        "client_id": client_id,
        "code_verifier": verifier,
        "created_at": time.time()
    })

    params = {
        "response_type": "code",
        "redirect_uri": callback_url,
        "client_id": client_id,
        "scope": " ".join(scopes),
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "state": state,
    }
    url = f"{SSO_AUTH_URL}?{urllib.parse.urlencode(params)}"
    return url, verifier, state
