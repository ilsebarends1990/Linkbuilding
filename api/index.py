"""
Main API handler for Vercel serverless deployment
Handles all API endpoints for WordPress Link Manager
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
import logging
import os

# Import utilities
from utils.config import load_websites_config, get_website_config, save_websites_config, WebsiteConfig
from utils.wordpress import add_link_to_wordpress, test_wordpress_connection

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="WordPress Link Manager API",
    description="API voor het beheren van links op WordPress websites (Vercel)",
    version="2.0.0"
)

# CORS middleware - updated for Vercel deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://*.vercel.app",  # All Vercel apps
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative dev server
        "http://localhost:8080",  # Alternative dev server
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Pydantic models
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

class LinkResponse(BaseModel):
    success: bool
    message: str
    website_url: str
    page_id: int
    link_added: bool = False

class WebsiteListResponse(BaseModel):
    websites: List[Dict[str, Any]]

class WebsiteResponse(BaseModel):
    success: bool
    message: str
    website_url: str
    site_name: str

# Global variable to store website configs (loaded on each request in serverless)
websites_config: List[WebsiteConfig] = []

def ensure_config_loaded():
    """Ensure website configuration is loaded"""
    global websites_config
    if not websites_config:
        websites_config = load_websites_config()
    return websites_config

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "WordPress Link Manager API (Vercel)", 
        "version": "2.0.0",
        "environment": os.environ.get("VERCEL_ENV", "development")
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    configs = ensure_config_loaded()
    return {
        "status": "healthy",
        "websites_loaded": len(configs),
        "environment": os.environ.get("VERCEL_ENV", "development"),
        "timestamp": "2025-07-24T09:37:00Z"
    }

@app.get("/websites", response_model=WebsiteListResponse)
async def get_websites():
    """Get list of available websites"""
    configs = ensure_config_loaded()
    websites = [
        {
            "website_url": config.website_url,
            "site_name": config.site_name,
            "page_id": config.page_id
        }
        for config in configs
    ]
    return WebsiteListResponse(websites=websites)

@app.post("/add-link", response_model=LinkResponse)
async def add_link(request: LinkRequest):
    """Add a single link to a WordPress website"""
    configs = ensure_config_loaded()
    config = get_website_config(request.website_url, configs)
    
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
    
    return LinkResponse(**result.to_dict())

@app.post("/add-bulk-links", response_model=List[LinkResponse])
async def add_bulk_links(request: BulkLinkRequest):
    """Add the same link to multiple WordPress websites"""
    configs = ensure_config_loaded()
    results = []
    
    for website_url in request.website_urls:
        config = get_website_config(website_url, configs)
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
        
        results.append(LinkResponse(**result.to_dict()))
    
    return results

@app.post("/websites", response_model=WebsiteResponse)
async def add_website(request: WebsiteRequest):
    """Add a new website configuration"""
    configs = ensure_config_loaded()
    
    # Check if website already exists
    existing = get_website_config(request.website_url, configs)
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
    configs.append(new_config)
    
    # Try to save (will work in development, not in production)
    save_success = save_websites_config(configs)
    if not save_success and not os.environ.get("VERCEL_ENV"):
        raise HTTPException(status_code=500, detail="Failed to save configuration")
    
    logger.info(f"Added new website configuration: {request.website_url}")
    return WebsiteResponse(
        success=True,
        message="Website added successfully" + (" (restart required in production)" if os.environ.get("VERCEL_ENV") else ""),
        website_url=request.website_url,
        site_name=request.site_name
    )

@app.get("/test-connection/{website_url:path}")
async def test_connection(website_url: str):
    """Test connection to a WordPress website"""
    configs = ensure_config_loaded()
    config = get_website_config(website_url, configs)
    
    if not config:
        raise HTTPException(status_code=404, detail="Website configuration not found")
    
    result = test_wordpress_connection(config)
    return result

# Export the app for Vercel
handler = app
