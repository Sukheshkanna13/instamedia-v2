"""
Setup script for Supabase Storage bucket for brand logos
Run this once to create the 'brand-logos' bucket
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

def setup_storage_bucket():
    """Create the brand-logos storage bucket if it doesn't exist"""
    
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("❌ Supabase credentials not found in .env file")
        return False
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        # Try to create the bucket
        # Note: This will fail if bucket already exists, which is fine
        try:
            supabase.storage.create_bucket(
                'brand-logos',
                options={
                    'public': True,  # Make bucket public so logos are accessible
                    'file_size_limit': 2097152,  # 2MB limit
                    'allowed_mime_types': ['image/png', 'image/jpeg', 'image/jpg', 'image/svg+xml', 'image/webp']
                }
            )
            print("✅ Created 'brand-logos' storage bucket")
        except Exception as e:
            if 'already exists' in str(e).lower():
                print("ℹ️  'brand-logos' bucket already exists")
            else:
                print(f"⚠️  Error creating bucket: {e}")
        
        # List buckets to verify
        buckets = supabase.storage.list_buckets()
        print(f"\n📦 Available storage buckets:")
        for bucket in buckets:
            print(f"   - {bucket.name} (public: {bucket.public})")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to setup storage: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Setting up Supabase Storage for InstaMedia AI\n")
    setup_storage_bucket()
