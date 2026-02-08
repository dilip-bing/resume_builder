"""
Test which Gemini models are available with your API key
"""

import google.generativeai as genai
import streamlit as st

# Load API key
st.secrets.load_if_toml_exists()
api_key = st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=api_key)

print("=" * 70)
print("AVAILABLE GEMINI MODELS")
print("=" * 70)

try:
    models = genai.list_models()
    
    print("\nAll available models:")
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"\n✅ {model.name}")
            print(f"   Display name: {model.display_name}")
            print(f"   Supported methods: {', '.join(model.supported_generation_methods)}")
    
    print("\n" + "=" * 70)
    print("\nTesting models:")
    
    test_models = [
        'gemini-1.5-flash-latest',
        'gemini-1.5-flash',
        'gemini-1.0-pro',
        'gemini-pro',
        'models/gemini-1.5-flash',
        'models/gemini-pro'
    ]
    
    for model_name in test_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say 'test successful'")
            print(f"\n✅ {model_name} - WORKS!")
            print(f"   Response: {response.text[:50]}")
        except Exception as e:
            print(f"\n❌ {model_name} - FAILED")
            print(f"   Error: {str(e)[:100]}")
    
    print("\n" + "=" * 70)
    
except Exception as e:
    print(f"\n❌ Error listing models: {e}")

print("\nTest complete!")
