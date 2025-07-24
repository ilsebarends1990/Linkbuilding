import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Globe, Plus, Edit, Trash2, Save, X } from 'lucide-react'
import { useWebsites, useAddWebsite, useUpdateWebsite, useDeleteWebsite } from '@/hooks/useApi'
import { Website } from '@/services/api'

interface WebsiteFormData {
  website_url: string;
  site_name: string;
  page_id: string;
  username: string;
  app_password: string;
}

interface EditingWebsite extends WebsiteFormData {
  original_url: string;
}

export default function WebsiteManager() {
  const [isAddingWebsite, setIsAddingWebsite] = useState(false);
  const [editingWebsite, setEditingWebsite] = useState<EditingWebsite | null>(null);
  const [formData, setFormData] = useState<WebsiteFormData>({
    website_url: '',
    site_name: '',
    page_id: '49',
    username: '',
    app_password: '',
  });

  const { data: websites = [], isLoading } = useWebsites();
  const addWebsiteMutation = useAddWebsite();
  const updateWebsiteMutation = useUpdateWebsite();
  const deleteWebsiteMutation = useDeleteWebsite();

  const resetForm = () => {
    setFormData({
      website_url: '',
      site_name: '',
      page_id: '49',
      username: '',
      app_password: '',
    });
    setIsAddingWebsite(false);
    setEditingWebsite(null);
  };

  const handleAdd = async () => {
    if (!formData.website_url || !formData.site_name || !formData.username || !formData.app_password) {
      return;
    }

    try {
      await addWebsiteMutation.mutateAsync({
        website_url: formData.website_url,
        site_name: formData.site_name,
        page_id: parseInt(formData.page_id) || 49,
        username: formData.username,
        app_password: formData.app_password,
      });
      resetForm();
    } catch (error) {
      console.error('Error adding website:', error);
    }
  };

  const handleUpdate = async () => {
    if (!editingWebsite || !formData.website_url || !formData.site_name || !formData.username || !formData.app_password) {
      return;
    }

    try {
      await updateWebsiteMutation.mutateAsync({
        original_url: editingWebsite.original_url,
        website_url: formData.website_url,
        site_name: formData.site_name,
        page_id: parseInt(formData.page_id) || 49,
        username: formData.username,
        app_password: formData.app_password,
      });
      resetForm();
    } catch (error) {
      console.error('Error updating website:', error);
    }
  };

  const handleEdit = (website: Website) => {
    setEditingWebsite({
      original_url: website.website_url,
      website_url: website.website_url,
      site_name: website.site_name,
      page_id: website.page_id.toString(),
      username: website.username || '',
      app_password: website.app_password || '',
    });
    setFormData({
      website_url: website.website_url,
      site_name: website.site_name,
      page_id: website.page_id.toString(),
      username: website.username || '',
      app_password: website.app_password || '',
    });
  };

  const handleDelete = async (website_url: string) => {
    if (confirm('Weet je zeker dat je deze website wilt verwijderen?')) {
      try {
        await deleteWebsiteMutation.mutateAsync(website_url);
      } catch (error) {
        console.error('Error deleting website:', error);
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Website Manager</h1>
          <p className="text-muted-foreground">
            Beheer je WordPress websites en configuraties
          </p>
        </div>
        <Button onClick={() => setIsAddingWebsite(true)} disabled={isAddingWebsite || !!editingWebsite}>
          <Plus className="mr-2 h-4 w-4" />
          Website Toevoegen
        </Button>
      </div>

      {/* Add/Edit Form */}
      {(isAddingWebsite || editingWebsite) && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="h-5 w-5" />
              {editingWebsite ? 'Website Bewerken' : 'Nieuwe Website Toevoegen'}
            </CardTitle>
            <CardDescription>
              {editingWebsite 
                ? 'Bewerk de website configuratie' 
                : 'Voeg een nieuwe WordPress website toe aan je dashboard'
              }
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Website URL</label>
                <Input
                  type="url"
                  value={formData.website_url}
                  onChange={(e) => setFormData(prev => ({ ...prev, website_url: e.target.value }))}
                  placeholder="https://example.com"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Site Naam</label>
                <Input
                  value={formData.site_name}
                  onChange={(e) => setFormData(prev => ({ ...prev, site_name: e.target.value }))}
                  placeholder="Mijn Website"
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Pagina ID</label>
                <Input
                  type="number"
                  value={formData.page_id}
                  onChange={(e) => setFormData(prev => ({ ...prev, page_id: e.target.value }))}
                  placeholder="49"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Username</label>
                <Input
                  value={formData.username}
                  onChange={(e) => setFormData(prev => ({ ...prev, username: e.target.value }))}
                  placeholder="WordPress gebruikersnaam"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">App Password</label>
                <Input
                  type="password"
                  value={formData.app_password}
                  onChange={(e) => setFormData(prev => ({ ...prev, app_password: e.target.value }))}
                  placeholder="WordPress app password"
                />
              </div>
            </div>

            <div className="flex gap-2 pt-4">
              <Button
                onClick={editingWebsite ? handleUpdate : handleAdd}
                disabled={addWebsiteMutation.isPending || updateWebsiteMutation.isPending}
              >
                <Save className="mr-2 h-4 w-4" />
                {editingWebsite ? 'Bijwerken' : 'Toevoegen'}
              </Button>
              <Button onClick={resetForm} variant="outline">
                <X className="mr-2 h-4 w-4" />
                Annuleren
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Websites List */}
      <Card>
        <CardHeader>
          <CardTitle>Geconfigureerde Websites</CardTitle>
          <CardDescription>
            Overzicht van alle WordPress websites in je dashboard
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8 text-muted-foreground">
              Websites laden...
            </div>
          ) : websites.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              Nog geen websites geconfigureerd. Voeg je eerste website toe!
            </div>
          ) : (
            <div className="space-y-4">
              {websites.map((website: Website) => (
                <div key={website.website_url} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <Globe className="h-4 w-4 text-muted-foreground" />
                        <h3 className="font-semibold">{website.site_name}</h3>
                      </div>
                      <p className="text-sm text-muted-foreground mt-1">
                        {website.website_url}
                      </p>
                      <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                        <span>Pagina ID: {website.page_id}</span>
                        <span>Gebruiker: {website.username}</span>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleEdit(website)}
                        disabled={isAddingWebsite || !!editingWebsite}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDelete(website.website_url)}
                        disabled={deleteWebsiteMutation.isPending || isAddingWebsite || !!editingWebsite}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
