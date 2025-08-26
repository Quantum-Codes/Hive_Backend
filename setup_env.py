#!/usr/bin/env python3
"""
Setup script for Hive Backend environment configuration.
This script helps users create their .env file from the template.
"""

import os
import shutil
from pathlib import Path

def setup_environment():
    """Set up the environment configuration file."""
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    # Check if env.example exists
    if not os.path.exists('env.example'):
        print("❌ env.example file not found!")
        print("Please make sure you're running this script from the project root directory.")
        return
    
    try:
        # Copy env.example to .env
        shutil.copy('env.example', '.env')
        print("✅ Successfully created .env file from template!")
        print("\n📝 Next steps:")
        print("1. Edit the .env file with your actual configuration values")
        print("2. Get your Supabase credentials from: https://supabase.com/dashboard")
        print("3. Get your OpenAI API key from: https://platform.openai.com/api-keys")
        print("4. Generate a secure secret key: python -c \"import secrets; print(secrets.token_urlsafe(32))\"")
        print("\n🚀 After configuring, run: uvicorn app.main:app --reload")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")

if __name__ == "__main__":
    setup_environment()
