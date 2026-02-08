"""Request models for flight search API."""
import re

from pydantic import BaseModel, Field, field_validator


class FlightSearchRequest(BaseModel):
    """Query parameters for the flight search endpoint."""

    origin: str = Field(..., description="Origin airport IATA code (e.g. JFK)", min_length=3, max_length=3)
    destination: str = Field(..., description="Destination airport IATA code (e.g. LAX)", min_length=3, max_length=3)
    date: str = Field(..., description="Departure date in ISO 8601 format (YYYY-MM-DD)")

    @field_validator("origin", "destination")
    @classmethod
    def uppercase_code(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("date must be YYYY-MM-DD")
        return v
