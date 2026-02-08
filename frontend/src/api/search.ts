/**
 * SkyPath search API client.
 * Uses relative /v1 path so Vite proxy forwards to backend.
 */
import type { SearchResponse } from '../types';

const BASE = '/v1/skypath';

export interface SearchQuery {
  origin: string;
  destination: string;
  date: string;
}

export async function searchFlights(query: SearchQuery): Promise<SearchResponse> {
  const params = new URLSearchParams({
    origin: query.origin.trim().toUpperCase(),
    destination: query.destination.trim().toUpperCase(),
    date: query.date,
  });
  const res = await fetch(`${BASE}/search?${params.toString()}`);
  const data = await res.json();
  if (!res.ok) {
    const message = data.detail ?? data.message ?? 'Search failed';
    throw new Error(typeof message === 'string' ? message : JSON.stringify(message));
  }
  return data as SearchResponse;
}
