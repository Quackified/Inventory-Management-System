const envApiBaseUrl = import.meta.env.VITE_API_BASE_URL;
const API_BASE_URL = typeof envApiBaseUrl === "string" && envApiBaseUrl.trim()
  ? envApiBaseUrl.trim()
  : "http://127.0.0.1:20006";

/**
 * Convert a relative or absolute image URL to a full URL
 * @param url - The image URL (can be relative like `/uploads/avatars/...` or absolute)
 * @returns Full absolute URL for the image
 */
export function getImageUrl(url: string | null | undefined): string {
  if (!url) return "";
  // If URL already starts with http/https, return as-is
  if (url.startsWith("http://") || url.startsWith("https://")) {
    return url;
  }
  // Otherwise prepend API base URL
  return `${API_BASE_URL}${url}`;
}
