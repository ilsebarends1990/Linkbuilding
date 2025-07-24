# Website Configuration

Dit project gebruikt nu JSON bestanden voor website configuraties in plaats van environment variables.

## Bestandsstructuur

- `websites_production.json` - Configuratie voor productie (Vercel)
- `websites_development.json` - Configuratie voor development (lokaal)

## Omgeving Detectie

Het systeem detecteert automatisch de omgeving:
- **Productie**: `VERCEL=1` of `NODE_ENV=production`
- **Development**: Alle andere gevallen

## Prioriteit Volgorde

1. **JSON bestanden** (hoogste prioriteit)
   - `config/websites_{environment}.json`
   - `websites_config.json` (legacy fallback)

2. **Environment Variables** (backward compatibility)
   - `WEBSITES_CONFIG` (JSON string)
   - `WEBSITES_CONFIG_BASE64` (base64 encoded JSON)

3. **CSV bestand** (laatste fallback)
   - `websites_config.csv`

## Voordelen van JSON Configuratie

- ✅ Geen grootte limitaties (Vercel env vars zijn beperkt tot 4KB)
- ✅ Makkelijker onderhoud en bewerking
- ✅ Versiebeheer mogelijk via Git
- ✅ Geen base64 encoding nodig
- ✅ Betere performance
- ✅ Lokale development en productie gebruiken dezelfde bron

## Migratie van Environment Variables

De environment variables kunnen nu weggehaald worden uit Vercel. Het systeem gebruikt automatisch de JSON bestanden.

## Backup

Bij elke save operatie wordt ook een CSV backup gemaakt voor compatibiliteit.
