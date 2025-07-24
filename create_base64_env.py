#!/usr/bin/env python3
"""
Script om een base64 gecodeerde versie van de environment variable te maken voor Vercel
Dit helpt bij het omzeilen van de 4KB limiet voor environment variables
"""

import json
import csv
import base64
import os
from pathlib import Path

def create_base64_env():
    """Maak een base64 gecodeerde versie van de WEBSITES_CONFIG environment variable"""
    
    # Probeer eerst de JSON te laden uit het CSV bestand
    csv_file = Path("websites_config.csv")
    json_file = Path("websites_config.json")
    
    websites = []
    
    # Probeer eerst uit JSON bestand te laden als die bestaat
    if json_file.exists():
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                websites = json.load(f)
            print(f"✅ {len(websites)} websites geladen uit JSON bestand")
        except Exception as e:
            print(f"❌ Fout bij laden van JSON bestand: {e}")
            websites = []
    
    # Als er geen websites zijn geladen, probeer dan uit CSV
    if not websites and csv_file.exists():
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['website_url'].strip():
                        websites.append({
                            "website_url": row['website_url'].strip(),
                            "page_id": int(row['page_id']),
                            "username": row['username'].strip(),
                            "app_password": row['app_password'].strip(),
                            "site_name": row['site_name'].strip()
                        })
            print(f"✅ {len(websites)} websites geladen uit CSV bestand")
        except Exception as e:
            print(f"❌ Fout bij laden van CSV bestand: {e}")
            return
    
    if not websites:
        print("❌ Geen websites gevonden om te verwerken!")
        return
    
    # Valideer en rapporteer websites zonder page_id
    missing_page_ids = [website for website in websites if website['page_id'] == 0]
    if missing_page_ids:
        print(f"⚠️ Waarschuwing: {len(missing_page_ids)} websites hebben geen geldige page_id")
        for website in missing_page_ids[:5]:  # Toon de eerste 5
            print(f"   - {website['website_url']}")
        if len(missing_page_ids) > 5:
            print(f"   - ... en {len(missing_page_ids) - 5} meer")
    
    # Maak compacte JSON (geen spaties)
    compact_json = json.dumps(websites, separators=(',', ':'))
    
    # Codeer naar base64
    base64_encoded = base64.b64encode(compact_json.encode('utf-8')).decode('utf-8')
    
    # Schrijf naar .env.vercel.base64
    with open('.env.vercel.base64', 'w', encoding='utf-8') as f:
        f.write(f"WEBSITES_CONFIG_BASE64='{base64_encoded}'\n")
    
    # Schrijf ook de normale JSON versie voor referentie
    with open('.env.vercel', 'w', encoding='utf-8') as f:
        f.write(f"WEBSITES_CONFIG='{compact_json}'\n")
    
    # Toon statistieken
    print(f"\n📊 Statistieken:")
    print(f"   - Aantal websites: {len(websites)}")
    print(f"   - JSON grootte: {len(compact_json)} karakters")
    print(f"   - Base64 grootte: {len(base64_encoded)} karakters")
    
    # Controleer of het te lang is voor Vercel (4KB limiet)
    if len(compact_json) > 4000:
        print(f"⚠️ Waarschuwing: JSON is {len(compact_json)} karakters, te lang voor Vercel")
        print(f"✅ Base64 versie is {len(base64_encoded)} karakters")
        if len(base64_encoded) > 4000:
            print(f"⚠️ Waarschuwing: Ook de Base64 versie is te lang voor Vercel!")
            print("💡 Overweeg om de configuratie op te splitsen of een externe service te gebruiken")
        else:
            print("✅ Base64 versie past binnen de Vercel limiet")
    else:
        print("✅ JSON is klein genoeg voor Vercel environment variables")
    
    print(f"\n📁 Bestanden gemaakt:")
    print(f"   - .env.vercel (normale JSON)")
    print(f"   - .env.vercel.base64 (base64 gecodeerd)")
    
    print("\n💡 Instructies voor Vercel:")
    print("   1. Gebruik de inhoud van .env.vercel.base64 voor de WEBSITES_CONFIG_BASE64 environment variable")
    print("   2. Zorg dat de backend code base64 decoding ondersteunt (main.py is aangepast)")
    print("   3. Deploy de applicatie opnieuw en controleer de logs")
    
    return base64_encoded

if __name__ == "__main__":
    create_base64_env()
