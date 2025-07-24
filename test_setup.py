#!/usr/bin/env python3
"""
Test script om de Vercel deployment setup te valideren
"""

import sys
import os
import json
from pathlib import Path

def test_project_structure():
    """Test of de project structuur correct is"""
    print("🔍 Testing project structure...")
    
    required_files = [
        "frontend/package.json",
        "frontend/vercel.json", 
        "frontend/.env.local",
        "frontend/src/services/api.ts",
        "api/index.py",
        "api/vercel.json",
        "api/requirements.txt",
        "api/utils/config.py",
        "api/utils/wordpress.py",
        "api/data/websites_config.json",
        "websites_config.json"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True

def test_config_files():
    """Test configuratie bestanden"""
    print("\n🔍 Testing configuration files...")
    
    # Test JSON config
    try:
        with open("websites_config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"✅ JSON config loaded: {len(config)} websites")
    except Exception as e:
        print(f"❌ JSON config error: {e}")
        return False
    
    # Test API config
    try:
        with open("api/data/websites_config.json", 'r', encoding='utf-8') as f:
            api_config = json.load(f)
        print(f"✅ API config loaded: {len(api_config)} websites")
    except Exception as e:
        print(f"❌ API config error: {e}")
        return False
    
    return True

def test_environment_files():
    """Test environment configuratie"""
    print("\n🔍 Testing environment files...")
    
    # Test frontend .env.local
    env_path = Path("frontend/.env.local")
    if env_path.exists():
        with open(env_path, 'r') as f:
            content = f.read()
        if "VITE_API_URL" in content:
            print("✅ Frontend environment configured")
        else:
            print("❌ VITE_API_URL not found in .env.local")
            return False
    else:
        print("❌ frontend/.env.local not found")
        return False
    
    return True

def test_api_imports():
    """Test of API imports werken"""
    print("\n🔍 Testing API imports...")
    
    # Change to api directory for imports
    original_path = sys.path.copy()
    api_path = str(Path("api").absolute())
    sys.path.insert(0, api_path)
    
    try:
        from utils.config import load_websites_config, WebsiteConfig
        from utils.wordpress import add_link_to_wordpress, test_wordpress_connection
        print("✅ API imports successful")
        
        # Test config loading
        configs = load_websites_config()
        print(f"✅ Config loading works: {len(configs)} websites loaded")
        
        return True
    except Exception as e:
        print(f"❌ API import error: {e}")
        return False
    finally:
        sys.path = original_path

def generate_deployment_summary():
    """Genereer deployment samenvatting"""
    print("\n📋 DEPLOYMENT SUMMARY")
    print("=" * 50)
    
    # Read config for summary
    try:
        with open("websites_config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"📊 Websites configured: {len(config)}")
        for site in config:
            print(f"   • {site['site_name']} ({site['website_url']})")
        
        # Generate environment variable
        config_str = json.dumps(config, ensure_ascii=False)
        print(f"\n🔑 Environment Variable for Vercel:")
        print(f"WEBSITES_CONFIG = {config_str}")
        
    except Exception as e:
        print(f"❌ Error generating summary: {e}")

def main():
    """Hoofdfunctie"""
    print("🚀 API WP - Vercel Deployment Setup Test")
    print("=" * 50)
    
    tests = [
        test_project_structure,
        test_config_files,
        test_environment_files,
        test_api_imports
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Setup is ready for Vercel deployment!")
        generate_deployment_summary()
    else:
        print("❌ Setup needs fixes before deployment")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
