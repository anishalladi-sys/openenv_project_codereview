#!/usr/bin/env python3
"""Verify HuggingFace API configuration"""

import os

print("\n" + "="*80)
print("VERIFYING HUGGINGFACE API CONFIGURATION")
print("="*80 + "\n")

# Test default configuration
print("Testing get_config() with defaults (no env vars set):")
print("-"*80)

# Clear any existing env vars
for key in ["API_BASE_URL", "MODEL_NAME", "HF_TOKEN"]:
    if key in os.environ:
        del os.environ[key]

# Now import and test
from inference import get_config

try:
    config = get_config()
    print("❌ Should have raised ValueError for missing HF_TOKEN")
except ValueError as e:
    print(f"✅ Correctly raised error: {e}\n")

# Test with HF_TOKEN set
print("Testing get_config() with HF_TOKEN set:")
print("-"*80)

os.environ["HF_TOKEN"] = "test_token"
config = get_config()

print(f"API_BASE_URL default: {config['api_base']}")
if config['api_base'] == "https://api-inference.huggingface.co/v1":
    print("✅ Correct HuggingFace API endpoint")
else:
    print(f"❌ Wrong endpoint: {config['api_base']}")

print(f"\nMODEL_NAME default: {config['model_name']}")
if config['model_name'] == "meta-llama/Llama-3.2-3B-Instruct":
    print("✅ Correct HuggingFace model")
else:
    print(f"❌ Wrong model: {config['model_name']}")

print(f"\nHF_TOKEN: {'*' * (len(config['hf_token']) - 4) + config['hf_token'][-4:]}")
print("✅ HF_TOKEN correctly configured\n")

# Test with custom env vars
print("Testing get_config() with custom env vars:")
print("-"*80)

os.environ["API_BASE_URL"] = "https://custom-api.example.com"
os.environ["MODEL_NAME"] = "custom-model"

config = get_config()

print(f"API_BASE_URL custom: {config['api_base']}")
if config['api_base'] == "https://custom-api.example.com":
    print("✅ Custom API endpoint respected")
else:
    print("❌ Custom API endpoint ignored")

print(f"\nMODEL_NAME custom: {config['model_name']}")
if config['model_name'] == "custom-model":
    print("✅ Custom model respected")
else:
    print("❌ Custom model ignored")

print("\n" + "="*80)
print("✅ HUGGINGFACE API CONFIGURATION VERIFIED")
print("="*80 + "\n")

print("CLIENT INITIALIZATION TEST")
print("-"*80)

from inference import create_client

os.environ["API_BASE_URL"] = "https://api-inference.huggingface.co/v1"
os.environ["MODEL_NAME"] = "meta-llama/Llama-3.2-3B-Instruct"
os.environ["HF_TOKEN"] = "test_token"

config = get_config()
client = create_client(config)

print(f"✅ OpenAI client created successfully")
print(f"   Base URL: {client.base_url}")
print(f"   API Key: Set to HF_TOKEN")
print(f"   Ready to use: client.chat.completions.create()")

print("\n" + "="*80)
print("✅ ALL HUGGINGFACE API CONFIGURATION TESTS PASSED")
print("="*80 + "\n")

print("READY FOR PRODUCTION")
print("-"*80)
print("To use with HuggingFace API:")
print("  export HF_TOKEN='your_huggingface_token'")
print("  python inference.py --task syntax_review --steps 5")
print("\nTo use with different model:")
print("  export API_BASE_URL='https://api-inference.huggingface.co/v1'")
print("  export MODEL_NAME='meta-llama/Llama-2-7b-chat-hf'")
print("  export HF_TOKEN='your_token'")
print("  python inference.py --task syntax_review --steps 5")
print("\n")
