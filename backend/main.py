from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
import requests
from requests.auth import HTTPBasicAuth
import csv
import json
import logging
from datetime import datetime
import os
import base64
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="WordPress Link Manager API",
    description="API voor het beheren van links op WordPress websites",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:8080"],  # Vite default ports
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic models
class WebsiteConfig(BaseModel):
    website_url: str
    page_id: int
    username: str
    app_password: str
    site_name: str

class LinkRequest(BaseModel):
    anchor_text: str
    link_url: HttpUrl
    website_url: str
    page_id: Optional[int] = None

class BulkLinkRequest(BaseModel):
    anchor_text: str
    link_url: HttpUrl
    website_urls: List[str]
    page_id: Optional[int] = None



class BulkLinkRequest(BaseModel):
    anchor_text: str
    link_url: HttpUrl
    website_urls: List[str]
    page_id: Optional[int] = None

class LinkResponse(BaseModel):
    success: bool
    message: str
    website_url: str
    page_id: int
    link_added: bool = False

class WebsiteListResponse(BaseModel):
    websites: List[Dict[str, Any]]

class ConfigInfoResponse(BaseModel):
    config_source: str
    total_websites: int
    environment_available: bool
    environment_base64_available: bool
    csv_file_available: bool
    loaded_at: str
    missing_page_ids: int
    websites_with_missing_ids: Optional[List[str]] = None

class WebsiteRequest(BaseModel):
    website_url: str
    site_name: str
    page_id: int
    username: str
    app_password: str

class UpdateWebsiteRequest(BaseModel):
    original_url: str
    website_url: str
    site_name: str
    page_id: int
    username: str
    app_password: str

class WebsiteResponse(BaseModel):
    success: bool
    message: str
    website_url: str
    site_name: str

# Global variable to store website configs
websites_config: List[WebsiteConfig] = []
config_source: str = "unknown"  # Track where config was loaded from
config_loaded_at: str = ""  # Track when config was loaded

