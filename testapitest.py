import requests
from requests.auth import HTTPBasicAuth

# CONFIGURATIE (vervang deze gegevens met je eigen info)
API_BASE = "https://www.allincv.nl/wp-json/wp/v2"
PAGE_ID = 49  # Dit is de ID van de 'linkpagina'
USERNAME = "info@drijfveermedia.nl"
APP_PASSWORD = "XXEaNPwdaX4T7MblMyC7d5Q0"

# HIER VUL JE DE LINK EN ANCHOR IN
anchor_tekst = "Mijn geweldige link"
link_url = "https://voorbeeldsite.nl"

# Bouw de HTML-link op
nieuwe_link = f'<a href="{link_url}">{anchor_tekst}</a><br>'

# Stap 1: Haal de bestaande pagina-inhoud op
response = requests.get(
    f"{API_BASE}/pages/{PAGE_ID}",
    auth=HTTPBasicAuth(USERNAME, APP_PASSWORD)
)

if response.status_code != 200:
    print("❌ Fout bij ophalen van pagina:", response.status_code)
    print(response.text)
    exit()

page_data = response.json()

# Probeer 'raw' op te halen (de originele content zonder extra HTML-opmaak)
bestaande_content = page_data.get("content", {}).get("raw")

# Als 'raw' niet beschikbaar is, val terug op 'rendered' (minder ideaal)
if not bestaande_content:
    bestaande_content = page_data.get("content", {}).get("rendered", "")
    print("⚠️ Let op: 'raw' content was niet beschikbaar, dus 'rendered' wordt gebruikt.")

# Stap 2: Check of link al bestaat
if link_url in bestaande_content:
    print("ℹ️ Link bestaat al. Geen actie ondernomen.")
    exit()

# Stap 3: Voeg de link toe onderaan de pagina
nieuwe_content = bestaande_content + "\n" + nieuwe_link

# Stap 4: Update de pagina met de nieuwe content
update_response = requests.post(
    f"{API_BASE}/pages/{PAGE_ID}",
    auth=HTTPBasicAuth(USERNAME, APP_PASSWORD),
    headers={"Content-Type": "application/json"},
    json={"content": nieuwe_content}
)

if update_response.status_code == 200:
    print("✅ Link succesvol toegevoegd!")
else:
    print("❌ Fout bij bijwerken van pagina:")
    print(update_response.text)
