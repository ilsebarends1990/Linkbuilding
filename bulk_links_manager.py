import requests
from requests.auth import HTTPBasicAuth
import csv
import json
import time
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

# 📊 LOGGING SETUP
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bulk_links.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BulkLinksManager:
    """
    Professionele bulk links manager voor meerdere WordPress websites
    """
    
    def __init__(self, config_file='websites_config.csv'):
        self.config_file = config_file
        self.websites = []
        self.results = []
        
    def load_websites_config(self):
        """
        Laad website configuratie uit CSV bestand
        CSV format: website_url,page_id,username,app_password,site_name
        """
        try:
            with open(self.config_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self.websites = list(reader)
                logger.info(f"✅ {len(self.websites)} websites geladen uit {self.config_file}")
                return True
        except FileNotFoundError:
            logger.error(f"❌ Config bestand {self.config_file} niet gevonden!")
            self.create_example_config()
            return False
        except Exception as e:
            logger.error(f"❌ Fout bij laden config: {e}")
            return False
    
    def create_example_config(self):
        """Maak een voorbeeld configuratie bestand"""
        example_data = [
            {
                'website_url': 'https://website1.nl',
                'page_id': '49',
                'username': 'admin@website1.nl',
                'app_password': 'xxxx xxxx xxxx xxxx xxxx xxxx',
                'site_name': 'Website 1'
            },
            {
                'website_url': 'https://website2.nl',
                'page_id': '25',
                'username': 'info@website2.nl',
                'app_password': 'yyyy yyyy yyyy yyyy yyyy yyyy',
                'site_name': 'Website 2'
            }
        ]
        
        with open('websites_config_example.csv', 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['website_url', 'page_id', 'username', 'app_password', 'site_name']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(example_data)
        
        logger.info("📝 Voorbeeld config bestand aangemaakt: websites_config_example.csv")
    
    def add_link_to_website(self, website_config, link_data, timeout=30):
        """
        Voeg link toe aan een specifieke website
        """
        site_name = website_config.get('site_name', 'Onbekend')
        website_url = website_config['website_url']
        
        try:
            # API configuratie
            api_base = f"{website_url}/wp-json/wp/v2"
            page_id = website_config['page_id']
            username = website_config['username']
            app_password = website_config['app_password'].replace(' ', '')  # Spaties verwijderen
            
            logger.info(f"🔄 Bezig met {site_name} ({website_url})...")
            
            # Stap 1: Pagina ophalen
            response = requests.get(
                f"{api_base}/pages/{page_id}",
                auth=HTTPBasicAuth(username, app_password),
                timeout=timeout
            )
            
            if response.status_code != 200:
                return {
                    'site_name': site_name,
                    'website_url': website_url,
                    'status': 'FOUT',
                    'message': f"Kan pagina niet ophalen: {response.status_code}",
                    'timestamp': datetime.now().isoformat()
                }
            
            page_data = response.json()
            
            # Content ophalen
            bestaande_content = page_data.get("content", {}).get("raw")
            if not bestaande_content:
                bestaande_content = page_data.get("content", {}).get("rendered", "")
            
            # Stap 2: Check duplicaat
            if link_data['url'] in bestaande_content:
                return {
                    'site_name': site_name,
                    'website_url': website_url,
                    'status': 'BESTAAT_AL',
                    'message': 'Link bestaat al',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Stap 3: Link toevoegen
            nieuwe_link = f'<a href="{link_data["url"]}">{link_data["anchor"]}</a><br>'
            nieuwe_content = bestaande_content + "\n" + nieuwe_link
            
            # Stap 4: Update
            update_response = requests.post(
                f"{api_base}/pages/{page_id}",
                auth=HTTPBasicAuth(username, app_password),
                headers={"Content-Type": "application/json"},
                json={"content": nieuwe_content},
                timeout=timeout
            )
            
            if update_response.status_code == 200:
                return {
                    'site_name': site_name,
                    'website_url': website_url,
                    'status': 'SUCCES',
                    'message': 'Link succesvol toegevoegd',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'site_name': site_name,
                    'website_url': website_url,
                    'status': 'FOUT',
                    'message': f"Update gefaald: {update_response.status_code}",
                    'timestamp': datetime.now().isoformat()
                }
                
        except requests.exceptions.Timeout:
            return {
                'site_name': site_name,
                'website_url': website_url,
                'status': 'TIMEOUT',
                'message': f'Timeout na {timeout} seconden',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'site_name': site_name,
                'website_url': website_url,
                'status': 'FOUT',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def bulk_add_links(self, link_data, max_workers=5, delay_between_batches=2):
        """
        Voeg links toe aan alle websites (parallel processing)
        """
        if not self.websites:
            logger.error("❌ Geen websites geladen!")
            return False
        
        logger.info(f"🚀 Start bulk toevoegen van link: {link_data['anchor']}")
        logger.info(f"📊 Aantal websites: {len(self.websites)}")
        logger.info(f"⚡ Max workers: {max_workers}")
        
        # Parallel processing met ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit alle taken
            future_to_website = {
                executor.submit(self.add_link_to_website, website, link_data): website 
                for website in self.websites
            }
            
            # Verzamel resultaten
            for future in as_completed(future_to_website):
                website = future_to_website[future]
                try:
                    result = future.result()
                    self.results.append(result)
                    
                    # Log resultaat
                    status_emoji = {
                        'SUCCES': '✅',
                        'BESTAAT_AL': 'ℹ️',
                        'FOUT': '❌',
                        'TIMEOUT': '⏰'
                    }
                    emoji = status_emoji.get(result['status'], '❓')
                    logger.info(f"{emoji} {result['site_name']}: {result['message']}")
                    
                except Exception as e:
                    logger.error(f"❌ Onverwachte fout bij {website.get('site_name', 'Onbekend')}: {e}")
            
            # Kleine pauze tussen batches
            if delay_between_batches > 0:
                time.sleep(delay_between_batches)
        
        return True
    
    def generate_report(self, output_file='bulk_results.csv'):
        """Genereer rapport van resultaten"""
        if not self.results:
            logger.warning("⚠️ Geen resultaten om te rapporteren")
            return
        
        # Statistieken
        stats = {}
        for result in self.results:
            status = result['status']
            stats[status] = stats.get(status, 0) + 1
        
        # Rapport naar CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['site_name', 'website_url', 'status', 'message', 'timestamp']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results)
        
        # Console rapport
        logger.info(f"\n📊 BULK OPERATIE VOLTOOID")
        logger.info(f"=" * 40)
        logger.info(f"📁 Rapport opgeslagen: {output_file}")
        logger.info(f"📈 Statistieken:")
        for status, count in stats.items():
            percentage = (count / len(self.results)) * 100
            logger.info(f"   {status}: {count} ({percentage:.1f}%)")

def main():
    """Hoofdfunctie voor bulk links beheer"""
    
    # Initialiseer manager
    manager = BulkLinksManager('websites_config.csv')
    
    # Laad configuratie
    if not manager.load_websites_config():
        logger.error("❌ Kan niet verder zonder geldige configuratie")
        return
    
    # Link data
    link_data = {
        'url': 'https://bulk-test-link.nl',
        'anchor': 'Bulk Test Link'
    }
    
    # Voer bulk operatie uit
    success = manager.bulk_add_links(
        link_data=link_data,
        max_workers=3,  # Niet te veel om servers niet te overbelasten
        delay_between_batches=1
    )
    
    if success:
        # Genereer rapport
        manager.generate_report()
        logger.info("🎉 Bulk operatie voltooid!")
    else:
        logger.error("❌ Bulk operatie gefaald")

if __name__ == "__main__":
    main()
