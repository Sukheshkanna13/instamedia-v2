#!/usr/bin/env python3
"""
Verify that API keys are properly configured
Run: python verify_setup.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def print_status(check, status, message):
    icon = "✅" if status else "❌"
    print(f"{icon} {check}: {message}")
    return status

def main():
    print("\n" + "="*60)
    print("  InstaMedia AI - Configuration Verification")
    print("="*60 + "\n")
    
    # Load .env file
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        print("❌ Error: .env file not found!")
        print("Run: python setup_keys.py")
        sys.exit(1)
    
    load_dotenv(env_path)
    
    all_good = True
    
    # Check LLM Provider
    print("🔍 Checking LLM Configuration...\n")
    
    llm_provider = os.getenv("LLM_PROVIDER", "").strip()
    if not llm_provider:
        print_status("LLM Provider", False, "Not set")
        all_good = False
    else:
        print_status("LLM Provider", True, f"Set to '{llm_provider}'")
    
    # Check API keys based on provider
    if llm_provider == "gemini":
        gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not gemini_key or gemini_key == "your_gemini_key_here":
            print_status("Gemini API Key", False, "Not configured")
            print("   Get your key: https://aistudio.google.com/app/apikey")
            all_good = False
        else:
            # Mask the key for security
            masked_key = gemini_key[:10] + "..." + gemini_key[-4:]
            print_status("Gemini API Key", True, f"Configured ({masked_key})")
    
    elif llm_provider == "groq":
        groq_key = os.getenv("GROQ_API_KEY", "").strip()
        if not groq_key or groq_key == "your_groq_key_here":
            print_status("Groq API Key", False, "Not configured")
            print("   Get your key: https://console.groq.com")
            all_good = False
        else:
            masked_key = groq_key[:10] + "..." + groq_key[-4:]
            print_status("Groq API Key", True, f"Configured ({masked_key})")
    
    # Check Supabase (optional)
    print("\n🔍 Checking Optional Services...\n")
    
    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_key = os.getenv("SUPABASE_ANON_KEY", "").strip()
    
    if supabase_url and supabase_url != "your_supabase_project_url":
        print_status("Supabase URL", True, "Configured")
        if supabase_key and supabase_key != "your_supabase_anon_key":
            print_status("Supabase Key", True, "Configured")
        else:
            print_status("Supabase Key", False, "Missing")
    else:
        print_status("Supabase", True, "Not configured (using in-memory storage)")
    
    # Check OAuth (optional)
    instagram_id = os.getenv("INSTAGRAM_CLIENT_ID", "").strip()
    linkedin_id = os.getenv("LINKEDIN_CLIENT_ID", "").strip()
    twitter_id = os.getenv("TWITTER_CLIENT_ID", "").strip()
    
    oauth_configured = False
    if instagram_id and instagram_id != "your_instagram_client_id":
        print_status("Instagram OAuth", True, "Configured")
        oauth_configured = True
    
    if linkedin_id and linkedin_id != "your_linkedin_client_id":
        print_status("LinkedIn OAuth", True, "Configured")
        oauth_configured = True
    
    if twitter_id and twitter_id != "your_twitter_client_id":
        print_status("Twitter OAuth", True, "Configured")
        oauth_configured = True
    
    if not oauth_configured:
        print_status("OAuth", True, "Not configured (optional for later)")
    
    # Summary
    print("\n" + "="*60)
    if all_good:
        print("✅ Configuration Complete!")
        print("\n📋 Next Steps:")
        print("1. Start/restart your backend:")
        print("   cd backend")
        print("   source venv/bin/activate")
        print("   python app.py")
        print("\n2. Test the API:")
        print("   curl http://127.0.0.1:5001/api/health")
        print("\n3. Open frontend:")
        print("   http://localhost:3000")
        print("\n🚀 You're ready to go!")
    else:
        print("⚠️  Configuration Incomplete")
        print("\n📋 Required Actions:")
        print("1. Add missing API keys to backend/.env")
        print("2. Run this script again to verify")
        print("\n💡 Quick setup:")
        print("   python setup_keys.py")
    print("="*60 + "\n")
    
    sys.exit(0 if all_good else 1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