def load_websites_config():
    """Load website configuration - hardcoded for reliable Vercel deployment"""
    global websites_config, config_source, config_loaded_at
    websites_config = []
    config_loaded_at = datetime.now().isoformat()
    
    # Detect environment (production if running on Vercel, development otherwise)
    is_production = (
        os.getenv('VERCEL') == '1' or 
        os.getenv('NODE_ENV') == 'production' or
        os.getenv('VERCEL_ENV') == 'production'
    )
    environment = 'production' if is_production else 'development'
    logger.info(f"🌍 Detected environment: {environment} (VERCEL={os.getenv('VERCEL')}, NODE_ENV={os.getenv('NODE_ENV')}, VERCEL_ENV={os.getenv('VERCEL_ENV')})")
    
    # Hardcoded website configurations for reliable deployment
    hardcoded_websites = [
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
    
    # Load hardcoded configurations
    missing_page_ids = 0
    for website_data in hardcoded_websites:
        # Validate page_id
        if website_data['page_id'] == 0 or not website_data['page_id']:
            missing_page_ids += 1
            logger.warning(f"⚠️ Missing page_id for {website_data['website_url']}")
        
        websites_config.append(WebsiteConfig(
            website_url=website_data['website_url'],
            page_id=website_data['page_id'],
            username=website_data['username'],
            app_password=website_data['app_password'],
            site_name=website_data['site_name']
        ))
    
    config_source = f"hardcoded_{environment}"
    logger.info(f"✅ {len(websites_config)} websites loaded from hardcoded configuration")
    if missing_page_ids > 0:
        logger.warning(f"⚠️ {missing_page_ids} websites have missing or invalid page_ids")
    return True

def get_website_config(website_url: str) -> Optional[WebsiteConfig]:
    """Get website configuration by URL with intelligent matching"""
    if not website_url:
        return None
    
    # First try exact match
    for config in websites_config:
        if config.website_url == website_url:
            return config
    
    # Then try root domain matching
    try:
        from urllib.parse import urlparse
        input_domain = urlparse(website_url.lower()).netloc.replace('www.', '')
        
        for config in websites_config:
            config_domain = urlparse(config.website_url.lower()).netloc.replace('www.', '')
            if input_domain == config_domain:
                logger.info(f"🔗 URL matched via domain: {website_url} -> {config.website_url}")
                return config
    except Exception as e:
        logger.warning(f"⚠️ Error in URL matching for {website_url}: {e}")
    
    logger.warning(f"❌ No website configuration found for: {website_url}")
    return None
    return None

def save_websites_config():
    """Save website configurations to JSON file"""
    try:
        # Detect environment
        is_production = os.getenv('VERCEL') == '1' or os.getenv('NODE_ENV') == 'production'
        environment = 'production' if is_production else 'development'
        
        # Save to environment-specific JSON file
        config_dir = Path(__file__).parent.parent / "config"
        config_dir.mkdir(exist_ok=True)  # Create config directory if it doesn't exist
        json_path = config_dir / f"websites_{environment}.json"
        
        # Convert websites_config to JSON-serializable format
        websites_data = []
        for config in websites_config:
            websites_data.append({
                'website_url': config.website_url,
                'page_id': config.page_id,
                'username': config.username,
                'app_password': config.app_password,
                'site_name': config.site_name
            })
        
        # Write to JSON file with proper formatting
        with open(json_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(websites_data, jsonfile, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Saved {len(websites_config)} website configurations to {json_path}")
        
        # Also save CSV backup for compatibility
        csv_path = Path(__file__).parent.parent / "websites_config.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['website_url', 'page_id', 'username', 'app_password', 'site_name']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for config in websites_config:
                writer.writerow({
                    'website_url': config.website_url,
                    'page_id': config.page_id,
                    'username': config.username,
                    'app_password': config.app_password,
                    'site_name': config.site_name
                })
        logger.info(f"📄 Also saved CSV backup to {csv_path}")
        
    except Exception as e:
        logger.error(f"❌ Error saving website configurations: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving configurations: {str(e)}")

def add_website_config(request: WebsiteRequest) -> WebsiteConfig:
    """Add a new website configuration"""
    # Check if website already exists
    existing = get_website_config(request.website_url)
    if existing:
        raise HTTPException(status_code=400, detail=f"Website {request.website_url} already exists")
    
    # Create new config
    new_config = WebsiteConfig(
        website_url=request.website_url,
        site_name=request.site_name,
        page_id=request.page_id,
        username=request.username,
        app_password=request.app_password
    )
    
    # Add to global list
    websites_config.append(new_config)
    
    # Save to CSV
    save_websites_config()
    
    logger.info(f"Added new website configuration: {request.website_url}")
    return new_config

def update_website_config(request: UpdateWebsiteRequest) -> WebsiteConfig:
    """Update an existing website configuration"""
    # Find existing config
    config_index = None
    for i, config in enumerate(websites_config):
        if config.website_url == request.original_url:
            config_index = i
            break
    
    if config_index is None:
        raise HTTPException(status_code=404, detail=f"Website {request.original_url} not found")
    
    # Check if new URL conflicts with existing (unless it's the same)
    if request.website_url != request.original_url:
        existing = get_website_config(request.website_url)
        if existing:
            raise HTTPException(status_code=400, detail=f"Website {request.website_url} already exists")
    
    # Update config
    updated_config = WebsiteConfig(
        website_url=request.website_url,
        site_name=request.site_name,
        page_id=request.page_id,
        username=request.username,
        app_password=request.app_password
    )
    
    websites_config[config_index] = updated_config
    
    # Save to CSV
    save_websites_config()
    
    logger.info(f"Updated website configuration: {request.original_url} -> {request.website_url}")
    return updated_config

def delete_website_config(website_url: str) -> bool:
    """Delete a website configuration"""
    # Find and remove config
    config_index = None
    for i, config in enumerate(websites_config):
        if config.website_url == website_url:
            config_index = i
            break
    
    if config_index is None:
        raise HTTPException(status_code=404, detail=f"Website {website_url} not found")
    
    # Remove from list
    removed_config = websites_config.pop(config_index)
    
    # Save to CSV
    save_websites_config()
    
    logger.info(f"Deleted website configuration: {website_url}")
    return True

def add_link_to_wordpress(config: WebsiteConfig, anchor_text: str, link_url: str, page_id: Optional[int] = None) -> LinkResponse:
    """Add a link to a WordPress page with detailed logging"""
    try:
        # Use provided page_id or default from config
        target_page_id = page_id or config.page_id
        
        logger.info(f"🔍 Attempting to add link to {config.website_url} (page {target_page_id})")
        logger.info(f"🔗 Link: '{anchor_text}' -> {link_url}")
        
        # Build API URL
        api_base = f"{config.website_url.rstrip('/')}/wp-json/wp/v2"
        
        # Step 1: Get existing page content
        logger.info(f"📥 Fetching page content from {api_base}/pages/{target_page_id}")
        response = requests.get(
            f"{api_base}/pages/{target_page_id}",
            auth=HTTPBasicAuth(config.username, config.app_password),
            timeout=60
        )
        
        if response.status_code != 200:
            error_msg = f"Failed to fetch page: HTTP {response.status_code}"
            logger.error(f"❌ {error_msg} from {config.website_url}")
            return LinkResponse(
                success=False,
                message=error_msg,
                website_url=config.website_url,
                page_id=target_page_id
            )
        
        page_data = response.json()
        logger.info(f"✅ Successfully fetched page data from {config.website_url}")
        
        # Get existing content (prefer raw over rendered)
        existing_content = page_data.get("content", {}).get("raw")
        if not existing_content:
            existing_content = page_data.get("content", {}).get("rendered", "")
        
        # Step 2: Check if link already exists
        if str(link_url) in existing_content:
            logger.info(f"🔄 Link already exists on {config.website_url}")
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
        
        logger.info(f"📤 Updating page content on {config.website_url}")
        
        # Step 4: Update the page
        update_response = requests.post(
            f"{api_base}/pages/{target_page_id}",
            auth=HTTPBasicAuth(config.username, config.app_password),
            headers={"Content-Type": "application/json"},
            json={"content": new_content},
            timeout=60
        )
        
        if update_response.status_code == 200:
            logger.info(f"✅ Successfully updated page on {config.website_url}")
            return LinkResponse(
                success=True,
                message="Link successfully added",
                website_url=config.website_url,
                page_id=target_page_id,
                link_added=True
            )
        else:
            error_msg = f"Failed to update page: HTTP {update_response.status_code}"
            logger.error(f"❌ {error_msg} on {config.website_url}")
            try:
                error_detail = update_response.json()
                logger.error(f"❌ Error details: {error_detail}")
            except:
                pass
            return LinkResponse(
                success=False,
                message=error_msg,
                website_url=config.website_url,
                page_id=target_page_id
            )
            
    except requests.exceptions.Timeout:
        error_msg = "Request timeout"
        logger.error(f"⏰ {error_msg} for {config.website_url}")
        return LinkResponse(
            success=False,
            message=error_msg,
            website_url=config.website_url,
            page_id=target_page_id
        )
    except requests.exceptions.ConnectionError:
        error_msg = "Connection error"
        logger.error(f"🔌 {error_msg} for {config.website_url}")
        return LinkResponse(
            success=False,
            message=error_msg,
            website_url=config.website_url,
            page_id=target_page_id
        )
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"💥 {error_msg} for {config.website_url}")
        return LinkResponse(
            success=False,
            message=error_msg,
            website_url=config.website_url,
            page_id=target_page_id
        )

# Load config on startup
@app.on_event("startup")
async def startup_event():
    load_websites_config()

# API Endpoints
@app.get("/")
async def root():
    return {"message": "WordPress Link Manager API", "version": "1.0.0"}

@app.get("/websites", response_model=WebsiteListResponse)
async def get_websites():
    """Get list of available websites"""
    websites = [
        {
            "website_url": config.website_url,
            "site_name": config.site_name,
            "page_id": config.page_id
        }
        for config in websites_config
    ]
    return WebsiteListResponse(websites=websites)

@app.get("/config-info", response_model=ConfigInfoResponse)
async def get_config_info():
    """Get information about the current configuration source"""
    # Check if environment variables are available
    env_available = bool(os.getenv('WEBSITES_CONFIG'))
    env_base64_available = bool(os.getenv('WEBSITES_CONFIG_BASE64'))
    
    # Check if CSV file is available
    config_file = Path(__file__).parent.parent / "websites_config.csv"
    csv_available = config_file.exists()
    
    # Collect information about missing page_ids
    websites_with_missing_ids = [config.website_url for config in websites_config if config.page_id == 0]
    missing_page_ids = len(websites_with_missing_ids)
    
    # If there are too many websites with missing IDs, limit the list to avoid response size issues
    if len(websites_with_missing_ids) > 50:
        websites_with_missing_ids = websites_with_missing_ids[:50] + [f"... and {len(websites_with_missing_ids) - 50} more"]
    
    return ConfigInfoResponse(
        config_source=config_source,
        total_websites=len(websites_config),
        environment_available=env_available,
        environment_base64_available=env_base64_available,
        csv_file_available=csv_available,
        loaded_at=config_loaded_at,
        missing_page_ids=missing_page_ids,
        websites_with_missing_ids=websites_with_missing_ids if missing_page_ids > 0 else None
    )

@app.post("/add-link", response_model=LinkResponse)
async def add_link(request: LinkRequest):
    """Add a single link to a WordPress website with logging"""
    logger.info(f"🔗 Single link request: '{request.anchor_text}' -> {request.link_url} on {request.website_url}")
    
    config = get_website_config(request.website_url)
    if not config:
        error_msg = f"Website configuration not found for {request.website_url}"
        logger.error(f"❌ {error_msg}")
        raise HTTPException(status_code=404, detail=error_msg)
    
    result = add_link_to_wordpress(
        config=config,
        anchor_text=request.anchor_text,
        link_url=str(request.link_url),
        page_id=request.page_id
    )
    
    if result.success:
        if result.link_added:
            logger.info(f"✅ Successfully added single link to {request.website_url}")
        else:
            logger.info(f"🔄 Link already exists on {request.website_url}")
    else:
        logger.error(f"❌ Failed to add single link to {request.website_url}: {result.message}")
        raise HTTPException(status_code=400, detail=result.message)
    
    return result

@app.post("/add-bulk-links", response_model=List[LinkResponse])
async def add_bulk_links(request: BulkLinkRequest):
    """Add the same link to multiple WordPress websites with comprehensive logging"""
    results = []
    successful_count = 0
    failed_count = 0
    
    logger.info(f"🚀 Starting bulk link operation for {len(request.website_urls)} websites")
    logger.info(f"🔗 Link details: '{request.anchor_text}' -> {request.link_url}")
    
    for i, website_url in enumerate(request.website_urls, 1):
        logger.info(f"📝 Processing website {i}/{len(request.website_urls)}: {website_url}")
        
        config = get_website_config(website_url)
        if not config:
            error_msg = f"Website configuration not found for {website_url}"
            logger.error(f"❌ {error_msg}")
            results.append(LinkResponse(
                success=False,
                message=error_msg,
                website_url=website_url,
                page_id=request.page_id or 0
            ))
            failed_count += 1
            continue
        
        try:
            result = add_link_to_wordpress(
                config=config,
                anchor_text=request.anchor_text,
                link_url=str(request.link_url),
                page_id=request.page_id
            )
            
            if result.success:
                if result.link_added:
                    logger.info(f"✅ Successfully added link to {website_url} (page {result.page_id})")
                    successful_count += 1
                else:
                    logger.info(f"🔄 Link already exists on {website_url} (page {result.page_id})")
                    successful_count += 1
            else:
                logger.error(f"❌ Failed to add link to {website_url}: {result.message}")
                failed_count += 1
            
            results.append(result)
            
        except Exception as e:
            error_msg = f"Unexpected error processing {website_url}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            results.append(LinkResponse(
                success=False,
                message=error_msg,
                website_url=website_url,
                page_id=request.page_id or config.page_id
            ))
            failed_count += 1
    
    # Summary logging
    logger.info(f"🏁 Bulk link operation completed:")
    logger.info(f"  ✅ Successful: {successful_count}/{len(request.website_urls)}")
    logger.info(f"  ❌ Failed: {failed_count}/{len(request.website_urls)}")
    
    if failed_count > 0:
        failed_sites = [r.website_url for r in results if not r.success]
        logger.warning(f"⚠️ Failed websites: {', '.join(failed_sites)}")
    
    return results

