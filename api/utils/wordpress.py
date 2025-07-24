"""
WordPress API utility functions
Handles communication with WordPress REST API
"""

import requests
from requests.auth import HTTPBasicAuth
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class LinkResponse:
    """Response model for link operations"""
    def __init__(self, success: bool, message: str, website_url: str, page_id: int, link_added: bool = False):
        self.success = success
        self.message = message
        self.website_url = website_url
        self.page_id = page_id
        self.link_added = link_added
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'message': self.message,
            'website_url': self.website_url,
            'page_id': self.page_id,
            'link_added': self.link_added
        }

def add_link_to_wordpress(config, anchor_text: str, link_url: str, page_id: int = None, timeout: int = 30) -> LinkResponse:
    """
    Add a link to a WordPress page via REST API
    """
    try:
        # Use provided page_id or default from config
        target_page_id = page_id or config.page_id
        
        # Build API URL
        api_base = f"{config.website_url.rstrip('/')}/wp-json/wp/v2"
        
        logger.info(f"🔄 Adding link to {config.site_name} (Page ID: {target_page_id})")
        
        # Step 1: Get existing page content
        response = requests.get(
            f"{api_base}/pages/{target_page_id}",
            auth=HTTPBasicAuth(config.username, config.app_password),
            timeout=timeout
        )
        
        if response.status_code != 200:
            return LinkResponse(
                success=False,
                message=f"Failed to fetch page: HTTP {response.status_code}",
                website_url=config.website_url,
                page_id=target_page_id
            )
        
        page_data = response.json()
        
        # Get existing content (prefer raw over rendered)
        existing_content = page_data.get("content", {}).get("raw")
        if not existing_content:
            existing_content = page_data.get("content", {}).get("rendered", "")
        
        # Step 2: Check if link already exists
        if str(link_url) in existing_content:
            return LinkResponse(
                success=True,
                message="Link already exists",
                website_url=config.website_url,
                page_id=target_page_id,
                link_added=False
            )
        
        # Step 3: Add the new link
        new_link = f'<a href="{link_url}">{anchor_text}</a><br>'
        new_content = existing_content + "\n" + new_link
        
        # Step 4: Update the page
        update_response = requests.post(
            f"{api_base}/pages/{target_page_id}",
            auth=HTTPBasicAuth(config.username, config.app_password),
            headers={"Content-Type": "application/json"},
            json={"content": new_content},
            timeout=timeout
        )
        
        if update_response.status_code == 200:
            logger.info(f"✅ Link successfully added to {config.site_name}")
            return LinkResponse(
                success=True,
                message="Link successfully added",
                website_url=config.website_url,
                page_id=target_page_id,
                link_added=True
            )
        else:
            return LinkResponse(
                success=False,
                message=f"Failed to update page: HTTP {update_response.status_code}",
                website_url=config.website_url,
                page_id=target_page_id
            )
            
    except requests.exceptions.Timeout:
        logger.error(f"⏰ Timeout adding link to {config.site_name}")
        return LinkResponse(
            success=False,
            message=f"Request timeout after {timeout} seconds",
            website_url=config.website_url,
            page_id=target_page_id
        )
    except Exception as e:
        logger.error(f"❌ Error adding link to {config.site_name}: {e}")
        return LinkResponse(
            success=False,
            message=f"Error: {str(e)}",
            website_url=config.website_url,
            page_id=target_page_id
        )

def test_wordpress_connection(config, timeout: int = 10) -> Dict[str, Any]:
    """
    Test connection to WordPress site
    """
    try:
        api_base = f"{config.website_url.rstrip('/')}/wp-json/wp/v2"
        
        # Try to get site info
        response = requests.get(
            f"{api_base}/pages/{config.page_id}",
            auth=HTTPBasicAuth(config.username, config.app_password),
            timeout=timeout
        )
        
        if response.status_code == 200:
            page_data = response.json()
            return {
                'success': True,
                'message': 'Connection successful',
                'page_title': page_data.get('title', {}).get('rendered', 'Unknown'),
                'status_code': response.status_code
            }
        else:
            return {
                'success': False,
                'message': f'HTTP {response.status_code}',
                'status_code': response.status_code
            }
            
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'message': 'Connection timeout',
            'status_code': 408
        }
    except Exception as e:
        return {
            'success': False,
            'message': str(e),
            'status_code': 500
        }
