import { Outlet, useLocation, Link } from 'react-router-dom'
import { Link as LinkIcon, FileText, Globe, Settings } from 'lucide-react'
import { Toaster } from '@/components/ui/toaster'
import ConfigInfo from '@/components/ConfigInfo'

const navigation = [
  {
    name: 'Link Manager',
    href: '/links',
    icon: LinkIcon,
  },
  {
    name: 'Blog Manager',
    href: '/blogs',
    icon: FileText,
  },
  {
    name: 'Websites',
    href: '/websites',
    icon: Globe,
  },
]

export default function SidebarLayout() {
  const location = useLocation()

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 text-white flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b border-slate-700">
          <h1 className="text-xl font-bold text-white">
            Drijfveer Media
          </h1>
          <p className="text-sm text-slate-300 mt-1">
            Linkbuilding Dashboard
          </p>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-2">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            const Icon = item.icon
            
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors
                  ${isActive 
                    ? 'bg-blue-600 text-white' 
                    : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                  }
                `}
              >
                <Icon className="mr-3 h-5 w-5" />
                {item.name}
              </Link>
            )
          })}
        </nav>

        {/* Configuration Info */}
        <div className="px-4 py-2">
          <ConfigInfo />
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-700">
          <div className="flex items-center text-sm text-slate-400">
            <Settings className="mr-2 h-4 w-4" />
            Dashboard v1.0
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto bg-slate-50">
        <div className="p-6">
          <Outlet />
        </div>
      </main>
      <Toaster />
    </div>
  )
}
