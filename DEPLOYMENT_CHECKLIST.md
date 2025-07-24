# ✅ Vercel Deployment Checklist

## Wat is Automatisch Gedaan

### ✅ Project Herstructurering
- [x] Monorepo structuur gecreëerd (`frontend/` en `api/`)
- [x] Frontend bestanden verplaatst naar `frontend/`
- [x] Backend bestanden verplaatst naar `api/`
- [x] CSV configuratie geconverteerd naar JSON

### ✅ Frontend Configuratie
- [x] `.env.local` bestand aangemaakt met `VITE_API_URL`
- [x] `vercel.json` configuratie voor frontend
- [x] API service aangepast voor omgevingsvariabelen
- [x] Package.json scripts toegevoegd (`vercel-build`, `start`)

### ✅ Backend Herstructurering
- [x] FastAPI code omgezet naar serverless functie (`api/index.py`)
- [x] Config management utility (`api/utils/config.py`)
- [x] WordPress API utility (`api/utils/wordpress.py`)
- [x] Vercel configuratie voor API (`api/vercel.json`)
- [x] Requirements.txt geüpdatet met specifieke versies
- [x] CORS instellingen aangepast voor Vercel

### ✅ Data Management
- [x] JSON configuratie bestanden aangemaakt
- [x] Development/production config handling geïmplementeerd
- [x] Website configuraties geconverteerd naar JSON formaat

### ✅ Testing & Validatie
- [x] Setup test script aangemaakt (`test_setup.py`)
- [x] Alle tests succesvol uitgevoerd (4/4 passed)
- [x] Import validatie geslaagd
- [x] Configuratie bestanden gevalideerd

### ✅ Documentatie
- [x] Uitgebreide deployment guide (`VERCEL_DEPLOYMENT_GUIDE.md`)
- [x] README geüpdatet met deployment informatie
- [x] Deze checklist aangemaakt

## Wat JIJ Moet Doen

### 🔲 1. GitHub Repository Setup
```bash
# In de hoofdmap van het project:
git init
git add .
git commit -m "Initial commit - Vercel ready structure"

# Maak een nieuwe repository op GitHub en push:
git remote add origin https://github.com/jouw-username/api-wp.git
git push -u origin main
```

### 🔲 2. Frontend Deployment op Vercel
1. Ga naar [vercel.com](https://vercel.com) en log in
2. Klik "New Project" 
3. Selecteer je GitHub repository
4. **Belangrijke instellingen:**
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run vercel-build`
   - **Output Directory**: `dist`

5. **Environment Variables toevoegen:**
   ```
   VITE_API_URL = https://jouw-api-domain.vercel.app
   ```
   *(Je krijgt de API URL na stap 3)*

6. Deploy de frontend

### 🔲 3. Backend Deployment op Vercel  
1. Maak een **tweede** Vercel project voor de API
2. Selecteer dezelfde GitHub repository
3. **Belangrijke instellingen:**
   - **Framework Preset**: Other
   - **Root Directory**: `api`
   - **Build Command**: (laat leeg)
   - **Output Directory**: (laat leeg)

4. **Environment Variables toevoegen:**
   ```
   WEBSITES_CONFIG = [{"website_url": "https://www.allincv.nl", "page_id": 49, "username": "info@drijfveermedia.nl", "app_password": "XXEaNPwdaX4T7MblMyC7d5Q0", "site_name": "AllInCV Test"}, {"website_url": "https://website2.nl", "page_id": 25, "username": "admin@website2.nl", "app_password": "yyyy yyyy yyyy yyyy yyyy yyyy", "site_name": "Website 2"}, {"website_url": "https://website3.nl", "page_id": 30, "username": "info@website3.nl", "app_password": "zzzz zzzz zzzz zzzz zzzz zzzz", "site_name": "Website 3"}]
   ```

5. Deploy de API

### 🔲 4. URLs Koppelen
1. **Kopieer de API URL** uit stap 3 (bijv. `https://api-wp-api.vercel.app`)
2. **Update de frontend environment variable** in stap 2:
   - Ga naar je frontend project in Vercel
   - Settings → Environment Variables
   - Update `VITE_API_URL` met de API URL
   - Trigger een redeploy

### 🔲 5. CORS Configuratie Finaliseren
1. **Kopieer de frontend URL** uit stap 2 (bijv. `https://api-wp-frontend.vercel.app`)
2. **Update CORS in de API code:**
   - Bewerk `api/index.py` regel ~33
   - Vervang `"https://*.vercel.app"` met je specifieke frontend URL
   - Push wijziging naar GitHub (auto-redeploy)

### 🔲 6. Testing
1. **Frontend Test**: Ga naar je frontend URL
2. **API Health Check**: Ga naar `https://jouw-api-url.vercel.app/health`
3. **Integration Test**: Test het toevoegen van een link via de interface
4. **Bulk Import Test**: Test de bulk import functionaliteit

## Environment Variables Overzicht

### Frontend (Vercel Dashboard)
```
VITE_API_URL = https://jouw-api-domain.vercel.app
```

### Backend (Vercel Dashboard)  
```
WEBSITES_CONFIG = [JSON string met alle website configuraties]
```

## Verwachte URLs

Na deployment heb je twee URLs:
- **Frontend**: `https://api-wp-frontend.vercel.app` (of custom domain)
- **Backend**: `https://api-wp-api.vercel.app` (of custom domain)

## Support

Als je problemen ondervindt:
1. Controleer de Vercel function logs in het dashboard
2. Controleer browser console voor frontend errors  
3. Test de API endpoints direct in de browser
4. Raadpleeg `VERCEL_DEPLOYMENT_GUIDE.md` voor gedetailleerde troubleshooting

## 🎉 Success!

Na het voltooien van alle stappen heb je:
- Een volledig werkende WordPress Link Manager op Vercel
- Automatische deployments via GitHub
- Serverless backend met optimale performance
- Modern React frontend met alle functionaliteit intact
