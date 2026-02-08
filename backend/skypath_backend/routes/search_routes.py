"""
Search endpoint for flight itineraries.

Query params: origin, destination, date (ISO 8601 YYYY-MM-DD).
Responsibility: SkyPath Flight Connection Search.
"""
import re
from typing import Any, List

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from skypath_backend.models.response import ItineraryResponse, SearchResponse
from skypath_backend.utils.search import search_itineraries

search_router = APIRouter()


@search_router.get(
    "/airports",
    summary="List airports",
    description="Returns list of airports (code, name, city, country) for dropdowns.",
)
def list_airports(request: Request) -> list:
    """Return airports list from app state."""
    state = request.app.state
    airports = getattr(state, "airports_list", None) or []
    return airports


def _get_state(request: Request) -> Any:
    """Access app state (airport_map, flights_from)."""
    return request.app.state


DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@search_router.get(
    "/search",
    response_model=SearchResponse,
    summary="Search flight itineraries",
    description="Returns valid itineraries (direct, 1-stop, 2-stop) sorted by total travel time. Supports pagination via page_number and page_size.",
)
def search(
    request: Request,
    origin: str = Query(..., description="Origin airport IATA code (e.g. JFK)"),
    destination: str = Query(..., description="Destination airport IATA code (e.g. LAX)"),
    date: str = Query(..., description="Departure date (YYYY-MM-DD)"),
    page_number: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page (default 10, max 100)"),
) -> JSONResponse | SearchResponse:
    """Search itineraries by origin, destination, and date (query parameters). Pagination applied server-side."""
    origin = origin.strip().upper()
    destination = destination.strip().upper()

    if not DATE_RE.match(date):
        return JSONResponse(
            status_code=400,
            content={"detail": "date must be YYYY-MM-DD"},
        )
    if origin == destination:
        return JSONResponse(
            status_code=400,
            content={"detail": "origin and destination must be different"},
        )

    state = _get_state(request)
    airport_map = getattr(state, "airport_map", None) or {}
    flights_from = getattr(state, "flights_from", None) or {}

    if origin not in airport_map:
        return JSONResponse(
            status_code=400,
            content={"detail": f"Invalid origin airport code: {origin}"},
        )
    if destination not in airport_map:
        return JSONResponse(
            status_code=400,
            content={"detail": f"Invalid destination airport code: {destination}"},
        )

    all_data: List[dict] = search_itineraries(
        origin=origin,
        destination=destination,
        search_date=date,
        flights_from=flights_from,
    )
    total_count = len(all_data)
    page_size = min(page_size, 100)
    page_number = max(page_number, 1)
    offset = (page_number - 1) * page_size
    page_data = all_data[offset : offset + page_size]
    itineraries = [ItineraryResponse(**it) for it in page_data]
    return SearchResponse(itineraries=itineraries, total_count=total_count)
