import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api, WebsiteRequest, UpdateWebsiteRequest, LinkRequest, BulkLinkRequest, BlogCreateRequest, BlogUpdateRequest } from '@/services/api';

// Query keys
export const queryKeys = {
  websites: ['websites'] as const,
  blogs: (website_url?: string) => ['blogs', website_url] as const,
  health: ['health'] as const,
};

// Website hooks
export function useWebsites() {
  return useQuery({
    queryKey: queryKeys.websites,
    queryFn: api.getWebsites,
  });
}

export function useAddWebsite() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: WebsiteRequest) => api.addWebsite(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.websites });
    },
  });
}

export function useUpdateWebsite() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: UpdateWebsiteRequest) => api.updateWebsite(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.websites });
    },
  });
}

export function useDeleteWebsite() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (website_url: string) => api.deleteWebsite(website_url),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.websites });
    },
  });
}

// Link hooks
export function useAddLink() {
  return useMutation({
    mutationFn: (request: LinkRequest) => api.addLink(request),
  });
}

export function useAddBulkLinks() {
  return useMutation({
    mutationFn: (request: BulkLinkRequest) => api.addBulkLinks(request),
  });
}

// Blog hooks
export function useBlogs(website_url?: string) {
  return useQuery({
    queryKey: queryKeys.blogs(website_url),
    queryFn: () => api.getBlogs(website_url),
  });
}

export function useCreateBlog() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: BlogCreateRequest) => api.createBlog(request),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.blogs(variables.website_url) });
      queryClient.invalidateQueries({ queryKey: queryKeys.blogs() });
    },
  });
}

export function useUpdateBlog() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: BlogUpdateRequest) => api.updateBlog(request),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.blogs(variables.website_url) });
      queryClient.invalidateQueries({ queryKey: queryKeys.blogs() });
    },
  });
}

export function useDeleteBlog() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => api.deleteBlog(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.blogs() });
    },
  });
}

// Health check hook
export function useHealthCheck() {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: api.healthCheck,
    refetchInterval: 10000, // Refetch every 10 seconds
    refetchOnMount: true,
    refetchOnWindowFocus: true,
    retry: 3,
    staleTime: 5000, // Data is stale after 5 seconds
  });
}
