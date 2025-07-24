# Drijfveer Media Dashboard

Een moderne full-screen webapplicatie voor het beheren van WordPress websites, links en blog posts.

## 🚀 Features

### 📊 Dashboard Layout
- **Permanente sidebar** met navigatie
- **Responsive design** met Tailwind CSS
- **Modern UI** met shadcn/ui componenten
- **Dark mode** ondersteuning (toekomstig)

### 🔗 Link Manager
- **Enkele links** toevoegen aan WordPress websites
- **Bulk import** functionaliteit voor meerdere links tegelijk
- **Automatische website detectie** op basis van source URLs
- **Real-time parsing** van import data
- **Batch processing** met voortgangsindicatie

### 📝 Blog Manager
- **WYSIWYG editor** voor blog posts (toekomstig: TipTap)
- **Concept en publiceer** workflow
- **SEO-vriendelijke** slug generatie
- **Categorieën en tags** beheer
- **Excerpt** ondersteuning
- **Blog overzicht** met filtering

### 🌐 Website Manager
- **CRUD operaties** voor WordPress websites
- **Veilige opslag** van credentials
- **Bulk configuratie** mogelijkheden
- **Website status** monitoring

## 🛠️ Tech Stack

### Frontend
- **React 18** met TypeScript
- **Vite** voor snelle development
- **Tailwind CSS** voor styling
- **shadcn/ui** voor UI componenten
- **TanStack Query** voor state management
- **React Router v6** voor navigatie
- **Lucide React** voor iconen

### Backend
- **FastAPI** (Python)
- **WordPress REST API** integratie
- **CSV-based** configuratie opslag
- **Pydantic** voor data validatie

## 📁 Project Structuur

```
drijfveer-dashboard/
├── src/
│   ├── components/          # Herbruikbare UI componenten
│   │   └── ui/             # shadcn/ui basis componenten
│   ├── layouts/            # Layout componenten
│   │   └── SidebarLayout.tsx
│   ├── modules/            # Feature modules
│   │   ├── linkmanager/    # Link management
│   │   ├── blogmanager/    # Blog management
│   │   └── websites/       # Website management
│   ├── hooks/              # Custom React hooks
│   ├── services/           # API services
│   ├── lib/                # Utilities
│   └── utils/              # Helper functies
├── public/                 # Statische bestanden
└── backend/                # FastAPI backend (gedeeld)
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.8+
- npm of yarn

### Frontend Setup
```bash
cd drijfveer-dashboard
npm install
npm run dev
```

### Backend Setup
```bash
cd ../backend
pip install -r requirements.txt
python main.py
```

## 🔧 Development

### Available Scripts
- `npm run dev` - Start development server
- `npm run build` - Build voor productie
- `npm run lint` - Run ESLint
- `npm run preview` - Preview productie build

### API Endpoints
- `GET /websites` - Haal websites op
- `POST /add-link` - Voeg enkele link toe
- `POST /add-bulk-links` - Voeg bulk links toe
- `GET /blogs` - Haal blog posts op
- `POST /blogs` - Maak nieuwe blog post
- `PUT /blogs/{id}` - Update blog post
- `DELETE /blogs/{id}` - Verwijder blog post

## 📋 Roadmap

### Sprint 1 ✅
- [x] Project setup en basis structuur
- [x] Sidebar layout implementatie
- [x] LinkManager module (basis functionaliteit)
- [x] Website Manager module
- [x] Blog Manager module (basis)

### Sprint 2 🚧
- [ ] TipTap WYSIWYG editor integratie
- [ ] WordPress API integratie voor blogs
- [ ] Verbeterde error handling
- [ ] Loading states en skeletons

### Sprint 3 📅
- [ ] User authenticatie
- [ ] Role-based access control
- [ ] Dark mode implementatie
- [ ] Responsive optimalisaties

### Sprint 4 📅
- [ ] Database integratie (PostgreSQL)
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Production deployment

## 🔐 Security

- **App passwords** voor WordPress authenticatie
- **Environment variabelen** voor gevoelige data
- **CORS** configuratie voor veilige API toegang
- **Input validatie** op frontend en backend

## 🤝 Contributing

1. Fork het project
2. Maak een feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit je changes (`git commit -m 'Add some AmazingFeature'`)
4. Push naar de branch (`git push origin feature/AmazingFeature`)
5. Open een Pull Request

## 📝 License

Dit project is gelicenseerd onder de MIT License.

## 📞 Contact

Drijfveer Media - [contact@drijfveermedia.nl](mailto:contact@drijfveermedia.nl)

Project Link: [https://github.com/drijfveermedia/dashboard](https://github.com/drijfveermedia/dashboard)
