# 🚀 GitHub Setup Instructies

## Stap 1: GitHub Repository Aanmaken

1. Ga naar [github.com](https://github.com) en log in
2. Klik op de "+" knop rechtsboven en selecteer "New repository"
3. Vul in:
   - **Repository name**: `api-wp` (of een andere naam naar keuze)
   - **Description**: `WordPress Link Manager - Vercel Ready`
   - **Visibility**: Private of Public (naar keuze)
   - **NIET** aanvinken: "Add a README file", "Add .gitignore", "Choose a license"

4. Klik "Create repository"

## Stap 2: Repository Koppelen en Pushen

Kopieer en plak deze commando's één voor één in je terminal:

```bash
# Voeg de GitHub repository toe als remote origin
git remote add origin https://github.com/JOUW-USERNAME/api-wp.git

# Push de code naar GitHub
git push -u origin master
```

**Vervang `JOUW-USERNAME` met je echte GitHub username!**

## Stap 3: Verificatie

Na het pushen kun je:
1. Je repository bekijken op GitHub
2. Controleren of alle bestanden zijn geüpload
3. De README.md en documentatie bekijken

## Volgende Stappen

Na succesvolle GitHub push:
1. Ga naar [vercel.com](https://vercel.com) voor deployment
2. Volg de stappen in `DEPLOYMENT_CHECKLIST.md`
3. Deploy eerst de frontend, dan de API

## Repository Structuur

Je repository bevat nu:
```
api-wp/
├── frontend/              # React frontend (voor Vercel)
├── api/                   # FastAPI backend (voor Vercel)
├── drijfveer-dashboard/   # Originele frontend (backup)
├── backend/               # Originele backend (backup)
├── DEPLOYMENT_CHECKLIST.md
├── VERCEL_DEPLOYMENT_GUIDE.md
└── ...
```

## Troubleshooting

Als je een foutmelding krijgt:
- Controleer of je GitHub username correct is
- Zorg dat je ingelogd bent op GitHub
- Probeer HTTPS in plaats van SSH als je problemen hebt met authenticatie
