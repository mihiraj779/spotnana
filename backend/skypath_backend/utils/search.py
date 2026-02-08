"""
DFS-based itinerary search with connection rules.

Responsibility: SkyPath Flight Connection Search.
"""
from typing import Dict, List

from skypath_backend.constants import (
    MAX_LAYOVER_MIN,
    MAX_STOPS,
    MIN_LAYOVER_DOMESTIC_MIN,
    MIN_LAYOVER_INTERNATIONAL_MIN,
)
from skypath_backend.utils.flight_loader import Flight


def valid_connection(prev: Flight, next_flight: Flight) -> bool:
    """
    Check if connection from prev to next_flight is valid.

    Same airport (no JFK→LGA), layover within [min, 6h].
    Domestic vs international: connection is domestic iff both the arriving
    and departing flights are within the same country.

    Args:
        prev: The flight that arrives at the connection airport.
        next_flight: The flight that departs from the connection airport.

    Returns:
        True if the connection satisfies all layover and same-airport rules.
    """
    if prev.destination != next_flight.origin:
        return False
    layover_delta = next_flight.departure_utc - prev.arrival_utc
    layover_minutes = int(layover_delta.total_seconds() / 60)
    if layover_minutes > MAX_LAYOVER_MIN:
        return False
    is_domestic = (
        prev.origin_country == prev.destination_country
        and next_flight.origin_country == next_flight.destination_country
    )
    min_layover = MIN_LAYOVER_DOMESTIC_MIN if is_domestic else MIN_LAYOVER_INTERNATIONAL_MIN
    if layover_minutes < min_layover:
        return False
    return True


def build_itinerary_output(path: List[Flight]) -> dict:
    """
    Build API response for one itinerary: segments, layovers, total duration, total price.

    Args:
        path: Ordered list of Flight segments in the itinerary.

    Returns:
        Dict with keys: segments, layovers, totalDurationMinutes, totalPrice.
    """
    segments = []
    layovers = []
    total_price = 0.0
    for i, fl in enumerate(path):
        segments.append({
            "flightNumber": fl.flight_number,
            "origin": fl.origin,
            "destination": fl.destination,
            "departureTime": fl.departure_local,
            "arrivalTime": fl.arrival_local,
            "price": fl.price,
        })
        total_price += fl.price
        if i + 1 < len(path):
            next_fl = path[i + 1]
            layover_delta = next_fl.departure_utc - fl.arrival_utc
            layovers.append({
                "airport": fl.destination,
                "durationMinutes": int(layover_delta.total_seconds() / 60),
            })
    first_dep = path[0].departure_utc
    last_arr = path[-1].arrival_utc
    total_duration_minutes = int((last_arr - first_dep).total_seconds() / 60)
    return {
        "segments": segments,
        "layovers": layovers,
        "totalDurationMinutes": total_duration_minutes,
        "totalPrice": round(total_price, 2),
    }


def search_itineraries(
    origin: str,
    destination: str,
    search_date: str,
    flights_from: Dict[str, List[Flight]],
) -> List[dict]:
    """
    Find all valid itineraries from origin to destination with first leg on search_date.

    Uses bounded DFS (max 2 stops). Only first legs departing on search_date (YYYY-MM-DD)
    are considered. Results are sorted by total travel duration (shortest first).

    Args:
        origin: Origin airport IATA code.
        destination: Destination airport IATA code.
        search_date: Departure date for first leg (YYYY-MM-DD).
        flights_from: Map of origin code -> list of Flight (from loader).

    Returns:
        List of itinerary dicts (segments, layovers, totalDurationMinutes, totalPrice).
    """
    results: List[dict] = []

    def dfs(path: List[Flight], stops: int) -> None:
        if stops > MAX_STOPS:
            return
        last_flight = path[-1]
        if last_flight.destination == destination:
            results.append(build_itinerary_output(path))
            return
        candidates = flights_from.get(last_flight.destination, [])
        for next_flight in candidates:
            if not valid_connection(last_flight, next_flight):
                continue
            dfs(path + [next_flight], stops + 1)

    first_flights = flights_from.get(origin, [])
    for fl in first_flights:
        if fl.departure_date == search_date:
            dfs([fl], 0)

    results.sort(key=lambda x: x["totalDurationMinutes"])
    return results
