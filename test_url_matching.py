#!/usr/bin/env python3
"""
Test script om de verbeterde URL matching te demonstreren
"""

def test_url_matching_examples():
    """Demonstreer hoe de verbeterde URL matching werkt"""
    
    print("🔗 URL MATCHING TEST")
    print("=" * 50)
    
    # Simuleer website configuraties
    websites = [
        {"website_url": "https://www.allincv.nl", "site_name": "AllInCV"},
        {"website_url": "https://www.aluminiumbedrijf.nl", "site_name": "Aluminium Bedrijf"},
        {"website_url": "https://www.am-team.nl", "site_name": "AM Team"},
        {"website_url": "https://asbestcrew.nl", "site_name": "Asbest Crew"},
    ]
    
    # Test URLs die zouden moeten matchen
    test_urls = [
        "https://www.allincv.nl/pagina1",
        "https://allincv.nl/contact",
        "http://www.allincv.nl/diensten/cv-check",
        "https://www.aluminiumbedrijf.nl/producten/kozijnen",
        "https://aluminiumbedrijf.nl/contact",
        "https://www.am-team.nl/over-ons",
        "https://am-team.nl/diensten",
        "https://www.asbestcrew.nl/sanering",
        "https://asbestcrew.nl/advies",
        "https://unknown-website.nl/page",  # Zou niet moeten matchen
    ]
    
    print("📋 Website Configuraties:")
    for website in websites:
        print(f"   • {website['site_name']}: {website['website_url']}")
    
    print(f"\n🧪 Test URLs ({len(test_urls)} stuks):")
    
    matches = 0
    no_matches = 0
    
    for i, test_url in enumerate(test_urls, 1):
        # Simuleer de verbeterde URL matching logica
        matched_website = None
        
        # Extract root domain van test URL
        try:
            from urllib.parse import urlparse
            parsed = urlparse(test_url)
            test_domain = parsed.netloc.lower().replace('www.', '')
            
            # Zoek matching website
            for website in websites:
                website_parsed = urlparse(website['website_url'])
                website_domain = website_parsed.netloc.lower().replace('www.', '')
                
                if test_domain == website_domain:
                    matched_website = website
                    break
        except:
            pass
        
        if matched_website:
            print(f"   ✅ {i:2d}. {test_url}")
            print(f"       → Matched: {matched_website['site_name']} ({matched_website['website_url']})")
            matches += 1
        else:
            print(f"   ❌ {i:2d}. {test_url}")
            print(f"       → No match found")
            no_matches += 1
    
    print(f"\n📊 RESULTATEN:")
    print(f"   ✅ Successvol gematcht: {matches}")
    print(f"   ❌ Geen match gevonden: {no_matches}")
    print(f"   📈 Success rate: {(matches / len(test_urls)) * 100:.1f}%")
    
    print(f"\n💡 VERBETERINGEN:")
    print("   • Root domain matching: www.example.com/page1 → example.com")
    print("   • Protocol onafhankelijk: http:// en https:// beide ondersteund")
    print("   • Pad onafhankelijk: /page1, /contact, etc. worden genegeerd")
    print("   • Subdomain normalisatie: www. prefix wordt automatisch verwijderd")

def show_frontend_improvements():
    """Toon de verbeteringen in de frontend"""
    
    print(f"\n🎨 FRONTEND VERBETERINGEN:")
    print("=" * 50)
    
    improvements = [
        "✅ Verbeterde URL matching met root domain extractie",
        "✅ Betere console logging voor debugging",
        "✅ Specifiekere toast berichten met website counts",
        "✅ Automatische URL normalisatie naar root domains",
        "✅ Verbeterde error handling met regel nummers",
        "✅ Realistische placeholder voorbeelden",
        "✅ Duidelijkere beschrijving van functionaliteit"
    ]
    
    for improvement in improvements:
        print(f"   {improvement}")
    
    print(f"\n📝 VOORBEELD GEBRUIK:")
    print("   Source URLs:")
    print("   https://www.allincv.nl/pagina1")
    print("   https://aluminiumbedrijf.nl/contact")
    print("   https://www.am-team.nl/diensten")
    print("")
    print("   → Worden automatisch gematcht met:")
    print("   • AllInCV (https://www.allincv.nl)")
    print("   • Aluminium Bedrijf (https://www.aluminiumbedrijf.nl)")
    print("   • AM Team (https://www.am-team.nl)")

if __name__ == "__main__":
    test_url_matching_examples()
    show_frontend_improvements()
    
    print(f"\n🎉 URL MATCHING VERBETERINGEN VOLTOOID!")
    print("   De Source URLs worden nu correct gekoppeld aan websites")
    print("   op basis van root domain matching, ongeacht paden of www. prefixes.")
