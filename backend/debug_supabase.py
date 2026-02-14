from supabase import create_client, Client
from dotenv import load_dotenv
import os
import sys

# Load environment logic just like app.py
load_dotenv()

# --- Config ---
url = os.getenv("SUPABASE_URL", "")
key = os.getenv("SUPABASE_ANON_KEY", "")

# --- Validation ---
print(f"Supabase Debugger")
print(f"-----------------")
print(f"URL: {url}")
if len(key) > 10:
    print(f"Key: {key[:5]}...{key[-5:]} (Length: {len(key)})")
else:
    print(f"Key: '{key}' (Too short)")

if not url or not key:
    print("❌ Configuration missing. Check .env file.")
    sys.exit(1)

# Check Key Format
if key.startswith("sb_"):
    print("⚠️  Warning: Key starts with 'sb_'. This looks like a Service Token/Management Key.")
    print("   The Supabase Client usually expects the 'anon public' key which is a long JWT string starting with 'eyJ...'.")
elif key.startswith("eyJ"):
    print("✅ Key format looks correct (JWT).")
else:
    print("ℹ️  Key format unrecognized.")

# --- Connection Attempt ---
print("\nAttempting connection...")
try:
    supabase: Client = create_client(url, key)
    # The client creation doesn't validate, we need to make a request
    # Try a simple select. Even if table doesn't exist, allow 404.
    # But usually 'auth' endpoint is safest.
    
    # Let's try to just list tables or check auth config
    # Actually, let's just create the client and see if it throws immediately (sometimes it does)
    print("Client created locally.")

    # Now make a request to verify credentials
    print("Sending test request to 'brand_dna' (expecting empty result or table error, but successful auth)...")
    response = supabase.table("brand_dna").select("count", count="exact").execute()
    
    print("✅ Connection SUCCESS!")
    print(f"Response data: {response.data}")
    print(f"Response count: {response.count}")

except Exception as e:
    print("\n❌ Connection FAILED.")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}")
    
    # Sometimes Supabase lib wraps the real HTTP error
    if hasattr(e, 'code'):
        print(f"Error Code: {e.code}")
    if hasattr(e, 'details'):
        print(f"Error Details: {e.details}")
