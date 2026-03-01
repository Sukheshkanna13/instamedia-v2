#!/usr/bin/env python3
"""
Interactive script to set up API keys for InstaMedia AI
Run: python setup_keys.py
"""

import os
import sys
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def print_step(number, text):
    print(f"\n📍 Step {number}: {text}")

def get_input(prompt, default=""):
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()

def update_env_file(key, value):
    """Update or add a key-value pair in .env file"""
    env_path = Path(__file__).parent / ".env"
    
    if not env_path.exists():
        print("❌ Error: .env file not found!")
        print("Creating .env from .env.example...")
        example_path = Path(__file__).parent / ".env.example"
        if example_path.exists():
            with open(example_path, 'r') as f:
                content = f.read()
            with open(env_path, 'w') as f:
                f.write(content)
        else:
            print("❌ Error: .env.example not found!")
            return False
    
    # Read current content
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    # Update or add the key
    key_found = False
    new_lines = []
    for line in lines:
        if line.strip().startswith(f"{key}="):
            new_lines.append(f"{key}={value}\n")
            key_found = True
        else:
            new_lines.append(line)
    
    if not key_found:
        new_lines.append(f"\n{key}={value}\n")
    
    # Write back
    with open(env_path, 'w') as f:
        f.writelines(new_lines)
    
    return True

def main():
    print_header("InstaMedia AI - API Keys Setup")
    print("This script will help you configure your API keys.")
    print("You can skip optional keys by pressing Enter.")
    
    # Step 1: Choose LLM provider
    print_step(1, "Choose LLM Provider")
    print("1. Gemini (Recommended - Free: 15 req/min, 1M tokens/day)")
    print("2. Groq (Alternative - Fast inference)")
    
    choice = get_input("Enter choice (1 or 2)", "1")
    
    if choice == "1":
        provider = "gemini"
        print("\n✅ Selected: Gemini")
        print("📝 Get your free key: https://aistudio.google.com/app/apikey")
        
        api_key = get_input("\nEnter your Gemini API key")
        if api_key and api_key != "your_gemini_key_here":
            update_env_file("LLM_PROVIDER", provider)
            update_env_file("GEMINI_API_KEY", api_key)
            print("✅ Gemini API key saved!")
        else:
            print("⚠️  No API key provided. AI features will not work.")
    
    elif choice == "2":
        provider = "groq"
        print("\n✅ Selected: Groq")
        print("📝 Get your free key: https://console.groq.com")
        
        api_key = get_input("\nEnter your Groq API key")
        if api_key and api_key != "your_groq_key_here":
            update_env_file("LLM_PROVIDER", provider)
            update_env_file("GROQ_API_KEY", api_key)
            print("✅ Groq API key saved!")
        else:
            print("⚠️  No API key provided. AI features will not work.")
    
    # Step 2: Supabase (optional)
    print_step(2, "Supabase Configuration (Optional)")
    print("For development, you can skip this (uses in-memory storage).")
    print("For production, get free account: https://supabase.com")
    
    add_supabase = get_input("\nAdd Supabase credentials? (y/n)", "n").lower()
    
    if add_supabase == "y":
        supabase_url = get_input("Enter Supabase URL")
        supabase_key = get_input("Enter Supabase Anon Key")
        
        if supabase_url and supabase_key:
            update_env_file("SUPABASE_URL", supabase_url)
            update_env_file("SUPABASE_ANON_KEY", supabase_key)
            print("✅ Supabase credentials saved!")
    else:
        print("⏭️  Skipped Supabase (using in-memory storage)")
    
    # Step 3: OAuth (optional)
    print_step(3, "OAuth Configuration (Optional)")
    print("For social media posting. You can add these later.")
    
    add_oauth = get_input("\nAdd OAuth credentials? (y/n)", "n").lower()
    
    if add_oauth == "y":
        # Instagram
        print("\n📱 Instagram OAuth")
        print("Get from: https://developers.facebook.com/apps/")
        instagram_id = get_input("Instagram Client ID (or press Enter to skip)")
        if instagram_id:
            instagram_secret = get_input("Instagram Client Secret")
            update_env_file("INSTAGRAM_CLIENT_ID", instagram_id)
            update_env_file("INSTAGRAM_CLIENT_SECRET", instagram_secret)
            update_env_file("INSTAGRAM_REDIRECT_URI", "http://localhost:3000/auth/callback/instagram")
            print("✅ Instagram OAuth saved!")
        
        # LinkedIn
        print("\n💼 LinkedIn OAuth")
        print("Get from: https://www.linkedin.com/developers/apps")
        linkedin_id = get_input("LinkedIn Client ID (or press Enter to skip)")
        if linkedin_id:
            linkedin_secret = get_input("LinkedIn Client Secret")
            update_env_file("LINKEDIN_CLIENT_ID", linkedin_id)
            update_env_file("LINKEDIN_CLIENT_SECRET", linkedin_secret)
            update_env_file("LINKEDIN_REDIRECT_URI", "http://localhost:3000/auth/callback/linkedin")
            print("✅ LinkedIn OAuth saved!")
        
        # Twitter
        print("\n🐦 Twitter OAuth")
        print("Get from: https://developer.twitter.com/en/portal/dashboard")
        twitter_id = get_input("Twitter Client ID (or press Enter to skip)")
        if twitter_id:
            twitter_secret = get_input("Twitter Client Secret")
            update_env_file("TWITTER_CLIENT_ID", twitter_id)
            update_env_file("TWITTER_CLIENT_SECRET", twitter_secret)
            update_env_file("TWITTER_REDIRECT_URI", "http://localhost:3000/auth/callback/twitter")
            print("✅ Twitter OAuth saved!")
    else:
        print("⏭️  Skipped OAuth configuration")
    
    # Summary
    print_header("Setup Complete!")
    print("✅ Configuration saved to backend/.env")
    print("\n📋 Next Steps:")
    print("1. Restart your backend server:")
    print("   cd backend")
    print("   source venv/bin/activate")
    print("   python app.py")
    print("\n2. Test the API:")
    print("   Open: http://127.0.0.1:5001/api/health")
    print("\n3. Test the frontend:")
    print("   Open: http://localhost:3000")
    print("   Navigate to 'Content Ideation' and click 'Generate Ideas'")
    print("\n🚀 You're all set! Happy building!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
