import { Website } from '@/services/api';

/**
 * Detecteert automatisch de juiste website configuratie op basis van een URL
 */
export function detectWebsiteFromUrl(url: string, websites: Website[]): Website | null {
  if (!url || websites.length === 0) return null;

  try {
    const urlObj = new URL(url);
    const hostname = urlObj.hostname.toLowerCase();

    // Zoek naar exacte hostname match
    const exactMatch = websites.find(site => {
      try {
        const siteUrl = new URL(site.website_url);
        return siteUrl.hostname.toLowerCase() === hostname;
      } catch {
        return false;
      }
    });

    if (exactMatch) return exactMatch;

    // Zoek naar subdomain match (bijv. www.example.com matcht met example.com)
    const domainMatch = websites.find(site => {
      try {
        const siteUrl = new URL(site.website_url);
        const siteHostname = siteUrl.hostname.toLowerCase();
        
        // Verwijder www. prefix voor vergelijking
        const cleanHostname = hostname.replace(/^www\./, '');
        const cleanSiteHostname = siteHostname.replace(/^www\./, '');
        
        return cleanHostname === cleanSiteHostname;
      } catch {
        return false;
      }
    });

    return domainMatch || null;
  } catch {
    return null;
  }
}

/**
 * Detecteert automatisch de pagina ID op basis van URL patronen
 */
export function detectPageIdFromUrl(url: string): string | null {
  if (!url) return null;

  try {
    const urlObj = new URL(url);
    const pathname = urlObj.pathname;

    // Zoek naar pagina ID in verschillende URL patronen
    const patterns = [
      /\/page\/(\d+)/,           // /page/123
      /\/p\/(\d+)/,              // /p/123
      /\/(\d+)\/$/,              // /123/
      /page_id=(\d+)/,           // ?page_id=123
      /p=(\d+)/,                 // ?p=123
      /\/linkpartners\/?$/,      // Specifiek voor linkpartners pagina's (standaard ID 49)
    ];

    for (const pattern of patterns) {
      const match = pathname.match(pattern) || url.match(pattern);
      if (match && match[1]) {
        return match[1];
      }
    }

    // Specifieke pagina detectie voor bekende URL patronen
    if (pathname.includes('linkpartners') || pathname.includes('partners')) {
      return '49'; // Standaard linkpartners pagina ID
    }

    return null;
  } catch {
    return null;
  }
}

/**
 * Valideert of een URL geldig is
 */
export function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * Normaliseert een URL door protocol toe te voegen indien ontbrekend
 */
export function normalizeUrl(url: string): string {
  if (!url) return url;
  
  // Voeg https:// toe als er geen protocol is
  if (!/^https?:\/\//i.test(url)) {
    return `https://${url}`;
  }
  
  return url;
}
