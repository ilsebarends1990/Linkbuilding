# API WP Project Analyse

## Overzicht
Het API WP project is een WordPress Link Management systeem dat bestaat uit een FastAPI backend en een React frontend. Het systeem is ontworpen om links bulk-gewijs toe te voegen aan meerdere WordPress websites via de WordPress REST API.

## Projectstructuur

```
API WP/
├── backend/                    # FastAPI backend server
│   ├── main.py                # Hoofdapplicatie met API endpoints
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variabelen
├── link-wizard-wp/            # React frontend applicatie
│   ├── src/
│   │   ├── components/        # React componenten
│   │   ├── hooks/            # Custom React hooks
│   │   ├── services/         # API service laag
│   │   └── pages/            # React pagina's
│   └── package.json          # Node.js dependencies
├── bulk_links_manager.py      # Standalone bulk links script
├── websites_config.csv        # Website configuratie bestand
└── testapitest.py            # Test script
```

## Backend (FastAPI)

### Hoofdbestand: `backend/main.py`

**Functionaliteit:**
- FastAPI applicatie voor WordPress link management
- CORS middleware voor frontend communicatie
- HTTP Bearer authenticatie (momenteel niet actief gebruikt)
- CSV-gebaseerde website configuratie opslag

**Belangrijkste API Endpoints:**

