import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import SidebarLayout from './layouts/SidebarLayout'
import LinkManager from './modules/linkmanager/LinkManager'
import BlogManager from './modules/blogmanager/BlogManager'
import WebsiteManager from './modules/websites/WebsiteManager'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<SidebarLayout />}>
            <Route path="/links" element={<LinkManager />} />
            <Route path="/blogs" element={<BlogManager />} />
            <Route path="/websites" element={<WebsiteManager />} />
            <Route index element={<Navigate to="/links" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
