/**
 * Flight search and airports API.
 * Responsibility: SkyPath Flight Connection Search (frontend).
 */
import {
  buildSearchUrl,
  SKYPATH_ENDPOINTS,
} from "../../apiConstants/urlConstants";

/**
 * Normalizes FastAPI error detail (string or array of { msg } objects) to a single display string.
 */
function normalizeApiErrorDetail(detail) {
  if (detail == null) return null;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0];
    return typeof first === "object" && first?.msg != null
      ? first.msg
      : String(first);
  }
  return null;
}

export const searchFlights = async ({
  origin,
  destination,
  date,
  page_number = 1,
  page_size = 10,
}) => {
  const url = buildSearchUrl({
    origin,
    destination,
    date,
    page_number,
    page_size,
  });
  const response = await fetch(url);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message =
      normalizeApiErrorDetail(data.detail) || data.message || "Search failed";
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
