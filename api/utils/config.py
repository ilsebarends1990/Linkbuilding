"""
Configuration management for Vercel deployment
Handles website configurations from environment variables or local JSON file
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class WebsiteConfig:
    """Website configuration model"""
    def __init__(self, website_url: str, page_id: int, username: str, app_password: str, site_name: str):
        self.website_url = website_url
        self.page_id = page_id
        self.username = username
        self.app_password = app_password
        self.site_name = site_name
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'website_url': self.website_url,
            'page_id': self.page_id,
            'username': self.username,
            'app_password': self.app_password,
            'site_name': self.site_name
        }

def load_websites_config() -> List[WebsiteConfig]:
    """
    Load website configuration - hardcoded for reliable Vercel deployment
    """
    logger.info("Loading hardcoded website configuration")
    
    # Hardcoded website configurations for reliable deployment
    websites_data = [
        {
            "website_url": "https://www.allincv.nl",
            "page_id": 49,
            "username": "admin",
            "app_password": "XXEaNPwdaX4T7MblMyC7d5Q0",
            "site_name": "www.allincv.nl"
        },
        {
            "website_url": "https://www.aluminiumbedrijf.nl",
            "page_id": 142,
            "username": "admin",
            "app_password": "I53V VPj9 Z14Y lJfd jlkZ SrOJ",
            "site_name": "www.aluminiumbedrijf.nl"
        },
        {
            "website_url": "https://www.am-team.nl",
            "page_id": 7,
            "username": "admin",
            "app_password": "8EY7 Iiuj TZ4h ys2z Rfx8 1Ywd",
            "site_name": "www.am-team.nl"
        },
        {
            "website_url": "https://www.asbestcrew.nl",
            "page_id": 325,
            "username": "testwebsite3",
            "app_password": "8Gfs S3Nb GB3l 55RG dB40 DUZk",
            "site_name": "www.asbestcrew.nl"
        },
        {
            "website_url": "https://www.ashbyhoveniersbedrijf.nl",
            "page_id": 13025,
            "username": "v3xmt0",
            "app_password": "yjcf LmWn 5T62 iCte QJYv qn2T",
            "site_name": "www.ashbyhoveniersbedrijf.nl"
        }
    ]
    
    try:
        # Convert to WebsiteConfig objects
        websites = []
        for data in websites_data:
            if isinstance(data, dict) and data.get('website_url'):
                websites.append(WebsiteConfig(
                    website_url=data['website_url'],
                    page_id=int(data['page_id']),
                    username=data['username'],
                    app_password=data['app_password'],
                    site_name=data['site_name']
                ))
        
        logger.info(f"✅ Loaded {len(websites)} website configurations")
        return websites
        
    except Exception as e:
        logger.error(f"❌ Error loading config: {e}")
        return []

def get_website_config(website_url: str, websites: List[WebsiteConfig]) -> Optional[WebsiteConfig]:
    """Get website configuration by URL with intelligent matching"""
    if not website_url:
        return None
    
    # First try exact match
    for config in websites:
        if config.website_url == website_url:
            return config
    
    # Then try root domain matching
    try:
        from urllib.parse import urlparse
        input_domain = urlparse(website_url.lower()).netloc.replace('www.', '')
        
        for config in websites:
            config_domain = urlparse(config.website_url.lower()).netloc.replace('www.', '')
            if input_domain == config_domain:
                logger.info(f"🔗 URL matched via domain: {website_url} -> {config.website_url}")
                return config
    except Exception as e:
        logger.warning(f"⚠️ Error in URL matching for {website_url}: {e}")
    
    logger.warning(f"❌ No website configuration found for: {website_url}")
    return None

def save_websites_config(websites: List[WebsiteConfig]) -> bool:
    """
    Save website configurations
    In production (Vercel), this would need to update environment variables
    In development, save to JSON file
    """
    try:
        if os.environ.get("VERCEL_ENV"):
            # In production, we can't easily update environment variables
            # This would require integration with Vercel API or external storage
            logger.warning("Cannot save config in production environment")
            return False
        else:
            # Local development - save to JSON file
            config_path = Path(__file__).parent.parent / "data" / "websites_config.json"
            config_path.parent.mkdir(exist_ok=True)
            
            websites_data = [website.to_dict() for website in websites]
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(websites_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Saved {len(websites)} website configurations")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error saving config: {e}")
        return False
