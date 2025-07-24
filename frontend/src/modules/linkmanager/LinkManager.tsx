import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { CheckCircle, XCircle, Loader2, Upload, Activity, AlertCircle } from 'lucide-react'
import { useWebsites, useHealthCheck } from '@/hooks/useApi'
import { LineNumberedTextarea } from '@/components/LineNumberedTextarea'
import { detectWebsiteFromUrl, detectPageIdFromUrl, isValidUrl } from '@/utils/urlHelpers'
import { useToast } from '@/hooks/use-toast'

interface FormData {
  importSourceUrls: string;
  importAnchorTexts: string;
  importTargetUrls: string;
}

interface ParsedLink {
  sourceUrl: string;
  anchorText: string;
  targetUrl: string;
  website?: string;
  pageId?: string;
}

interface BatchResult {
  link: ParsedLink;
  success: boolean;
  error?: string;
  result?: any;
}

interface BatchProgress {
  total: number;
  completed: number;
  isProcessing: boolean;
}

export default function LinkManager() {
  const [formData, setFormData] = useState<FormData>({
    importSourceUrls: '',
    importAnchorTexts: '',
    importTargetUrls: '',
  });

  const [parsedLinks, setParsedLinks] = useState<ParsedLink[]>([]);
  const [batchResults, setBatchResults] = useState<BatchResult[]>([]);
  const [batchProgress, setBatchProgress] = useState<BatchProgress>({
    total: 0,
    completed: 0,
    isProcessing: false,
  });

  const { data: websites = [], isLoading: websitesLoading } = useWebsites();
  const { data: healthData, isLoading: healthLoading } = useHealthCheck();
  const { toast } = useToast();

  const parseImportData = () => {
    const sourceUrls = formData.importSourceUrls.split('\n').filter(url => url.trim());
    const anchorTexts = formData.importAnchorTexts.split('\n').filter(text => text.trim());
    const targetUrls = formData.importTargetUrls.split('\n').filter(url => url.trim());

    if (sourceUrls.length !== anchorTexts.length || anchorTexts.length !== targetUrls.length) {
      toast({
        title: "Data mismatch",
        description: "Alle kolommen moeten hetzelfde aantal regels hebben",
        variant: "destructive"
      });
      return;
    }

    const parsed: ParsedLink[] = [];
    let validCount = 0;
    let invalidCount = 0;

    for (let i = 0; i < sourceUrls.length; i++) {
      const sourceUrl = sourceUrls[i].trim();
      const anchorText = anchorTexts[i].trim();
      const targetUrl = targetUrls[i].trim();

      if (!isValidUrl(sourceUrl) || !isValidUrl(targetUrl) || !anchorText) {
        invalidCount++;
        continue;
      }

      const matchingWebsite = detectWebsiteFromUrl(sourceUrl, websites);
      const detectedPageId = detectPageIdFromUrl(sourceUrl);

      if (matchingWebsite) {
        parsed.push({
          sourceUrl,
          anchorText,
          targetUrl,
          website: matchingWebsite?.website_url,
          pageId: detectedPageId || matchingWebsite?.page_id.toString() || '49',
        });
        validCount++;
      }
    }

    setParsedLinks(parsed);
    
    // Toast feedback
    if (validCount > 0) {
      toast({
        title: "Data geparsed",
        description: `${validCount} geldige links gevonden${invalidCount > 0 ? `, ${invalidCount} ongeldige overgeslagen` : ''}`,
        variant: "success"
      });
    } else {
      toast({
        title: "Geen geldige data",
        description: "Controleer of alle velden correct zijn ingevuld en URLs geldig zijn",
        variant: "destructive"
      });
    }
  };

  const handleBulkLinks = async () => {
    if (parsedLinks.length === 0) return;

    setBatchProgress({
      total: parsedLinks.length,
      completed: 0,
      isProcessing: true,
    });

    const results: BatchResult[] = [];

    for (let i = 0; i < parsedLinks.length; i++) {
      const link = parsedLinks[i];
      
      try {
        const response = await fetch('/api/links/bulk', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            anchor_text: link.anchorText,
            link_url: link.targetUrl,
            website_urls: [link.website],
            page_id: parseInt(link.pageId || '49'),
          }),
        });

        const result = await response.json();
        
        results.push({
          link,
          success: response.ok,
          result: result,
          error: response.ok ? undefined : result.detail || 'Unknown error'
        });

      } catch (error) {
        results.push({
          link,
          success: false,
          error: error instanceof Error ? error.message : 'Network error'
        });
      }

      setBatchProgress(prev => ({
        ...prev,
        completed: i + 1,
      }));
    }

    setBatchResults(results);
    setBatchProgress(prev => ({ ...prev, isProcessing: false }));

    const successCount = results.filter(r => r.success).length;
    const failureCount = results.length - successCount;

    toast({
      title: "Bulk import voltooid",
      description: `${successCount} links succesvol toegevoegd${failureCount > 0 ? `, ${failureCount} gefaald` : ''}`,
      variant: successCount > 0 ? "success" : "destructive"
    });
  };

  if (websitesLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Link Manager</h1>
          <p className="text-muted-foreground">
            Bulk import van links naar WordPress websites
          </p>
        </div>
        <div className="flex items-center gap-2 text-sm">
          {healthLoading ? (
            <div className="flex items-center gap-2 text-gray-500">
              <Loader2 className="h-4 w-4 animate-spin" />
              Checking status...
            </div>
          ) : healthData ? (
            <div className="flex items-center gap-2 text-green-600">
              <Activity className="h-4 w-4" />
              API Online • {websites.length} websites
            </div>
          ) : (
            <div className="flex items-center gap-2 text-red-600">
              <AlertCircle className="h-4 w-4" />
              API Offline
            </div>
          )}
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Bulk Import
          </CardTitle>
          <CardDescription>
            Importeer meerdere links tegelijk uit gestructureerde data
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Source URLs</label>
              <LineNumberedTextarea
                value={formData.importSourceUrls}
                onChange={(e) => setFormData(prev => ({ ...prev, importSourceUrls: e.target.value }))}
                placeholder="https://website1.com/page1&#10;https://website2.com/page2"
                className="min-h-[200px]"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Anchor Texts</label>
              <LineNumberedTextarea
                value={formData.importAnchorTexts}
                onChange={(e) => setFormData(prev => ({ ...prev, importAnchorTexts: e.target.value }))}
                placeholder="Link tekst 1&#10;Link tekst 2"
                className="min-h-[200px]"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Target URLs</label>
              <LineNumberedTextarea
                value={formData.importTargetUrls}
                onChange={(e) => setFormData(prev => ({ ...prev, importTargetUrls: e.target.value }))}
                placeholder="https://target1.com&#10;https://target2.com"
                className="min-h-[200px]"
              />
            </div>
          </div>

          <div className="flex gap-2">
            <Button onClick={parseImportData} variant="outline">
              Parse Data
            </Button>
            <Button 
              onClick={handleBulkLinks}
              disabled={parsedLinks.length === 0 || batchProgress.isProcessing}
            >
              {batchProgress.isProcessing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Verwerken... ({batchProgress.completed}/{batchProgress.total})
                </>
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" />
                  Start Bulk Import ({parsedLinks.length} links)
                </>
              )}
            </Button>
          </div>

          {batchProgress.isProcessing && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Voortgang</span>
                <span>{batchProgress.completed}/{batchProgress.total}</span>
              </div>
              <Progress value={(batchProgress.completed / batchProgress.total) * 100} />
            </div>
          )}

          {parsedLinks.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Geparsde Links ({parsedLinks.length})</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {parsedLinks.slice(0, 10).map((link, index) => (
                    <div key={index} className="flex items-center gap-2 text-sm p-2 bg-gray-50 rounded">
                      <span className="font-medium">{link.anchorText}</span>
                      <span className="text-gray-500">→</span>
                      <span className="text-blue-600">{link.targetUrl}</span>
                      <span className="text-gray-500">op</span>
                      <span className="text-green-600">{link.website}</span>
                    </div>
                  ))}
                  {parsedLinks.length > 10 && (
                    <div className="text-sm text-gray-500 text-center">
                      ... en {parsedLinks.length - 10} meer
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {batchResults.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Resultaten</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {batchResults.map((result, index) => (
                    <div key={index} className="flex items-center gap-2 text-sm p-2 rounded" 
                         style={{ backgroundColor: result.success ? '#f0f9ff' : '#fef2f2' }}>
                      {result.success ? (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      ) : (
                        <XCircle className="h-4 w-4 text-red-500" />
                      )}
                      <span className="font-medium">{result.link.anchorText}</span>
                      <span className="text-gray-500">→</span>
                      <span className="text-blue-600">{result.link.targetUrl}</span>
                      {result.error && (
                        <span className="text-red-600 text-xs">({result.error})</span>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