1. **GET /** - Root endpoint
2. **GET /websites** - Haal beschikbare websites op
3. **POST /add-link** - Voeg enkele link toe
4. **POST /add-bulk-links** - Voeg bulk links toe aan meerdere websites
5. **POST /websites** - Voeg nieuwe website configuratie toe
6. **PUT /websites** - Update bestaande website configuratie
7. **DELETE /websites/{website_url}** - Verwijder website configuratie
8. **GET /health** - Health check endpoint

**Pydantic Models:**
- `WebsiteConfig`: Website configuratie structuur
- `LinkRequest`: Enkele link request
- `BulkLinkRequest`: Bulk link request
- `WebsiteRequest`: Nieuwe website request
- `UpdateWebsiteRequest`: Website update request
- Response models voor API responses

**Kernfuncties:**

1. **`load_websites_config()`**: Laadt website configuraties uit CSV
2. **`save_websites_config()`**: Slaat configuraties op naar CSV
3. **`add_link_to_wordpress()`**: Voegt link toe aan WordPress pagina via REST API
4. **Website management functies**: CRUD operaties voor website configuraties

**WordPress Integratie:**
- Gebruikt WordPress REST API (`/wp-json/wp/v2/pages/{page_id}`)
- HTTP Basic Auth met app passwords
- Voegt links toe door pagina content te updaten

### Dependencies (`requirements.txt`)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
requests==2.31.0
python-multipart==0.0.6
pydantic==2.5.0
python-dotenv==1.0.0
```

## Frontend (React + TypeScript)

### Technologie Stack
- **React 18** met TypeScript
- **Vite** als build tool
- **TanStack Query** voor API state management
- **Shadcn/ui** voor UI componenten
- **Tailwind CSS** voor styling
- **React Router** voor navigatie

### Hoofdcomponenten

#### 1. `WordPressLinkManagerNew.tsx`
**Hoofdcomponent van de applicatie**

**Functionaliteit:**
- Tabbed interface met drie modi:
  - **Enkele Link**: Voeg één link toe aan geselecteerde website
  - **Bulk Import**: Import meerdere links uit gestructureerde tekst
  - **Website Beheer**: Beheer website configuraties

**Bulk Import Functionaliteit:**
- Parseert drie kolommen tekst (Source URLs, Anchor Texts, Target URLs)
- Automatische website detectie op basis van source URL
- Batch processing met voortgangsindicatie
- Regel-voor-regel validatie en foutafhandeling

**Key Features:**
- Real-time parsing van import data
- Automatische website matching
- Batch size selectie
- Voortgangstracking tijdens bulk operaties

#### 2. `WebsiteManager.tsx`
**Website configuratie beheer**

**Functionaliteit:**
- CRUD operaties voor website configuraties
- Inline editing van website gegevens
- Form validatie
- Toast notificaties voor feedback

**Form Fields:**
- Website URL
- Site naam
- Page ID (standaard: 49)
- Username
- App Password

#### 3. Custom Hooks

**`useWebsiteApi.ts`:**
- `useAddWebsite()`: Voeg nieuwe website toe
- `useUpdateWebsite()`: Update bestaande website
- `useDeleteWebsite()`: Verwijder website

**`useApi.ts`** (niet getoond maar gerefereerd):
- `useWebsites()`: Haal websites op
- `useAddLink()`: Voeg enkele link toe
- `useAddBulkLinks()`: Voeg bulk links toe
- `useHealthCheck()`: Health check

#### 4. API Service (`services/api.ts`)

**API Client configuratie:**
- Base URL: `http://localhost:8000`
- TypeScript interfaces voor alle API requests/responses
- Centralized error handling met `ApiError` class
- Fetch wrapper met JSON handling

**API Methods:**
- `getWebsites()`: Haal websites lijst op
- `addLink()`: Voeg enkele link toe
- `addBulkLinks()`: Voeg bulk links toe
- `addWebsite()`: Voeg website configuratie toe
- `updateWebsite()`: Update website configuratie
- `deleteWebsite()`: Verwijder website configuratie
- `healthCheck()`: Server status check

## Standalone Scripts

### `bulk_links_manager.py`
**Professionele bulk links manager voor command-line gebruik**

**Functionaliteit:**
- CSV-gebaseerde website configuratie
- Concurrent processing met ThreadPoolExecutor
- Uitgebreide logging naar bestand en console
- Retry mechanisme voor gefaalde requests
- Progress tracking en statistieken

**Key Features:**
- Multi-threading voor snelle verwerking
- Robuuste error handling
- Gedetailleerde logging
- Configureerbare retry logic

### `testapitest.py`
Test script voor API functionaliteit (inhoud niet geanalyseerd)

## Configuratie

### `websites_config.csv`
**Website configuratie opslag**

**Format:**
```csv
website_url,page_id,username,app_password,site_name
https://www.allincv.nl,49,info@drijfveermedia.nl,XXEaNPwdaX4T7MblMyC7d5Q0,AllInCV Test
```

**Velden:**
- `website_url`: WordPress website URL
- `page_id`: WordPress pagina ID waar links toegevoegd worden
- `username`: WordPress gebruikersnaam
- `app_password`: WordPress applicatie wachtwoord
- `site_name`: Vriendelijke naam voor de website

## Workflow

### Typische Gebruiksscenario's

1. **Bulk Import Workflow:**
   - Gebruiker ontvangt email met link updates in tabelvorm
   - Kopieert data naar drie tekstgebieden (Source URLs, Anchor Texts, Target URLs)
   - Systeem parseert en matcht automatisch websites
   - Batch verwerking met voortgangsindicatie
   - Resultaten worden getoond per link

2. **Website Beheer:**
   - Voeg nieuwe WordPress websites toe
   - Configureer authenticatie (username/app_password)
   - Stel standaard page ID in
   - Beheer bestaande configuraties

3. **Enkele Link Toevoeging:**
   - Selecteer website uit dropdown
   - Voer anchor text en target URL in
   - Voeg link toe aan gespecificeerde pagina

## Technische Details

### WordPress Integratie
- **API Endpoint**: `/wp-json/wp/v2/pages/{page_id}`
- **Authenticatie**: HTTP Basic Auth met app passwords
- **Methode**: PUT request om pagina content bij te werken
- **Content Update**: Voegt link toe aan bestaande pagina content

### Error Handling
- Uitgebreide error logging in backend
- Toast notificaties in frontend
- Retry mechanisme voor gefaalde requests
- Validatie op zowel frontend als backend

### Security
- App passwords voor WordPress authenticatie
- CORS configuratie voor frontend toegang
- Environment variabelen voor gevoelige data

## Uitbreidingsmogelijkheden

1. **Database Integratie**: Vervang CSV opslag door database
2. **User Authentication**: Implementeer gebruikersauthenticatie
3. **Link Analytics**: Track link performance
4. **Bulk Operations**: Uitgebreide bulk operaties
5. **Website Templates**: Voorgedefinieerde website configuraties
6. **API Rate Limiting**: Implementeer rate limiting voor WordPress API calls

## Deployment Overwegingen

1. **Backend**: FastAPI server op poort 8000
2. **Frontend**: Vite development server op poort 5173
3. **CORS**: Geconfigureerd voor lokale development
4. **Environment**: Lokale development setup
5. **Dependencies**: Python backend, Node.js frontend

## Conclusie

Het API WP project is een goed gestructureerd WordPress link management systeem met een moderne tech stack. Het biedt zowel een gebruiksvriendelijke web interface als command-line tools voor bulk operaties. De architectuur is schaalbaar en kan eenvoudig uitgebreid worden met extra functionaliteit.

De bulk import functionaliteit is specifiek ontworpen voor de gebruikscase waarbij link updates via email ontvangen worden in tabelvorm, wat het workflow aanzienlijk stroomlijnt ten opzichte van handmatige invoer.
