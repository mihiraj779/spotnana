#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test cases for flight search endpoint (instructions.md Test Cases 1–6).
Responsibility: SkyPath Flight Connection Search.
"""
import pytest
from fastapi.testclient import TestClient

from skypath_backend.app import app

SEARCH_URL = "/v1/skypath/search"
DATE = "2024-03-15"


@pytest.fixture(scope="module")
def client():
    """TestClient; startup loads flights.json."""
    with TestClient(app) as c:
        yield c


class TestSearchEndpoint:
    """Test cases from instructions.md - Use these to verify your implementation."""

    def test_1_jfk_lax_returns_direct_and_multi_stop(self, client: TestClient) -> None:
        """#1 JFK → LAX, 2024-03-15: Returns direct flights AND multi-stop options."""
        response = client.get(
            SEARCH_URL,
            params={"origin": "JFK", "destination": "LAX", "date": DATE},
        )
        assert response.status_code == 200
        data = response.json()
        assert "itineraries" in data
        assert "total_count" in data
        itineraries = data["itineraries"]
        assert len(itineraries) >= 1
        direct = [it for it in itineraries if len(it["segments"]) == 1]
        multi_stop = [it for it in itineraries if len(it["segments"]) >= 2]
        assert len(direct) >= 1, "Should return at least one direct flight"
        assert len(multi_stop) >= 1, "Should return at least one multi-stop option"

    def test_2_sfo_nrt_international_90_min_layover(self, client: TestClient) -> None:
        """#2 SFO → NRT, 2024-03-15: International route—90-minute minimum layover applies."""
        response = client.get(
            SEARCH_URL,
            params={"origin": "SFO", "destination": "NRT", "date": DATE},
        )
        assert response.status_code == 200
        data = response.json()
        itineraries = data.get("itineraries", [])
        for it in itineraries:
            for layover in it.get("layovers", []):
                assert (
                    layover["durationMinutes"] >= 90
                ), "International layover must be at least 90 minutes"

    def test_3_bos_sea_no_direct_must_find_connections(self, client: TestClient) -> None:
        """#3 BOS → SEA, 2024-03-15: No direct flight exists—must find connections."""
        response = client.get(
            SEARCH_URL,
            params={"origin": "BOS", "destination": "SEA", "date": DATE},
        )
        assert response.status_code == 200
        data = response.json()
        itineraries = data.get("itineraries", [])
        direct = [it for it in itineraries if len(it["segments"]) == 1]
        assert len(direct) == 0, "No direct flight should exist BOS → SEA"
        assert len(itineraries) >= 1, "Should find at least one connection"

    def test_4_jfk_jfk_validation_error_or_empty(self, client: TestClient) -> None:
        """#4 JFK → JFK, 2024-03-15: Should return empty results or validation error."""
        response = client.get(
            SEARCH_URL,
            params={"origin": "JFK", "destination": "JFK", "date": DATE},
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data or "message" in data

    def test_5_invalid_airport_code_graceful_error(self, client: TestClient) -> None:
        """#5 XXX → LAX, 2024-03-15: Invalid airport code—graceful error handling."""
        response = client.get(
            SEARCH_URL,
            params={"origin": "XXX", "destination": "LAX", "date": DATE},
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data or "message" in data
        assert "XXX" in str(data.get("detail", data.get("message", "")))

    def test_6_syd_lax_date_line_crossing(self, client: TestClient) -> None:
        """#6 SYD → LAX, 2024-03-15: Date line crossing—arrival appears 'before' departure in local time."""
        response = client.get(
            SEARCH_URL,
            params={"origin": "SYD", "destination": "LAX", "date": DATE},
        )
        assert response.status_code == 200
        data = response.json()
        assert "itineraries" in data
        # Should not crash; may return empty or valid itineraries depending on dataset
        itineraries = data["itineraries"]
        for it in itineraries:
            assert "segments" in it
            assert "totalDurationMinutes" in it
            assert "totalPrice" in it

    def test_invalid_date_format_returns_400(self, client: TestClient) -> None:
        """Edge case: invalid date format returns 400 (Correctness—edge cases covered)."""
        response = client.get(
            SEARCH_URL,
            params={"origin": "JFK", "destination": "LAX", "date": "03-15-2024"},
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data or "message" in data

    def test_search_pagination(self, client: TestClient) -> None:
        """Pagination: page_number and page_size return correct slice; total_count at root only."""
        response = client.get(
            SEARCH_URL,
            params={
                "origin": "JFK",
                "destination": "LAX",
                "date": DATE,
                "page_number": 1,
                "page_size": 2,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "itineraries" in data
        assert "total_count" in data
        assert "pagination" not in data
        total_count = data["total_count"]
        assert total_count >= len(data["itineraries"])
        assert len(data["itineraries"]) <= 2
