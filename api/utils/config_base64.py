"""
Configuration management for Vercel deployment with Base64 support
Handles website configurations from environment variables (including Base64 encoded) or local JSON file
"""

import os
import json
import base64
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
    Load website configuration from environment variable (production) or JSON file (development)
    Supports Base64 encoded configuration for large datasets
    """
    try:
        # Check if running in Vercel (production)
        if os.environ.get("VERCEL_ENV"):
            logger.info("Loading config from environment variable (Vercel)")
            
            # First try Base64 encoded config (for large datasets)
            if os.environ.get("WEBSITES_CONFIG_BASE64"):
                logger.info("Using Base64 encoded configuration")
                encoded_config = os.environ.get("WEBSITES_CONFIG_BASE64", "")
                try:
                    config_json = base64.b64decode(encoded_config).decode('utf-8')
                    websites_data = json.loads(config_json)
                except Exception as e:
                    logger.error(f"Failed to decode Base64 config: {e}")
                    websites_data = []
            else:
                # Regular JSON string config
                config_json = os.environ.get("WEBSITES_CONFIG", "[]")
                websites_data = json.loads(config_json)
        else:
            # Local development - use JSON file
            logger.info("Loading config from local JSON file")
            config_path = Path(__file__).parent.parent / "data" / "websites_config.json"
            
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    websites_data = json.load(f)
            else:
                logger.warning(f"Config file {config_path} not found, using empty config")
                websites_data = []
        
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
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in config: {e}")
        return []
    except Exception as e:
        logger.error(f"❌ Error loading config: {e}")
        return []

def get_website_config(website_url: str, websites: List[WebsiteConfig]) -> Optional[WebsiteConfig]:
    """Get website configuration by URL"""
    for config in websites:
        if config.website_url == website_url:
            return config
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
            
            logger.info(f"✅ Saved {len(websites)} website configurations to {config_path}")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error saving config: {e}")
        return False
