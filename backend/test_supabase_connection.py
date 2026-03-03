"""
Test Supabase connection and storage setup
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

print("🔍 Testing Supabase Connection\n")
print(f"URL: {SUPABASE_URL}")
print(f"Key (first 20 chars): {SUPABASE_ANON_KEY[:20]}...")
print(f"Key length: {len(SUPABASE_ANON_KEY)} characters\n")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    print("❌ Missing Supabase credentials")
    exit(1)

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    print("✅ Supabase client created")
    
    # Test database connection
    try:
        result = supabase.table("brand_dna").select("count").limit(1).execute()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    
    # Test storage
    try:
        buckets = supabase.storage.list_buckets()
        print(f"✅ Storage accessible - {len(buckets)} buckets found")
        for bucket in buckets:
            print(f"   📦 {bucket.name}")
    except Exception as e:
        print(f"❌ Storage access failed: {e}")
        
except Exception as e:
    print(f"❌ Failed to create Supabase client: {e}")
