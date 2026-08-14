import urllib.request
import json
import http.cookiejar

cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

login_url = "http://localhost:3002/api/login"
payload = json.dumps({"email": "savianalexander@pm.me", "password": "Seeulater@4224"}).encode("utf-8")
req = urllib.request.Request(login_url, data=payload, headers={"Content-Type": "application/json"})

print("Attempting login at /api/login...")
try:
    with opener.open(req) as resp:
        print(f"Login Status: {resp.status}")
        data = resp.read().decode("utf-8")
        print("Response:", data)
        print("\nSession Cookies received:")
        for cookie in cookie_jar:
            print(f"  {cookie.name} = {cookie.value}")

    # Now request /api/profile with session cookies
    profile_url = "http://localhost:3002/api/profile"
    with opener.open(profile_url) as resp:
        print(f"\nProfile Status with Cookie: {resp.status}")
        print("User profile email:", json.loads(resp.read().decode("utf-8")).get("email"))
    print("\n✓ Full browser session login and profile load SUCCESSFUL!")

except urllib.error.HTTPError as e:
    print(f"Login failed: {e.code} - {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Exception: {e}")
