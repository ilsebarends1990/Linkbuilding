import { Website } from '@/services/api';

/**
 * Extraheert de root domain van een URL (zonder www, subdomeinen, paden, etc.)
 */
function extractRootDomain(url: string): string | null {
  try {
    const urlObj = new URL(url);
    let hostname = urlObj.hostname.toLowerCase();
    
    // Verwijder www. prefix
    hostname = hostname.replace(/^www\./, '');
    
    // Voor eenvoudige matching gebruiken we de volledige hostname
    // In de toekomst kunnen we hier meer geavanceerde domain extractie toevoegen
    return hostname;
  } catch {
    return null;
  }
}

/**
 * Detecteert automatisch de juiste website configuratie op basis van een URL
 * Gebruikt root domain matching voor betere koppeling tussen Source URLs en website configuraties
 */
export function detectWebsiteFromUrl(url: string, websites: Website[]): Website | null {
  if (!url || websites.length === 0) return null;

  const inputRootDomain = extractRootDomain(url);
  if (!inputRootDomain) return null;

  // Zoek naar exacte root domain match
  const match = websites.find(site => {
    const siteRootDomain = extractRootDomain(site.website_url);
    return siteRootDomain === inputRootDomain;
  });

  return match || null;
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
 * Normaliseert een URL naar de root domain voor consistente matching
 * Bijvoorbeeld: https://www.example.com/page/123 -> https://example.com
 */
export function normalizeToRootDomain(url: string): string {
  if (!url) return url;
  
  try {
    const urlObj = new URL(normalizeUrl(url));
    let hostname = urlObj.hostname.toLowerCase();
    
    // Verwijder www. prefix
    hostname = hostname.replace(/^www\./, '');
    
    // Retourneer alleen protocol + hostname (root domain)
    return `${urlObj.protocol}//${hostname}`;
  } catch {
    return url; // Retourneer originele URL als parsing faalt
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
