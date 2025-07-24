#!/usr/bin/env python3
"""
Eenvoudig script om WordPress_websites_API-overzicht.csv te converteren naar JSON
"""

import csv
import json
import os
from pathlib import Path

def csv_to_json():
    """Converteer CSV naar JSON en .env formaat"""
    csv_file = "WordPress_websites_API-overzicht.csv"
    json_path = Path("websites_config.json")
    env_path = Path(".env.vercel")
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV bestand {csv_file} niet gevonden!")
        return False
    
    try:
        # Lees CSV bestand
        print(f"📖 CSV bestand lezen: {csv_file}")
        websites_data = []
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            # Detecteer het scheidingsteken (comma of puntkomma)
            dialect = csv.Sniffer().sniff(f.read(1024), delimiters=',;')
            f.seek(0)
            
            # Lees de header
            reader = csv.reader(f, dialect)
            headers = next(reader)
            
            # Zoek de juiste kolomindexen
            col_indexes = {}
            for i, header in enumerate(headers):
                header = header.strip()
                if header in ["Website URL", "website_url"]:
                    col_indexes["website_url"] = i
                elif header in ["Pagina ID", "page_id"]:
                    col_indexes["page_id"] = i
                elif header in ["Gebruikersnaam", "username"]:
                    col_indexes["username"] = i
                elif header in ["E-mail"]:
                    col_indexes["email"] = i
                elif header in ["Application Password", "app_password"]:
                    col_indexes["app_password"] = i
                elif header in ["Label", "site_name"]:
                    col_indexes["site_name"] = i
            
            print(f"📊 Gevonden kolommen: {col_indexes}")
            
            # Controleer of we alle benodigde kolommen hebben
            required_cols = ["website_url", "page_id", "app_password"]
            missing_cols = [col for col in required_cols if col not in col_indexes]
            
            if missing_cols:
                print(f"❌ Ontbrekende kolommen: {missing_cols}")
                print(f"Beschikbare kolommen: {headers}")
                return False
            
            # Gebruik username of email voor de username kolom
            username_col = "username" if "username" in col_indexes else "email"
            if username_col not in col_indexes:
                print("❌ Geen username of email kolom gevonden!")
                return False
            
            # Lees de data
            f.seek(0)
            next(reader)  # Skip header
            
            for row in reader:
                if len(row) >= max(col_indexes.values()):
                    website_url = row[col_indexes["website_url"]].strip()
                    
                    if website_url:
                        try:
                            # Haal waarden op met foutafhandeling
                            page_id_str = row[col_indexes["page_id"]].strip()
                            page_id = int(page_id_str) if page_id_str.isdigit() else 0
                            
                            username = row[col_indexes[username_col]].strip()
                            app_password = row[col_indexes["app_password"]].strip()
                            
                            site_name = ""
                            if "site_name" in col_indexes:
                                site_name = row[col_indexes["site_name"]].strip()
                            
                            # Alleen toevoegen als verplichte velden aanwezig zijn
                            if website_url and username and app_password:
                                website = {
                                    "website_url": website_url,
                                    "page_id": page_id,
                                    "username": username,
                                    "app_password": app_password,
                                    "site_name": site_name or website_url  # Gebruik URL als site_name indien leeg
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
        
        return True
        
    except Exception as e:
        print(f"❌ Fout bij conversie: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    csv_to_json()
