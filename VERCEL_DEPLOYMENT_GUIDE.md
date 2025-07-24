# Vercel Deployment Guide - API WP Project

## Project Structuur

Het project is nu hergestructureerd voor Vercel deployment:

```
API WP/
├── frontend/          # React/TypeScript frontend
│   ├── src/
│   ├── .env.local     # Environment variables
│   ├── vercel.json    # Vercel config voor frontend
│   └── package.json
├── api/               # FastAPI backend (serverless)
│   ├── index.py       # Main API handler
│   ├── utils/         # Utility modules
│   │   ├── config.py  # Configuration management
│   │   └── wordpress.py # WordPress API functions
│   ├── data/          # Local development data
│   │   └── websites_config.json
│   ├── vercel.json    # Vercel config voor API
│   └── requirements.txt
└── websites_config.json # Generated from CSV
```

## Stappen voor Deployment

### 1. GitHub Repository Setup

```bash
# Initialiseer Git repository
git init
git add .
git commit -m "Initial commit - Vercel ready structure"

# Push naar GitHub
git remote add origin https://github.com/jouw-username/api-wp.git
git push -u origin main
```

### 2. Frontend Deployment (Vercel)

1. Ga naar [vercel.com](https://vercel.com) en log in
2. Klik "New Project"
3. Selecteer je GitHub repository
4. Configureer project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

5. Voeg Environment Variables toe:
   ```
   VITE_API_URL = https://jouw-api-domain.vercel.app
   ```

6. Deploy de frontend

### 3. Backend Deployment (Vercel)

1. Maak een nieuw Vercel project voor de API
2. Configureer project:
   - **Framework Preset**: Other
   - **Root Directory**: `api`
   - **Build Command**: (laat leeg)
   - **Output Directory**: (laat leeg)

3. Voeg Environment Variables toe:
   ```
   WEBSITES_CONFIG = [{"website_url": "https://www.allincv.nl", "page_id": 49, "username": "info@drijfveermedia.nl", "app_password": "XXEaNPwdaX4T7MblMyC7d5Q0", "site_name": "AllInCV Test"}, {"website_url": "https://website2.nl", "page_id": 25, "username": "admin@website2.nl", "app_password": "yyyy yyyy yyyy yyyy yyyy yyyy", "site_name": "Website 2"}, {"website_url": "https://website3.nl", "page_id": 30, "username": "info@website3.nl", "app_password": "zzzz zzzz zzzz zzzz zzzz zzzz", "site_name": "Website 3"}]
   ```

4. Deploy de API

### 4. CORS Configuratie Update

Na deployment, update de CORS origins in `api/index.py`:

```python
allow_origins=[
    "https://jouw-frontend-domain.vercel.app",  # Je frontend URL
    "http://localhost:5173",  # Development
],
```

Redeploy de API na deze wijziging.

## Environment Variables

### Frontend (.env.local)
```
VITE_API_URL=https://jouw-api-domain.vercel.app
```

### Backend (Vercel Dashboard)
```
WEBSITES_CONFIG=[JSON string met website configuraties]
```

## Testing na Deployment

1. **Frontend Test**: Ga naar je frontend URL en controleer of de interface laadt
2. **API Test**: Ga naar `https://jouw-api-domain.vercel.app/health` 
3. **Integration Test**: Test het toevoegen van een link via de frontend

## Belangrijke Opmerkingen

### Limitaties in Production

1. **Website Configuratie**: In productie kunnen nieuwe websites alleen worden toegevoegd door de `WEBSITES_CONFIG` environment variable bij te werken in Vercel
2. **Cold Starts**: Serverless functions hebben cold starts - eerste requests kunnen traag zijn
3. **Timeout Limits**: Vercel heeft een 30-seconden timeout voor serverless functions

### Bulk Processing

De bulk processing is aangepast voor serverless:
- Client-side batching voor grote sets
- Kleinere batch groottes (max 10 links per request)
- Timeout handling

### Development vs Production

- **Development**: Gebruikt lokale JSON bestanden voor configuratie
- **Production**: Gebruikt Vercel environment variables

## Troubleshooting

### Common Issues

1. **CORS Errors**: Controleer of de frontend URL is toegevoegd aan CORS origins
2. **Config Not Loading**: Controleer of `WEBSITES_CONFIG` environment variable correct is ingesteld
3. **API Timeout**: Verklein batch groottes voor bulk operations

### Logs

- **Frontend**: Browser Developer Tools Console
- **Backend**: Vercel Functions tab in dashboard

## Monitoring

- **Vercel Analytics**: Automatisch beschikbaar voor beide deployments
- **Function Logs**: Beschikbaar in Vercel dashboard
- **Error Tracking**: Ingebouwd in Vercel platform

## Updates

Voor updates aan de applicatie:
1. Push wijzigingen naar GitHub
2. Vercel zal automatisch rebuilden en deployen
3. Voor environment variable wijzigingen: update in Vercel dashboard en trigger redeploy
