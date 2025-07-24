const API_BASE_URL = 'http://localhost:8000';

export interface Website {
  website_url: string;
  site_name: string;
  page_id: number;
  username?: string;
  app_password?: string;
}

export interface WebsiteRequest {
  website_url: string;
  site_name: string;
  page_id: number;
  username: string;
  app_password: string;
}

export interface UpdateWebsiteRequest {
  original_url: string;
  website_url: string;
  site_name: string;
  page_id: number;
  username: string;
  app_password: string;
}

export interface WebsiteResponse {
  success: boolean;
  message: string;
  website_url: string;
  site_name: string;
}

export interface LinkRequest {
  anchor_text: string;
  link_url: string;
  website_url: string;
  page_id?: number;
}

export interface BulkLinkRequest {
  anchor_text: string;
  link_url: string;
  website_urls: string[];
  page_id?: number;
}

export interface LinkResponse {
  success: boolean;
  message: string;
  website_url: string;
  page_id: number;
  link_added: boolean;
}

export interface WebsiteListResponse {
  websites: Website[];
}

export interface BlogPost {
  id?: number;
  title: string;
  slug: string;
  content: string;
  excerpt?: string;
  status: 'draft' | 'publish';
  categories?: string[];
  tags?: string[];
  featured_image?: string;
  created_at?: string;
  updated_at?: string;
}

export interface BlogCreateRequest {
  title: string;
  content: string;
  excerpt?: string;
  status: 'draft' | 'publish';
  categories?: string[];
  tags?: string[];
  website_url: string;
}

export interface BlogUpdateRequest extends BlogCreateRequest {
  id: number;
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new ApiError(response.status, errorText || `HTTP ${response.status}`);
  }

  return response.json();
}

export const api = {
  // Website management
  async getWebsites(): Promise<Website[]> {
    const response = await fetchApi<WebsiteListResponse>('/websites');
    return response.websites;
  },

  async addWebsite(request: WebsiteRequest): Promise<WebsiteResponse> {
    return fetchApi<WebsiteResponse>('/websites', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  async updateWebsite(request: UpdateWebsiteRequest): Promise<WebsiteResponse> {
    return fetchApi<WebsiteResponse>('/websites', {
      method: 'PUT',
      body: JSON.stringify(request),
    });
  },

  async deleteWebsite(website_url: string): Promise<WebsiteResponse> {
    return fetchApi<WebsiteResponse>(`/websites/${encodeURIComponent(website_url)}`, {
      method: 'DELETE',
    });
  },

  // Link management
  async addLink(request: LinkRequest): Promise<LinkResponse> {
    return fetchApi<LinkResponse>('/add-link', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  async addBulkLinks(request: BulkLinkRequest): Promise<LinkResponse[]> {
    return fetchApi<LinkResponse[]>('/add-bulk-links', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  // Blog management
  async getBlogs(website_url?: string): Promise<BlogPost[]> {
    const params = website_url ? `?website_url=${encodeURIComponent(website_url)}` : '';
    return fetchApi<BlogPost[]>(`/blogs${params}`);
  },

  async createBlog(request: BlogCreateRequest): Promise<BlogPost> {
    return fetchApi<BlogPost>('/blogs', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  async updateBlog(request: BlogUpdateRequest): Promise<BlogPost> {
    return fetchApi<BlogPost>(`/blogs/${request.id}`, {
      method: 'PUT',
      body: JSON.stringify(request),
    });
  },

  async deleteBlog(id: number): Promise<{ success: boolean; message: string }> {
    return fetchApi<{ success: boolean; message: string }>(`/blogs/${id}`, {
      method: 'DELETE',
    });
  },

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string; websites_loaded: number }> {
    return fetchApi<{ status: string; timestamp: string; websites_loaded: number }>('/health');
  },
};

