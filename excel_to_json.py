#!/usr/bin/env python3
"""
Script om Excel bestand te converteren naar websites_config.json
en .env.vercel bestand voor Vercel deployment
"""

import pandas as pd
import json
import base64
from pathlib import Path
import os
import sys

def excel_to_json(excel_file=None):
    """Converteer Excel naar JSON en .env formaat"""
    # Zoek naar Excel bestanden als er geen is opgegeven
    if not excel_file:
        # Zoek naar verschillende Excel formaten in huidige map en submappen
        excel_files = []
        for ext in [".xlsx", ".xls", ".xlsm", ".xlsb", ".csv"]:
            excel_files.extend(list(Path(".").glob(f"*{ext}")))
            excel_files.extend(list(Path(".").glob(f"*/*{ext}")))
        
        if not excel_files:
            print("❌ Geen Excel bestand gevonden in de huidige map of submappen!")
            print("   Geef het pad naar het Excel bestand op als argument:")
            print("   python excel_to_json.py pad/naar/bestand.xlsx")
            return False
        
        # Toon gevonden bestanden en laat gebruiker kiezen
        print("📊 Gevonden Excel bestanden:")
        for i, file in enumerate(excel_files):
            print(f"  {i+1}. {file}")
        
        # Als er maar één bestand is, gebruik die automatisch
        if len(excel_files) == 1:
            excel_file = excel_files[0]
            print(f"📊 Automatisch gekozen: {excel_file}")
        else:
            # Anders vraag welke te gebruiken
            try:
                choice = input("Kies een bestand (nummer): ")
                excel_file = excel_files[int(choice) - 1]
                print(f"📊 Gekozen bestand: {excel_file}")
            except (ValueError, IndexError):
                print("❌ Ongeldige keuze!")
                return False
    else:
        excel_file = Path(excel_file)
        if not excel_file.exists():
            print(f"❌ Excel bestand {excel_file} niet gevonden!")
            return False
    
    json_path = Path("websites_config.json")
    env_path = Path(".env.vercel")
    
    try:
        # Lees Excel of CSV bestand
        print(f"📖 Bestand lezen: {excel_file}")
        if str(excel_file).lower().endswith('.csv'):
            print("Bestand wordt gelezen als CSV")
            df = pd.read_csv(excel_file, sep=';', encoding='utf-8')
        else:
            print("Bestand wordt gelezen als Excel")
            df = pd.read_excel(excel_file)
        
        # Controleer en map kolomnamen
        # Verwachte kolomnamen in de code
        expected_columns = ['website_url', 'page_id', 'username', 'app_password', 'site_name']
        
        # Mogelijke kolomnamen in het CSV/Excel bestand
        column_mapping = {
            'Website URL': 'website_url',
            'website_url': 'website_url',
            'Pagina ID': 'page_id',
            'page_id': 'page_id',
            'Gebruikersnaam': 'username',
            'username': 'username',
            'E-mail': 'username',  # E-mail wordt gebruikt als username
            'Application Password': 'app_password',
            'app_password': 'app_password',
            'Label': 'site_name',
            'site_name': 'site_name'
        }
        
        # Hernoem kolommen indien nodig
        renamed_columns = {}
        for col in df.columns:
            if col in column_mapping:
                renamed_columns[col] = column_mapping[col]
        
        if renamed_columns:
            df = df.rename(columns=renamed_columns)
            print(f"✅ Kolommen hernoemd: {renamed_columns}")
        
        # Controleer of alle verplichte kolommen nu aanwezig zijn
        missing_columns = [col for col in expected_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ Nog steeds ontbrekende kolommen: {', '.join(missing_columns)}")
            print(f"Beschikbare kolommen na hernoemen: {', '.join(df.columns)}")
            return False
        
        # Converteer naar lijst van dictionaries
        websites_data = []
        for _, row in df.iterrows():
            if pd.notna(row['website_url']) and str(row['website_url']).strip():
                # Controleer en zet waarden om met foutafhandeling
                try:
                    website_url = str(row['website_url']).strip() if pd.notna(row['website_url']) else ""
                    page_id = int(row['page_id']) if pd.notna(row['page_id']) else 0
                    username = str(row['username']).strip() if pd.notna(row['username']) else ""
                    app_password = str(row['app_password']).strip() if pd.notna(row['app_password']) else ""
                    site_name = str(row['site_name']).strip() if pd.notna(row['site_name']) else ""
                    
                    # Alleen toevoegen als alle verplichte velden aanwezig zijn
                    if website_url and username and app_password:
                        website = {
                            'website_url': website_url,
                            'page_id': page_id,
                            'username': username,
                            'app_password': app_password,
                            'site_name': site_name or website_url  # Gebruik URL als site_name indien leeg
                        }
                        websites_data.append(website)
                    else:
                        print(f"⚠️ Overgeslagen rij met onvolledige data: {website_url}")
                except Exception as e:
                    print(f"⚠️ Fout bij verwerken rij: {e}")
                    continue
        
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
        
        # Base64 encode voor grote configuraties
        encoded = base64.b64encode(json_string.encode('utf-8')).decode('utf-8')
        with open(".env.vercel.base64", 'w', encoding='utf-8') as f:
            f.write(f"WEBSITES_CONFIG_BASE64='{encoded}'\n")
        
        print(f"✅ Base64 versie gemaakt in .env.vercel.base64 (voor zeer grote configuraties)")
        
        # Toon statistieken
        print("\n📊 Statistieken:")
        print(f"- Totaal aantal websites: {len(websites_data)}")
        print(f"- JSON bestandsgrootte: {os.path.getsize(json_path) / 1024:.2f} KB")
        print(f"- .env bestandsgrootte: {os.path.getsize(env_path) / 1024:.2f} KB")
        
        # Waarschuwing voor grote bestanden
        if os.path.getsize(env_path) > 50 * 1024:  # 50 KB
            print("\n⚠️ Waarschuwing: .env bestand is groot (>50 KB).")
            print("   Overweeg de Base64-gecodeerde versie te gebruiken voor Vercel.")
        
        return True
        
    except Exception as e:
        print(f"❌ Fout bij conversie: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Gebruik opgegeven bestandsnaam of zoek automatisch
    excel_file = sys.argv[1] if len(sys.argv) > 1 else "WordPress_websites_API-overzicht.csv"
    excel_to_json(excel_file)
