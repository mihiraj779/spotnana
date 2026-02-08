"""
Load and preprocess flights.json at startup.

Normalizes all times to UTC and builds airport map and flights-from-origin index.
Responsibility: SkyPath Flight Connection Search.
"""
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from zoneinfo import ZoneInfo


@dataclass
class AirportInfo:
    """Airport metadata from dataset."""

    code: str
    country: str
    timezone: str


@dataclass
class Flight:
    """Immutable flight with UTC times for search."""

    flight_number: str
    origin: str
    destination: str
    departure_utc: datetime
    arrival_utc: datetime
    price: float
    origin_country: str
    destination_country: str
    airline: str
    departure_local: str
    arrival_local: str

    @property
    def departure_date(self) -> str:
        """Return departure date (UTC) as YYYY-MM-DD for filtering by search date."""
        return self.departure_utc.strftime("%Y-%m-%d")


def _to_utc_naive(dt: datetime) -> datetime:
    """Convert to UTC and return naive datetime for consistent comparison."""
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)


def _safe_float(value) -> float:
    """Coerce price to float (dataset has some string values)."""
    if isinstance(value, (int, float)):
        return float(value)
    return float(str(value).strip())


def load_flights_and_airports(data_path: Path) -> tuple[Dict[str, AirportInfo], Dict[str, List[Flight]], List[dict]]:
    """
    Load flights.json, normalize times to UTC, build airport map and flights-from-origin index.

    Dataset times are in local airport time; they are converted to UTC using each
    airport's timezone. Flights whose origin or destination is not in the airports
    list are skipped. Price is coerced to float (handles string values in data).

    Args:
        data_path: Path to flights.json containing "airports" and "flights" keys.

    Returns:
        A tuple of (airport_map, flights_from, airports_list) where:
        - airport_map: IATA code -> AirportInfo.
        - flights_from: origin code -> list of Flight sorted by departure_utc.
        - airports_list: list of dicts with code, name, city, country for API.
    """
    import json

    raw = json.loads(data_path.read_text())
    airports_raw = raw["airports"]
    flights_raw = raw["flights"]

    airport_map: Dict[str, AirportInfo] = {}
    airports_list: List[dict] = []
    for a in airports_raw:
        airport_map[a["code"]] = AirportInfo(
            code=a["code"],
            country=a["country"],
            timezone=a["timezone"],
        )
        airports_list.append({
            "code": a["code"],
            "name": a.get("name", ""),
            "city": a.get("city", ""),
            "country": a["country"],
        })

    flights: List[Flight] = []
    for f in flights_raw:
        origin_code = f["origin"]
        dest_code = f["destination"]
        if origin_code not in airport_map or dest_code not in airport_map:
            continue
        origin_tz = airport_map[origin_code].timezone
        dest_tz = airport_map[dest_code].timezone
        dep_local = str(f["departureTime"])
        arr_local = str(f["arrivalTime"])
        dep_dt = datetime.fromisoformat(dep_local.replace("Z", "+00:00"))
        arr_dt = datetime.fromisoformat(arr_local.replace("Z", "+00:00"))
        if dep_dt.tzinfo is None:
            dep_utc = dep_dt.replace(tzinfo=ZoneInfo(origin_tz)).astimezone(ZoneInfo("UTC"))
        else:
            dep_utc = dep_dt.astimezone(ZoneInfo("UTC"))
        if arr_dt.tzinfo is None:
            arr_utc = arr_dt.replace(tzinfo=ZoneInfo(dest_tz)).astimezone(ZoneInfo("UTC"))
        else:
            arr_utc = arr_dt.astimezone(ZoneInfo("UTC"))
        dep_utc_naive = _to_utc_naive(dep_utc)
        arr_utc_naive = _to_utc_naive(arr_utc)
        price = _safe_float(f.get("price", 0))
        flights.append(
            Flight(
                flight_number=f["flightNumber"],
                origin=origin_code,
                destination=dest_code,
                departure_utc=dep_utc_naive,
                arrival_utc=arr_utc_naive,
                price=price,
                origin_country=airport_map[origin_code].country,
                destination_country=airport_map[dest_code].country,
                airline=f.get("airline", ""),
                departure_local=dep_local,
                arrival_local=arr_local,
            )
        )

    flights_from: Dict[str, List[Flight]] = {}
    for fl in flights:
        flights_from.setdefault(fl.origin, []).append(fl)
    for key in flights_from:
        flights_from[key].sort(key=lambda x: x.departure_utc)

    return airport_map, flights_from, airports_list
