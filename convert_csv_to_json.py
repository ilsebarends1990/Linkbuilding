#!/usr/bin/env python3
"""
Script om websites_config.csv te converteren naar JSON formaat
voor gebruik in Vercel deployment
"""

import csv
import json
from pathlib import Path

def convert_csv_to_json():
    """Converteer CSV naar JSON formaat"""
    csv_path = Path("websites_config.csv")
    json_path = Path("websites_config.json")
    
    if not csv_path.exists():
        print(f"❌ {csv_path} niet gevonden!")
        return False
    
    websites = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['website_url'].strip():
                    websites.append({
                        'website_url': row['website_url'].strip(),
                        'page_id': int(row['page_id']),
                        'username': row['username'].strip(),
                        'app_password': row['app_password'].strip(),
                        'site_name': row['site_name'].strip()
                    })
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(websites, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Geconverteerd: {len(websites)} websites naar {json_path}")
        
        # Print JSON string voor Vercel omgevingsvariabele
        json_string = json.dumps(websites, ensure_ascii=False)
        print(f"\n📋 Voor Vercel omgevingsvariabele WEBSITES_CONFIG:")
        print(json_string)
        
        return True
        
    except Exception as e:
        print(f"❌ Fout bij conversie: {e}")
        return False

if __name__ == "__main__":
    convert_csv_to_json()
