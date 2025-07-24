#!/usr/bin/env python3
"""
Script om WordPress_websites_API-overzicht.csv te converteren naar JSON en .env formaat
Specifiek voor het formaat met puntkomma als scheidingsteken
"""

import json
import os
import base64
from pathlib import Path

def csv_to_json():
    """Converteer CSV naar JSON en .env formaat"""
    csv_file = "WordPress_websites_API-overzicht.csv"
    json_path = Path("websites_config.json")
    env_path = Path(".env.vercel")
    env_base64_path = Path(".env.vercel.base64")
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV bestand {csv_file} niet gevonden!")
        return False
    
    try:
        # Lees CSV bestand
        print(f"📖 CSV bestand lezen: {csv_file}")
        websites_data = []
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            # Lees de header
            header_line = f.readline().strip()
            headers = header_line.split(';')
            
            # Zoek de juiste kolomindexen
            col_indexes = {}
            for i, header in enumerate(headers):
                header = header.strip()
                if header == "Website URL":
                    col_indexes["website_url"] = i
                elif header == "Pagina ID":
                    col_indexes["page_id"] = i
                elif header == "Gebruikersnaam":
                    col_indexes["username"] = i
                elif header == "E-mail":
                    col_indexes["email"] = i
                elif header == "Application Password":
                    col_indexes["app_password"] = i
                elif header == "Label":
                    col_indexes["site_name"] = i
            
            print(f"📊 Gevonden kolommen: {col_indexes}")
            
            # Lees de data
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                # Split op puntkomma, maar houd rekening met mogelijke puntkomma's in velden
                row = line.split(';')
                
                if len(row) >= max(col_indexes.values()):
                    website_url = row[col_indexes["website_url"]].strip()
                    
                    if website_url:
                        try:
                            # Haal waarden op met foutafhandeling
                            page_id_str = row[col_indexes["page_id"]].strip()
                            page_id = int(page_id_str) if page_id_str.isdigit() else 0
                            
                            # Gebruik username of email voor de username kolom
                            username = row[col_indexes["username"]].strip()
                            if not username and "email" in col_indexes:
                                username = row[col_indexes["email"]].strip()
                                
                            app_password = row[col_indexes["app_password"]].strip()
                            
                            site_name = ""
                            if "site_name" in col_indexes:
                                site_name = row[col_indexes["site_name"]].strip()
                            
                            # Alleen toevoegen als verplichte velden aanwezig zijn
                            if website_url and username and app_password:
                                # Zorg ervoor dat de website URL correct is geformatteerd
                                if not website_url.startswith('http'):
                                    website_url = 'https://' + website_url
                                
                                # Verwijder trailing slash indien aanwezig
                                if website_url.endswith('/'):
                                    website_url = website_url[:-1]
                                
                                website = {
                                    "website_url": website_url,
                                    "page_id": page_id,
                                    "username": username,
                                    "app_password": app_password,
                                    "site_name": site_name or website_url.replace('https://', '').replace('http://', '')
                                }
                                websites_data.append(website)
                                print(f"✅ Website toegevoegd: {website_url}")
                            else:
                                print(f"⚠️ Overgeslagen rij met onvolledige data: {website_url}")
                        except Exception as e:
                            print(f"⚠️ Fout bij verwerken rij: {e}")
        
        # Schrijf naar JSON bestand
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(websites_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Geconverteerd: {len(websites_data)} websites naar {json_path}")
        
        # Schrijf naar .env bestand voor Vercel
        json_string = json.dumps(websites_data, ensure_ascii=False)
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(f"WEBSITES_CONFIG='{json_string}'\n")
        
        print(f"✅ Geconverteerd: {len(websites_data)} websites naar {env_path}")
        
        # Maak Base64 versie voor grote configuraties
        json_bytes = json_string.encode('utf-8')
        base64_bytes = base64.b64encode(json_bytes)
        base64_string = base64_bytes.decode('utf-8')
        
        with open(env_base64_path, 'w', encoding='utf-8') as f:
            f.write(f"WEBSITES_CONFIG_BASE64='{base64_string}'\n")
        
        print(f"✅ Base64 versie gemaakt in {env_base64_path} (voor zeer grote configuraties)")
        
        # Kopieer naar api/data map voor lokale ontwikkeling
        data_dir = Path("api") / "data"
        if data_dir.exists():
            data_json_path = data_dir / "websites_config.json"
            with open(data_json_path, 'w', encoding='utf-8') as f:
                json.dump(websites_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Gekopieerd naar {data_json_path} voor lokale ontwikkeling")
        
        # Toon statistieken
        print("\n📊 Statistieken:")
        print(f"- Totaal aantal websites: {len(websites_data)}")
        print(f"- JSON bestandsgrootte: {os.path.getsize(json_path) / 1024:.2f} KB")
        print(f"- .env bestandsgrootte: {os.path.getsize(env_path) / 1024:.2f} KB")
        print(f"- Base64 .env bestandsgrootte: {os.path.getsize(env_base64_path) / 1024:.2f} KB")
        
        return True
        
    except Exception as e:
        print(f"❌ Fout bij conversie: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    csv_to_json()
