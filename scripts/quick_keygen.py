"""
Quick API Key Generator - Run this to get your N8N_API_KEY
"""
import secrets

print("=" * 60)
print("Your new API Key:")
print("=" * 60)
print()
key = secrets.token_urlsafe(32)
print(key)
print()
print("=" * 60)
print("Add this to your .env file:")
print("=" * 60)
print(f"N8N_API_KEY={key}")
print()