@app.post("/websites", response_model=WebsiteResponse)
async def add_website(request: WebsiteRequest):
    """Add a new website configuration"""
    try:
        config = add_website_config(request)
        return WebsiteResponse(
            success=True,
            message=f"Website {config.site_name} added successfully",
            website_url=config.website_url,
            site_name=config.site_name
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding website: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/websites", response_model=WebsiteResponse)
async def update_website(request: UpdateWebsiteRequest):
    """Update an existing website configuration"""
    try:
        config = update_website_config(request)
        return WebsiteResponse(
            success=True,
            message=f"Website {config.site_name} updated successfully",
            website_url=config.website_url,
            site_name=config.site_name
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating website: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/websites/{website_url:path}", response_model=WebsiteResponse)
async def delete_website(website_url: str):
    """Delete a website configuration"""
    try:
        # Get the config before deleting for response
        config = get_website_config(website_url)
        if not config:
            raise HTTPException(status_code=404, detail=f"Website {website_url} not found")
        
        delete_website_config(website_url)
        return WebsiteResponse(
            success=True,
            message=f"Website {config.site_name} deleted successfully",
            website_url=website_url,
            site_name=config.site_name
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting website: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/test-wordpress/{website_url:path}")
async def test_wordpress_connection(website_url: str):
    """Test WordPress API connection for a specific website"""
    config = get_website_config(website_url)
    if not config:
        raise HTTPException(status_code=404, detail=f"Website configuration not found for {website_url}")
    
    try:
        api_base = f"{config.website_url.rstrip('/')}/wp-json/wp/v2"
        logger.info(f"🧪 Testing WordPress connection to {api_base}")
        
        # Test basic API connectivity
        response = requests.get(
            f"{api_base}/pages/{config.page_id}",
            auth=HTTPBasicAuth(config.username, config.app_password),
            timeout=10
        )
        
        if response.status_code == 200:
            page_data = response.json()
            return {
                "success": True,
                "message": "WordPress API connection successful",
                "website_url": config.website_url,
                "page_id": config.page_id,
                "page_title": page_data.get("title", {}).get("rendered", "Unknown"),
                "status_code": response.status_code
            }
        else:
            return {
                "success": False,
                "message": f"WordPress API returned status {response.status_code}",
                "website_url": config.website_url,
                "page_id": config.page_id,
                "status_code": response.status_code
            }
            
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": "Connection timeout - WordPress site may be slow or unreachable",
            "website_url": config.website_url,
            "page_id": config.page_id
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Connection error: {str(e)}",
            "website_url": config.website_url,
            "page_id": config.page_id
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "websites_loaded": len(websites_config)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
