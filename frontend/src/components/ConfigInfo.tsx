import { useQuery } from '@tanstack/react-query'
import { api } from '@/services/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { CheckCircle, XCircle, Server, FileText, Clock, AlertTriangle } from 'lucide-react'
import { useState } from 'react'

export default function ConfigInfo() {
  const [showMissingIds, setShowMissingIds] = useState(false);
  const { data: configInfo, isLoading, error } = useQuery({
    queryKey: ['config-info'],
    queryFn: api.getConfigInfo,
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  if (isLoading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center text-sm">
            <Server className="mr-2 h-4 w-4" />
            Configuration Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-muted-foreground">Loading...</div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center text-sm text-red-600">
            <XCircle className="mr-2 h-4 w-4" />
            Configuration Error
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-red-600">Failed to load config info</div>
        </CardContent>
      </Card>
    )
  }

  if (!configInfo) return null

  const getSourceBadge = (source: string) => {
    switch (source) {
      case 'environment_variables':
        return <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">Environment Variables</span>
      case 'csv_file':
        return <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">CSV File</span>
      case 'not_found':
        return <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">Not Found</span>
      case 'error':
        return <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">Error</span>
      default:
        return <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">{source}</span>
    }
  }

  const formatDateTime = (isoString: string) => {
    try {
      return new Date(isoString).toLocaleString('nl-NL', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    } catch {
      return isoString
    }
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center text-sm">
          <Server className="mr-2 h-4 w-4" />
          Configuration Status
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Source:</span>
          {getSourceBadge(configInfo.config_source)}
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Websites:</span>
          <span className="text-sm font-mono">{configInfo.total_websites}</span>
        </div>

        {configInfo.missing_page_ids > 0 && (
          <div className="flex flex-col space-y-2 bg-amber-50 p-2 rounded-md border border-amber-200">
            <div 
              className="flex items-center justify-between cursor-pointer" 
              onClick={() => setShowMissingIds(!showMissingIds)}
            >
              <span className="text-sm font-medium flex items-center text-amber-700">
                <AlertTriangle className="mr-1 h-4 w-4 text-amber-500" />
                Missing Page IDs:
              </span>
              <span className="text-sm font-mono text-amber-700">{configInfo.missing_page_ids}</span>
            </div>
            
            {showMissingIds && configInfo.websites_with_missing_ids && (
              <div className="text-xs text-amber-700 bg-amber-100 p-2 rounded max-h-32 overflow-y-auto">
                <ul className="list-disc pl-4 space-y-1">
                  {configInfo.websites_with_missing_ids.map((url, index) => (
                    <li key={index}>{url}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground flex items-center">
              <Server className="mr-1 h-3 w-3" />
              Environment JSON
            </span>
            {configInfo.environment_available ? (
              <CheckCircle className="h-4 w-4 text-green-500" />
            ) : (
              <XCircle className="h-4 w-4 text-red-500" />
            )}
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground flex items-center">
              <Server className="mr-1 h-3 w-3" />
              Environment Base64
            </span>
            {configInfo.environment_base64_available ? (
              <CheckCircle className="h-4 w-4 text-green-500" />
            ) : (
              <XCircle className="h-4 w-4 text-red-500" />
            )}
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground flex items-center">
              <FileText className="mr-1 h-3 w-3" />
              CSV File
            </span>
            {configInfo.csv_file_available ? (
              <CheckCircle className="h-4 w-4 text-green-500" />
            ) : (
              <XCircle className="h-4 w-4 text-red-500" />
            )}
          </div>
        </div>

        {configInfo.loaded_at && (
          <div className="pt-2 border-t">
            <div className="flex items-center text-xs text-muted-foreground">
              <Clock className="mr-1 h-3 w-3" />
              Loaded: {formatDateTime(configInfo.loaded_at)}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
