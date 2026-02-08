"""Response models for flight search API."""
from typing import List

from pydantic import BaseModel, Field


class FlightSegmentResponse(BaseModel):
    """Single flight segment in an itinerary."""

    flightNumber: str
    origin: str
    destination: str
    departureTime: str
    arrivalTime: str
    price: float


class LayoverResponse(BaseModel):
    """Layover between two segments."""

    airport: str
    durationMinutes: int


class ItineraryResponse(BaseModel):
    """One valid itinerary (direct or with connections)."""

    segments: List[FlightSegmentResponse]
    layovers: List[LayoverResponse]
    totalDurationMinutes: int
    totalPrice: float


class SearchResponse(BaseModel):
    """Response for the search endpoint. Only total_count at root besides itineraries."""

    itineraries: List[ItineraryResponse]
    total_count: int = Field(..., description="Total number of itineraries matching the search")
