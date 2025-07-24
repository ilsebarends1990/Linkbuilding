import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { FileText, Save, Eye, Edit, Trash2 } from 'lucide-react'
import { useWebsites, useBlogs, useCreateBlog, useUpdateBlog, useDeleteBlog } from '@/hooks/useApi'
import { BlogPost } from '@/services/api'

interface BlogFormData {
  title: string;
  slug: string;
  content: string;
  excerpt: string;
  status: 'draft' | 'publish';
  website_url: string;
  categories: string;
  tags: string;
}

export default function BlogManager() {
  const [formData, setFormData] = useState<BlogFormData>({
    title: '',
    slug: '',
    content: '',
    excerpt: '',
    status: 'draft',
    website_url: '',
    categories: '',
    tags: '',
  });

  const [editingPost, setEditingPost] = useState<BlogPost | null>(null);
  const [selectedWebsite, setSelectedWebsite] = useState<string>('');

  const { data: websites = [] } = useWebsites();
  const { data: blogs = [] } = useBlogs(selectedWebsite);
  const createBlogMutation = useCreateBlog();
  const updateBlogMutation = useUpdateBlog();
  const deleteBlogMutation = useDeleteBlog();

  // Auto-generate slug from title
  const generateSlug = (title: string) => {
    return title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/(^-|-$)/g, '');
  };

  const handleTitleChange = (title: string) => {
    setFormData(prev => ({
      ...prev,
      title,
      slug: prev.slug || generateSlug(title),
    }));
  };

  const handleSubmit = async (status: 'draft' | 'publish') => {
    if (!formData.title || !formData.content || !formData.website_url) {
      return;
    }

    const blogData = {
      title: formData.title,
      content: formData.content,
      excerpt: formData.excerpt,
      status,
      website_url: formData.website_url,
      categories: formData.categories ? formData.categories.split(',').map(c => c.trim()) : [],
      tags: formData.tags ? formData.tags.split(',').map(t => t.trim()) : [],
    };

    try {
      if (editingPost) {
        await updateBlogMutation.mutateAsync({
          ...blogData,
          id: editingPost.id!,
        });
      } else {
        await createBlogMutation.mutateAsync(blogData);
      }

      // Reset form
      setFormData({
        title: '',
        slug: '',
        content: '',
        excerpt: '',
        status: 'draft',
        website_url: '',
        categories: '',
        tags: '',
      });
      setEditingPost(null);
    } catch (error) {
      console.error('Error saving blog:', error as Error);
    }
  };

  const handleEdit = (post: BlogPost) => {
    setEditingPost(post);
    setFormData({
      title: post.title,
      slug: post.slug,
      content: post.content,
      excerpt: post.excerpt || '',
      status: post.status,
      website_url: selectedWebsite,
      categories: post.categories?.join(', ') || '',
      tags: post.tags?.join(', ') || '',
    });
  };

  const handleDelete = async (id: number) => {
    if (confirm('Weet je zeker dat je deze blog wilt verwijderen?')) {
      try {
        await deleteBlogMutation.mutateAsync(id);
      } catch (error) {
        console.error('Error deleting blog:', error as Error);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      slug: '',
      content: '',
      excerpt: '',
      status: 'draft',
      website_url: '',
      categories: '',
      tags: '',
    });
    setEditingPost(null);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Blog Manager</h1>
        <p className="text-muted-foreground">
          Beheer blog posts op je WordPress websites
        </p>
      </div>

      <Tabs defaultValue="editor" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="editor">Blog Editor</TabsTrigger>
          <TabsTrigger value="list">Blog Overzicht</TabsTrigger>
        </TabsList>

        <TabsContent value="editor" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                {editingPost ? 'Bewerk Blog Post' : 'Nieuwe Blog Post'}
              </CardTitle>
              <CardDescription>
                Schrijf en publiceer blog posts naar je WordPress websites
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Website Selection */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Website</label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={formData.website_url}
                  onChange={(e) => setFormData(prev => ({ ...prev, website_url: e.target.value }))}
                >
                  <option value="">Selecteer website...</option>
                  {websites.map((site: any) => (
                    <option key={site.website_url} value={site.website_url}>
                      {site.site_name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Title and Slug */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Titel</label>
                  <Input
                    value={formData.title}
                    onChange={(e) => handleTitleChange(e.target.value)}
                    placeholder="Blog post titel"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Slug</label>
                  <Input
                    value={formData.slug}
                    onChange={(e) => setFormData(prev => ({ ...prev, slug: e.target.value }))}
                    placeholder="blog-post-slug"
                  />
                </div>
              </div>

              {/* Excerpt */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Excerpt</label>
                <Textarea
                  value={formData.excerpt}
                  onChange={(e) => setFormData(prev => ({ ...prev, excerpt: e.target.value }))}
                  placeholder="Korte samenvatting van de blog post..."
                  className="min-h-[80px]"
                />
              </div>

              {/* Content */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Content</label>
                <Textarea
                  value={formData.content}
                  onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
                  placeholder="Schrijf hier je blog post content..."
                  className="min-h-[300px]"
                />
              </div>

              {/* Categories and Tags */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Categorieën</label>
                  <Input
                    value={formData.categories}
                    onChange={(e) => setFormData(prev => ({ ...prev, categories: e.target.value }))}
                    placeholder="categorie1, categorie2"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Tags</label>
                  <Input
                    value={formData.tags}
                    onChange={(e) => setFormData(prev => ({ ...prev, tags: e.target.value }))}
                    placeholder="tag1, tag2, tag3"
                  />
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-2 pt-4">
                <Button
                  onClick={() => handleSubmit('draft')}
                  variant="outline"
                  disabled={Boolean(createBlogMutation.isPending || updateBlogMutation.isPending)}
                >
                  <Save className="mr-2 h-4 w-4" />
                  Opslaan als Concept
                </Button>
                <Button
                  onClick={() => handleSubmit('publish')}
                  disabled={Boolean(createBlogMutation.isPending || updateBlogMutation.isPending)}
                >
                  <Eye className="mr-2 h-4 w-4" />
                  Publiceren
                </Button>
                {editingPost && (
                  <Button onClick={resetForm} variant="outline">
                    Annuleren
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="list" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Blog Overzicht</CardTitle>
              <CardDescription>
                Bekijk en beheer je bestaande blog posts
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* Website Filter */}
              <div className="mb-4">
                <select
                  className="flex h-10 w-64 rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={selectedWebsite}
                  onChange={(e) => setSelectedWebsite(e.target.value)}
                >
                  <option value="">Alle websites</option>
                  {websites.map((site: any) => (
                    <option key={site.website_url} value={site.website_url}>
                      {site.site_name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Blog List */}
              <div className="space-y-4">
                {blogs.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    Geen blog posts gevonden
                  </div>
                ) : (
                  blogs.map((post: any) => (
                    <div key={post.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-semibold text-lg">{post.title}</h3>
                          <p className="text-muted-foreground text-sm mt-1">
                            {post.excerpt || 'Geen excerpt beschikbaar'}
                          </p>
                          <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                            <span className={`px-2 py-1 rounded text-xs ${
                              post.status === 'publish' 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {post.status === 'publish' ? 'Gepubliceerd' : 'Concept'}
                            </span>
                            {post.created_at && (
                              <span>{new Date(post.created_at).toLocaleDateString('nl-NL')}</span>
                            )}
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleEdit(post)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleDelete(post.id!)}
                            disabled={Boolean(deleteBlogMutation.isPending)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
