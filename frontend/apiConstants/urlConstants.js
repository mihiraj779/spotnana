/**
 * API URL constants for SkyPath frontend.
 * Backend: /v1/skypath/search?origin=&destination=&date=
 */
const APP_URL = typeof window !== "undefined" ? window.location.origin : "";
const API_BASE = `${APP_URL}/v1/skypath`;

export const SKYPATH_ENDPOINTS = {
  SEARCH: `${API_BASE}/search`,
  AIRPORTS: `${API_BASE}/airports`,
};

export const buildSearchUrl = (params) => {
  const searchParams = new URLSearchParams({
    origin: params.origin || "",
    destination: params.destination || "",
    date: params.date || "",
    page_number: String(params.page_number ?? 1),
    page_size: String(params.page_size ?? 10),
  });
  return `${SKYPATH_ENDPOINTS.SEARCH}?${searchParams.toString()}`;
};
