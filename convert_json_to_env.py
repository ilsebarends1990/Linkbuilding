#!/usr/bin/env python3
"""
Script om websites_config.json te converteren naar .env formaat
voor eenvoudige import in Vercel environment variables
"""

import json
import base64
from pathlib import Path

def convert_json_to_env():
    """Converteer JSON naar .env formaat"""
    json_path = Path("websites_config.json")
    env_path = Path(".env.vercel")
    
    if not json_path.exists():
        print(f"❌ {json_path} niet gevonden!")
        return False
    
    try:
        # Lees JSON bestand
        with open(json_path, 'r', encoding='utf-8') as f:
            websites_data = json.load(f)
        
        # Converteer naar JSON string
        json_string = json.dumps(websites_data, ensure_ascii=False)
        
        # Schrijf naar .env bestand
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(f"WEBSITES_CONFIG='{json_string}'\n")
        
        print(f"✅ Geconverteerd: {len(websites_data)} websites naar {env_path}")
        print(f"Je kunt dit bestand nu importeren in Vercel environment variables.")
        
        # Base64 encode voor grote configuraties (alternatieve methode)
        encoded = base64.b64encode(json_string.encode('utf-8')).decode('utf-8')
        with open(".env.vercel.base64", 'w', encoding='utf-8') as f:
            f.write(f"WEBSITES_CONFIG_BASE64='{encoded}'\n")
        
        print(f"✅ Base64 versie gemaakt in .env.vercel.base64 (voor zeer grote configuraties)")
        
        return True
        
    except Exception as e:
        print(f"❌ Fout bij conversie: {e}")
        return False

if __name__ == "__main__":
    convert_json_to_env()
