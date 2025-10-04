#!/usr/bin/env python3
"""
API Key Generator
Generates secure API keys for n8n integration
"""

import secrets

def generate_api_key():
    """Generate a cryptographically secure API key"""
    return secrets.token_urlsafe(32)

if __name__ == '__main__':
    print("=" * 60)
    print("API KEY GENERATOR")
    print("=" * 60)
    print()
    print("Generated secure API key:")
    print()
    print(f"  {generate_api_key()}")
    print()
    print("=" * 60)
    print("SETUP INSTRUCTIONS:")
    print("=" * 60)
    print()
    print("1. Copy the API key above")
    print()
    print("2. Add to your .env file:")
    print("   N8N_API_KEY=<paste_key_here>")
    print()
    print("3. Restart your Flask application")
    print()
    print("4. In n8n HTTP Request node, add header:")
    print("   Name: X-API-Key")
    print("   Value: <paste_key_here>")
    print()
    print("=" * 60)
    print()
