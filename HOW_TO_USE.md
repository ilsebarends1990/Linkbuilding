# 📖 HOW TO USE - API WP Linkbuilding Dashboard

Deze handleiding is geschreven voor collega's zonder technische achtergrond om websites toe te voegen, te bewerken en de applicatie te deployen.

## 🎯 Wat doet deze applicatie?

Het API WP project is een **Linkbuilding Dashboard** bestaande uit:
- **Frontend**: Een moderne web interface (React) voor het beheren van links
- **Backend**: Een API server (Python) die communiceert met WordPress websites
- **Functionaliteiten**: Bulk import van links naar meerdere WordPress sites tegelijk

## 🏗️ Project Structuur

```
API WP/
├── frontend/          # Web interface (React + TypeScript)
├── backend/           # API server (Python + FastAPI)
├── config/           # Website configuraties (JSON bestanden)
└── HOW_TO_USE.md     # Deze handleiding
```

## 🌐 Vercel Projecten

Er zijn **2 projecten** in Vercel die samenwerken:

### 1. Frontend Project (`drijfveer-dashboard`)
- **Wat**: De web interface die gebruikers zien
- **URL**: `https://drijfveer-dashboard.vercel.app`
- **Functie**: Toont de dashboard interface, stuurt requests naar de backend

### 2. Backend Project (`api-wp-backend`) 
- **Wat**: De API server die de logica afhandelt
- **URL**: `https://api-wp-backend.vercel.app`
- **Functie**: Communiceert met WordPress sites, verwerkt link requests

**Hoe werken ze samen?**
- Gebruiker opent frontend → Frontend stuurt requests naar backend → Backend communiceert met WordPress → Resultaat terug naar frontend

## 📝 Websites Toevoegen/Bewerken

### Stap 1: Open de configuratie bestanden
Websites worden beheerd in JSON bestanden in de `config/` map:
- `websites_production.json` - Voor live/productie gebruik
- `websites_development.json` - Voor testen

### Stap 2: Website toevoegen
Voeg een nieuwe website toe aan het JSON bestand:

```json
{
  "website_url": "https://www.nieuwe-website.nl",
  "page_id": 123,
  "username": "admin",
  "app_password": "abcd efgh ijkl mnop qrst uvwx",
  "site_name": "Nieuwe Website"
}
```

**Vereiste informatie:**
- `website_url`: Volledige URL van de WordPress site
- `page_id`: ID van de pagina waar links toegevoegd moeten worden
- `username`: WordPress gebruikersnaam
- `app_password`: WordPress Application Password (niet het normale wachtwoord!)
- `site_name`: Vriendelijke naam voor in de interface

### Stap 3: Website bewerken
Zoek de website in het JSON bestand en pas de gewenste velden aan.

### Stap 4: Website verwijderen
Verwijder het hele JSON object van de website uit het bestand.

## 🚀 Deployment naar Vercel

### Voorbereiding
1. **Git installeren**: Download van https://git-scm.com/
2. **GitHub account**: Zorg dat je toegang hebt tot de repository
3. **Vercel account**: Toegang tot de Vercel projecten

### Stap 1: Wijzigingen lokaal maken
1. Open **Command Prompt** (CMD)
2. Navigeer naar de project map:
```cmd
cd "C:\Users\Drijfveer Media\Documents\API WP"
```

### Stap 2: Wijzigingen controleren
Bekijk welke bestanden je hebt aangepast:
```cmd
git status
```

### Stap 3: Wijzigingen toevoegen
Voeg alle gewijzigde bestanden toe:
```cmd
git add .
```

Of voeg specifieke bestanden toe:
```cmd
git add config/websites_production.json
```

### Stap 4: Wijzigingen committen
Maak een commit met een beschrijving:
```cmd
git commit -m "Website configuratie bijgewerkt: nieuwe site toegevoegd"
```

**Voorbeelden van goede commit berichten:**
- `"Nieuwe website toegevoegd: www.voorbeeld.nl"`
- `"Page ID bijgewerkt voor 3 websites"`
- `"Website verwijderd: oude-site.nl"`

### Stap 5: Wijzigingen naar GitHub pushen
Upload je wijzigingen naar GitHub:
```cmd
git push origin main
```

**Als je een error krijgt:**
```cmd
git pull origin main
git push origin main
```

### Stap 6: Automatische deployment
- **Frontend**: Vercel detecteert automatisch wijzigingen en deploy de frontend
- **Backend**: Vercel detecteert automatisch wijzigingen en deploy de backend
- **Wachttijd**: 2-5 minuten voor beide projecten

### Stap 7: Deployment controleren
1. Ga naar https://vercel.com/dashboard
2. Controleer beide projecten:
   - `drijfveer-dashboard` (frontend)
   - `api-wp-backend` (backend)
3. Kijk of de deployment succesvol is (groene vinkjes)

## 🔧 Troubleshooting

### "Git is not recognized"
Git is niet geïnstalleerd. Download van https://git-scm.com/

### "Permission denied"
Je hebt geen toegang tot de repository. Vraag toegang aan de beheerder.

### "Merge conflict"
Er zijn conflicterende wijzigingen:
```cmd
git pull origin main
# Los conflicten op in de bestanden
git add .
git commit -m "Merge conflicts opgelost"
git push origin main
```

### Deployment faalt
1. Controleer de Vercel dashboard voor error logs
2. Controleer of JSON bestanden valide zijn (geen syntax errors)
3. Test lokaal eerst met: `python backend/main.py`

### Website wordt niet gevonden
1. Controleer of `website_url` exact overeenkomt
2. Controleer of de WordPress site bereikbaar is
3. Controleer of Application Password correct is

## 📋 Checklist voor Website Toevoegen

- [ ] WordPress Application Password aangemaakt
- [ ] Page ID gevonden (via WordPress admin)
- [ ] Website toegevoegd aan juiste JSON bestand
- [ ] JSON syntax gecontroleerd (geen komma's vergeten)
- [ ] Git commit gemaakt met duidelijke beschrijving
- [ ] Wijzigingen gepusht naar GitHub
- [ ] Deployment gecontroleerd in Vercel
- [ ] Functionaliteit getest in de live applicatie

## 🆘 Hulp Nodig?

Bij problemen:
1. Controleer deze handleiding nogmaals
2. Kijk in de Vercel dashboard voor error logs
3. Test de applicatie lokaal
4. Vraag hulp aan de technische beheerder

---

💡 **Tip**: Maak altijd eerst een backup van configuratie bestanden voordat je grote wijzigingen maakt!
