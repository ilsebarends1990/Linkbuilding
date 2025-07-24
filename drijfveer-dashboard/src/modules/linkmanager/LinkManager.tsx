import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { Plus, CheckCircle, XCircle, Loader2, Upload, Activity, AlertCircle } from 'lucide-react'
import { useWebsites, useAddLink, useHealthCheck } from '@/hooks/useApi'
import { LineNumberedTextarea } from '@/components/LineNumberedTextarea'
import { detectWebsiteFromUrl, detectPageIdFromUrl, isValidUrl } from '@/utils/urlHelpers'
import { useToast } from '@/hooks/use-toast'

interface FormData {
  anchorText: string;
  linkUrl: string;
  website: string;
  pageId: string;
  isImportMode: boolean;
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
    anchorText: '',
    linkUrl: '',
    website: '',
    pageId: '49',
    isImportMode: false,
    importSourceUrls: '',
    importAnchorTexts: '',
    importTargetUrls: '',
  });

  const [parsedLinks, setParsedLinks] = useState<ParsedLink[]>([]);
  const [bulkResults, setBulkResults] = useState<BatchResult[]>([]);
  const [batchProgress, setBatchProgress] = useState<BatchProgress>({
    total: 0,
    completed: 0,
    isProcessing: false
  });

  const { data: websites = [] } = useWebsites();
  const addLinkMutation = useAddLink();
  const { data: healthData, isLoading: healthLoading } = useHealthCheck();
  const { toast } = useToast();

  const parseImportData = () => {
    const sourceUrls = formData.importSourceUrls.split('\n').filter(line => line.trim());
    const anchorTexts = formData.importAnchorTexts.split('\n').filter(line => line.trim());
    const targetUrls = formData.importTargetUrls.split('\n').filter(line => line.trim());

    const maxLength = Math.max(sourceUrls.length, anchorTexts.length, targetUrls.length);
    const parsed: ParsedLink[] = [];
    let validCount = 0;
    let invalidCount = 0;

    for (let i = 0; i < maxLength; i++) {
      const sourceUrl = sourceUrls[i]?.trim() || '';
      const anchorText = anchorTexts[i]?.trim() || '';
      const targetUrl = targetUrls[i]?.trim() || '';

      if (sourceUrl && anchorText && targetUrl) {
        // Validate URLs
        if (!isValidUrl(sourceUrl) || !isValidUrl(targetUrl)) {
          invalidCount++;
          continue;
        }

        // Automatische website detectie
        const matchingWebsite = detectWebsiteFromUrl(sourceUrl, websites);
        
        // Automatische pagina ID detectie
        const detectedPageId = detectPageIdFromUrl(sourceUrl);
        
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

  const handleSingleLink = async () => {
    if (!formData.anchorText || !formData.linkUrl || !formData.website) {
      toast({
        title: "Incomplete gegevens",
        description: "Vul alle vereiste velden in",
        variant: "destructive"
      });
      return;
    }

    try {
      await addLinkMutation.mutateAsync({
        anchor_text: formData.anchorText,
        link_url: formData.linkUrl,
        website_url: formData.website,
        page_id: parseInt(formData.pageId) || undefined,
      });

      toast({
        title: "Link toegevoegd",
        description: `Link "${formData.anchorText}" succesvol toegevoegd`,
        variant: "success"
      });

      // Reset form
      setFormData(prev => ({
        ...prev,
        anchorText: '',
        linkUrl: '',
      }));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Onbekende fout';
      toast({
        title: "Fout bij toevoegen link",
        description: errorMessage,
        variant: "destructive"
      });
    }
  };

  const handleBulkLinks = async () => {
    if (parsedLinks.length === 0) {
      toast({
        title: "Geen links om te verwerken",
        description: "Parse eerst de import data",
        variant: "destructive"
      });
      return;
    }

    const validLinks = parsedLinks.filter(link => link.website);
    if (validLinks.length === 0) {
      toast({
        title: "Geen geldige links",
        description: "Geen van de links kon worden gekoppeld aan een website",
        variant: "destructive"
      });
      return;
    }

    setBatchProgress({
      total: validLinks.length,
      completed: 0,
      isProcessing: true
    });

    const results: BatchResult[] = [];
    let successCount = 0;
    let errorCount = 0;
    
    for (let i = 0; i < validLinks.length; i++) {
      const link = validLinks[i];
      
      try {
        const result = await addLinkMutation.mutateAsync({
          anchor_text: link.anchorText,
          link_url: link.targetUrl,
          website_url: link.website!,
          page_id: parseInt(link.pageId || '49'),
        });
        
        results.push({ link, success: true, result });
        successCount++;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Onbekende fout';
        results.push({ link, success: false, error: errorMessage });
        errorCount++;
      }
      
      // Update progress
      setBatchProgress(prev => ({
        ...prev,
        completed: i + 1
      }));
      
      // Small delay to prevent overwhelming the server
      if (i < validLinks.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 100));
      }
    }

    setBulkResults(results);
    setBatchProgress(prev => ({ ...prev, isProcessing: false }));
    
    // Final toast with summary
    toast({
      title: "Bulk verwerking voltooid",
      description: `${successCount} links succesvol toegevoegd${errorCount > 0 ? `, ${errorCount} fouten` : ''}`,
      variant: successCount > 0 ? "success" : "destructive"
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Link Manager</h1>
          <p className="text-muted-foreground">
            Beheer links op je WordPress websites
          </p>
        </div>
        
        {/* Health Check Status */}
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

      <Tabs defaultValue="single" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="single">Enkele Link</TabsTrigger>
          <TabsTrigger value="bulk">Bulk Import</TabsTrigger>
        </TabsList>

        <TabsContent value="single" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Plus className="h-5 w-5" />
                Voeg Enkele Link Toe
              </CardTitle>
              <CardDescription>
                Voeg een link toe aan een specifieke WordPress website
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Website</label>
                  <select
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    value={formData.website}
                    onChange={(e) => setFormData(prev => ({ ...prev, website: e.target.value }))}
                  >
                    <option value="">Selecteer website...</option>
                    {websites.map((site: any) => (
                      <option key={site.website_url} value={site.website_url}>
                        {site.site_name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Pagina ID</label>
                  <Input
                    type="number"
                    value={formData.pageId}
                    onChange={(e) => setFormData(prev => ({ ...prev, pageId: e.target.value }))}
                    placeholder="49"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Anchor Text</label>
                <Input
                  value={formData.anchorText}
                  onChange={(e) => setFormData(prev => ({ ...prev, anchorText: e.target.value }))}
                  placeholder="Bijv. 'Klik hier voor meer info'"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Link URL</label>
                <Input
                  type="url"
                  value={formData.linkUrl}
                  onChange={(e) => setFormData(prev => ({ ...prev, linkUrl: e.target.value }))}
                  placeholder="https://example.com"
                />
              </div>

              <Button 
                onClick={handleSingleLink}
                disabled={addLinkMutation.isPending || !formData.anchorText || !formData.linkUrl || !formData.website}
                className="w-full"
              >
                {addLinkMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Link Toevoegen...
                  </>
                ) : (
                  <>
                    <Plus className="mr-2 h-4 w-4" />
                    Voeg Link Toe
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="bulk" className="space-y-4">
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
                    `Voeg ${parsedLinks.length} Links Toe`
                  )}
                </Button>
              </div>

              {/* Progress Bar */}
              {batchProgress.isProcessing && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Verwerken...</span>
                    <span>{batchProgress.completed}/{batchProgress.total}</span>
                  </div>
                  <Progress value={(batchProgress.completed / batchProgress.total) * 100} />
                </div>
              )}

              {parsedLinks.length > 0 && (
                <div className="space-y-2">
                  <h3 className="font-medium">Geparsede Links ({parsedLinks.length})</h3>
                  <div className="max-h-60 overflow-y-auto space-y-2">
                    {parsedLinks.map((link, index) => (
                      <div key={index} className="p-3 border rounded-lg text-sm">
                        <div className="font-medium">{link.anchorText}</div>
                        <div className="text-muted-foreground text-xs">
                          {link.sourceUrl} → {link.targetUrl}
                        </div>
                        <div className="flex items-center gap-2 mt-1">
                          {link.website ? (
                            <span className="text-green-600 text-xs flex items-center gap-1">
                              <CheckCircle className="h-3 w-3" />
                              {websites.find(w => w.website_url === link.website)?.site_name || link.website}
                            </span>
                          ) : (
                            <span className="text-red-600 text-xs flex items-center gap-1">
                              <XCircle className="h-3 w-3" />
                              Geen website gevonden
                            </span>
                          )}
                          <span className="text-gray-500 text-xs">Pagina ID: {link.pageId}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {bulkResults.length > 0 && (
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <h3 className="font-medium">Resultaten</h3>
                    <div className="text-sm text-muted-foreground">
                      {bulkResults.filter(r => r.success).length} succesvol, {bulkResults.filter(r => !r.success).length} fouten
                    </div>
                  </div>
                  <div className="max-h-60 overflow-y-auto space-y-2">
                    {bulkResults.map((result, index) => (
                      <div key={index} className="p-3 border rounded-lg text-sm flex items-start gap-2">
                        {result.success ? (
                          <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                        )}
                        <div className="flex-1 min-w-0">
                          <div className="font-medium truncate">{result.link.anchorText}</div>
                          <div className="text-xs text-muted-foreground truncate">
                            {result.link.targetUrl}
                          </div>
                          <div className={`text-xs mt-1 ${result.success ? 'text-green-600' : 'text-red-600'}`}>
                            {result.success ? 'Succesvol toegevoegd' : result.error}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
