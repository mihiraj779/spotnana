/**
 * Flight search and airports API.
 */
import {
  buildSearchUrl,
  SKYPATH_ENDPOINTS,
} from "../../apiConstants/urlConstants";

export const searchFlights = async ({ origin, destination, date, page_number = 1, page_size = 10 }) => {
  const url = buildSearchUrl({ origin, destination, date, page_number, page_size });
  const response = await fetch(url);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = data.detail || data.message || "Search failed";
    throw new Error(message);
  }
  return data;
};

export const getAirports = async () => {
  const response = await fetch(SKYPATH_ENDPOINTS.AIRPORTS);
  const data = await response.json().catch(() => ({}));
  if (!response.ok)
    throw new Error(data.detail || data.message || "Failed to load airports");
  return Array.isArray(data) ? data : [];
};
