# Stappenplan – Drijfveer Media Dashboard

> **Doel**  
> Een full‑screen webapplicatie met een permanente linker‑sidebar (“Drijfveer Media Linkbuilding”) en drie hoofdmodules: **LinkManager**, **BlogManager** en **Websites**.  
> Stack: React 18 + TypeScript + Vite, Tailwind CSS, shadcn/ui, TanStack Query, FastAPI‑backend.

---

## 1 – Project‑basis

| Stap | Actie | Output |
|------|-------|--------|
| 1.1 | Initialiseer nieuwe Git‑monorepo (`/frontend`, `/backend`). | Branch `dashboard` |
| 1.2 | **Frontend**: `npm create vite@latest drijfveer-dashboard -- --template react-ts`. | Vite‑project |
| 1.3 | Installeer UI‑stack: `tailwindcss`, `lucide-react`, `@tanstack/react-query`, `@shadcn/ui`, `@tiptap/react` (voor Blog‑editor). | `package.json` deps |
| 1.4 | **Backend** blijft bestaande FastAPI, uitbreiden met blog‑routes (zie §5). | `backend/` |
| 1.5 | Configureer CI (GitHub Actions) voor lint + test + preview‑deploy (Vercel/Render). | Workflow file |

---

## 2 – Layout & routing

1. Maak `SidebarLayout.tsx`  
   ```tsx
   <div className="flex h-screen">
     <aside className="w-64 bg-slate-900 text-white flex flex-col">
       {/* Logo + nav */}
     </aside>
     <main className="flex-1 overflow-y-auto bg-slate-50 p-6">
       <Outlet />
     </main>
   </div>
   ```
2. Voeg React Router v6 routes:
   ```tsx
   <Route element={<SidebarLayout />}>  
     <Route path="/links" element={<LinkManager />} />  
     <Route path="/blogs" element={<BlogManager />} />  
     <Route path="/websites" element={<Websites />} />  
     <Route index element={<Navigate to="/links" replace />} />  
   </Route>
   ```
3. Sidebar‑component: list‐items met Lucide‑icons; active state via `useLocation()`.

---

## 3 – LinkManager‑module

* **Hergebruik** bestaande componenten (`WordPressLinkManagerNew`, bulk‑import UI).  
* Verplaats naar `/modules/linkmanager/` en pas styling aan brede layout.  
* Voeg tabel‐view toe met reeds geplaatste links per site (GET `/links?site_id=`).

---

## 4 – BlogManager‑module

| Element | Beschrijving |
|---------|--------------|
| **Toolbar** | Buttons voor *Opslaan concept*, *Publiceer*, *Preview* |
| **Velden** | Titel, Slug (auto‐generate), Excerpt (textarea), Categorie‑select, Tags (multiselect), Featured Image (drag‑drop upload) |
| **Editor** | WYSIWYG (TipTap) met heading, bold, lists, link‑dialog, code‑block. |
| **SEO‑snippet** | Live preview: title‑tag + meta‑description. |
| **Validation** | Client‑side Zod + server errors. |

### 4.1 API Endpoints (FastAPI)

| Method | Path | Body | Doel |
|--------|------|------|------|
| `GET` | `/blogs` | – | Lijst posts (paged) |
| `POST` | `/blogs` | `BlogCreate` | Nieuwe post (status "draft" of "publish") |
| `PUT` | `/blogs/{id}` | `BlogUpdate` | Bijwerken |
| `DELETE` | `/blogs/{id}` | – | Verwijderen |
| `POST` | `/blogs/{id}/media` | multipart | Upload featured image |

Adapter in `wordpress_client.py` gebruikt WordPress REST `/wp/v2/posts` e.d.

---

## 5 – Websites‑module

* Bestaand CRUD‑scherm hergebruiken, maar lijst in **DataTable** met zoek‐ en sorteer‑opties.  
* Extra kolom: "Actieve links", "Actieve blogs" (counts via query joins).

---

## 6 – State & data‑fetching

1. Zet `QueryClient` met global error boundary prompt.  
2. Maak `useApi()` wrapper à la huidige project; voeg auth‑header.  
3. Gebruik *optimistic updates* voor snelle UI.

---

## 7 – Styling & UX‑details

* **Dark‑mode toggle** (Tailwind `dark:`).  
* Animaties met Framer Motion op route‑transitions.  
* WCAG‑labeling + focus‑ringen.  
* Skeleton loaders voor tabel‐ en editor‑laadproces.

---

## 8 – Veiligheid & rechten

* Integratie OAuth2 token (JWT stored in `httpOnly` cookie).  
* Rollen: `admin`, `editor`, `viewer`.  
* Guards in router.

---

## 9 – Testen

| Type | Tool | Scope |
|------|------|-------|
| Unit | Vitest + React Testing Library | UI‑componenten |
| E2E | Playwright (headed) | Volledige flows (create blog, publish) |
| API | Pytest + httpx | CRUD‑routes |

---

## 10 – Deploy

* **Docker Compose**: `frontend` (Nginx), `backend`, `postgres` (ipv CSV).  
* Staging omgeving via Render.com; main branch auto‑deploy.

---

## 11 – Migratie‑stappen (bestaande links‑tool)

1. Refactor link‑code naar shared package.  
2. Verplaats oude UI naar nieuwe `LinkManager` route.  
3. Redirect oude URLs.

---

## 12 – Roadmap & mijlpalen

| Sprint | Deliverable |
|--------|-------------|
| 0 | Setup repo, CI, Sidebar‑layout |
| 1 | LinkManager klaar in nieuwe layout |
| 2 | BlogManager MVP (titel + editor + publish) |
| 3 | Websites‑module refactor + counts |
| 4 | Auth & RBAC + SEO‑snippet |
| 5 | Deploy staging, QA, go‑live |

_Einde document_

