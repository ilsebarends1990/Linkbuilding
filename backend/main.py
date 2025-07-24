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

class BlogPost(BaseModel):
    id: Optional[int] = None
    title: str
    slug: str
    content: str
    excerpt: Optional[str] = None
    status: str = "draft"  # draft or publish
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    featured_image: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class BlogCreateRequest(BaseModel):
    title: str
    content: str
    excerpt: Optional[str] = None
    status: str = "draft"
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    website_url: str

class BlogUpdateRequest(BlogCreateRequest):
    id: int

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

def load_websites_config():
    """Load website configuration from CSV file"""
    global websites_config
    config_file = Path(__file__).parent.parent / "websites_config.csv"
    
    try:
        websites_config = []
        with open(config_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['website_url'].strip():  # Skip empty rows
                    websites_config.append(WebsiteConfig(
                        website_url=row['website_url'].strip(),
                        page_id=int(row['page_id']),
                        username=row['username'].strip(),
                        app_password=row['app_password'].strip(),
                        site_name=row['site_name'].strip()
                    ))
        logger.info(f"✅ {len(websites_config)} websites loaded from config")
        return True
    except FileNotFoundError:
        logger.error(f"❌ Config file {config_file} not found!")
        return False
    except Exception as e:
        logger.error(f"❌ Error loading config: {e}")
        return False

def get_website_config(website_url: str) -> Optional[WebsiteConfig]:
    """Get website configuration by URL"""
    for config in websites_config:
        if config.website_url == website_url:
            return config
    return None

def save_websites_config():
    """Save website configurations to CSV file"""
    try:
        csv_path = Path("websites_config.csv")
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
        logger.info(f"Saved {len(websites_config)} website configurations to CSV")
    except Exception as e:
        logger.error(f"Error saving website configurations: {e}")
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
    """Add a link to a WordPress page"""
    try:
        # Use provided page_id or default from config
        target_page_id = page_id or config.page_id
        
        # Build API URL
        api_base = f"{config.website_url.rstrip('/')}/wp-json/wp/v2"
        
        # Step 1: Get existing page content
        response = requests.get(
            f"{api_base}/pages/{target_page_id}",
            auth=HTTPBasicAuth(config.username, config.app_password),
            timeout=30
        )
        
        if response.status_code != 200:
            return LinkResponse(
                success=False,
                message=f"Failed to fetch page: {response.status_code}",
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
            timeout=30
        )
        
        if update_response.status_code == 200:
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
                message=f"Failed to update page: {update_response.status_code}",
                website_url=config.website_url,
                page_id=target_page_id
            )
            
    except requests.exceptions.Timeout:
        return LinkResponse(
            success=False,
            message="Request timeout",
            website_url=config.website_url,
            page_id=target_page_id
        )
    except Exception as e:
        return LinkResponse(
            success=False,
            message=f"Error: {str(e)}",
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

@app.post("/add-link", response_model=LinkResponse)
async def add_link(request: LinkRequest):
    """Add a single link to a WordPress website"""
    config = get_website_config(request.website_url)
    if not config:
        raise HTTPException(status_code=404, detail="Website configuration not found")
    
    result = add_link_to_wordpress(
        config=config,
        anchor_text=request.anchor_text,
        link_url=str(request.link_url),
        page_id=request.page_id
    )
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    
    return result

@app.post("/add-bulk-links", response_model=List[LinkResponse])
async def add_bulk_links(request: BulkLinkRequest):
    """Add the same link to multiple WordPress websites"""
    results = []
    
    for website_url in request.website_urls:
        config = get_website_config(website_url)
        if not config:
            results.append(LinkResponse(
                success=False,
                message="Website configuration not found",
                website_url=website_url,
                page_id=request.page_id or 0
            ))
            continue
        
        result = add_link_to_wordpress(
            config=config,
            anchor_text=request.anchor_text,
            link_url=str(request.link_url),
            page_id=request.page_id
        )
        results.append(result)
    
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

# Blog Management Endpoints
@app.get("/blogs", response_model=List[BlogPost])
async def get_blogs(website_url: Optional[str] = None):
    """Get blog posts, optionally filtered by website"""
    # This is a placeholder - in a real implementation, you would
    # fetch from WordPress API or database
    return []

@app.post("/blogs", response_model=BlogPost)
async def create_blog(request: BlogCreateRequest):
    """Create a new blog post"""
    try:
        config = get_website_config(request.website_url)
        if not config:
            raise HTTPException(status_code=404, detail="Website not found")
        
        # This is a placeholder - in a real implementation, you would
        # create the blog post via WordPress API
        blog_post = BlogPost(
            id=1,  # Would be generated by WordPress
            title=request.title,
            slug=request.title.lower().replace(' ', '-'),
            content=request.content,
            excerpt=request.excerpt,
            status=request.status,
            categories=request.categories,
            tags=request.tags,
            created_at=datetime.now().isoformat()
        )
        
        logger.info(f"Blog post '{request.title}' created for {request.website_url}")
        return blog_post
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating blog post: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/blogs/{blog_id}", response_model=BlogPost)
async def update_blog(blog_id: int, request: BlogUpdateRequest):
    """Update an existing blog post"""
    try:
        config = get_website_config(request.website_url)
        if not config:
            raise HTTPException(status_code=404, detail="Website not found")
        
        # This is a placeholder - in a real implementation, you would
        # update the blog post via WordPress API
        blog_post = BlogPost(
            id=blog_id,
            title=request.title,
            slug=request.title.lower().replace(' ', '-'),
            content=request.content,
            excerpt=request.excerpt,
            status=request.status,
            categories=request.categories,
            tags=request.tags,
            updated_at=datetime.now().isoformat()
        )
        
        logger.info(f"Blog post {blog_id} updated for {request.website_url}")
        return blog_post
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating blog post: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/blogs/{blog_id}")
async def delete_blog(blog_id: int):
    """Delete a blog post"""
    try:
        # This is a placeholder - in a real implementation, you would
        # delete the blog post via WordPress API
        logger.info(f"Blog post {blog_id} deleted")
        return {"success": True, "message": f"Blog post {blog_id} deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting blog post: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
