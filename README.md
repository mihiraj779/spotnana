# SkyPath: Flight Connection Search Engine

A full-stack flight connection search engine that finds valid itineraries (direct, 1-stop, 2-stop) between airports with timezone-aware connection rules. Built with **FastAPI (Python)** and **React**, fully containerized via Docker Compose.

**Our approach:** We model the flight network as a graph, use DFS to enumerate all valid paths under strict connection rules, and keep all time logic in UTC while comparing dates in local airport time. The backend owns search and itinerary construction; the frontend handles input, sorting, and presentation.

---

## How to Run

### Backend + Frontend (Docker — recommended)

From the `spotnana` directory:

```bash
docker compose up --build
```

**Services:**

- **Frontend:** http://localhost:3030
- **Backend API:** http://localhost:9090
- **API Docs:** http://localhost:9090/v1/skypath/docs
- **Health check:** http://localhost:9090/health

The frontend Vite server proxies `/v1` requests to the backend.

### Backend Only (Docker)

From the `spotnana/backend` directory:

```bash
docker compose up --build
```

- **API:** http://localhost:9090
- **Docs:** http://localhost:9090/v1/skypath/docs
- **Health check:** http://localhost:9090/health
- **Example search:** `GET /v1/skypath/search?origin=JFK&destination=LAX&date=2024-03-15`

### Health check API

The backend exposes a liveness endpoint in **`skypath_backend/core/health.py`**:

- **`GET /health`** — Returns `{"status": "OK"}` when the service is up. Use it for load balancers, container orchestration (e.g. Docker/Kubernetes), and monitoring.

### Backend (Local)

```bash
cd spotnana/backend
pip install -r requirements.txt
```

Ensure `flights.json` exists at:

```text
spotnana/flights.json
```

Run the server:

```bash
PYTHONPATH=. python3 -m uvicorn skypath_backend.app:app \
  --host 0.0.0.0 \
  --port 9090 \
  --reload
```

### Frontend (Local Dev)

```bash
cd spotnana/frontend
npm install
npm run dev
```

- **App:** http://localhost:3030
- Backend must be running on port 9090.

### Tests

```bash
cd spotnana/backend
pip install -r requirements.txt
PYTHONPATH=. python3 -m pytest skypath_backend/tests -v
```

With coverage:

```bash
PYTHONPATH=. python3 -m coverage run -m pytest skypath_backend/tests -v
python3 -m coverage report
```

---

## Features

- **Search** valid flight itineraries between origin and destination by **date**
- **Supports:** direct and multi-leg flights (up to 3 segments / 2 layovers), domestic and international layover rules, timezone-aware date filtering
- **Returns:** full flight sequences, layover durations at each connection, total price and total travel time
- **Frontend:** search form, itinerary cards, sorting and visualization
- **Backend:** REST API with query-parameter search, OpenAPI docs, health check for orchestration

---

## Project Structure

```text
spotnana/
├── backend/
│   ├── skypath_backend/
│   │   ├── app.py                 # FastAPI app, startup data load
│   │   ├── constants.py           # Layover limits, max stops
│   │   ├── core/
│   │   │   └── health.py          # GET /health
│   │   ├── models/                # Request/response Pydantic models
│   │   ├── routes/
│   │   │   └── search_routes.py   # GET /search, GET /airports
│   │   ├── utils/
│   │   │   ├── flight_loader.py   # Load flights.json, UTC normalization
│   │   │   └── search.py          # DFS search + connection rules
│   │   └── tests/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/            # SearchForm, FlightResults, ItineraryCard, etc.
│   │   ├── pages/
│   │   ├── routes/
│   │   └── services/              # flightSearchService
│   ├── vite.config.js
│   └── package.json
├── flights.json                   # Source flight data
├── docker-compose.yml             # Backend + frontend
└── README.md
```

---

## API Reference

### Search flights

**GET** `/v1/skypath/search`

All parameters are **query parameters** (no path parameters).

| Parameter     | Type   | Description |
|---------------|--------|-------------|
| `origin`      | string | 3-letter IATA airport code (e.g. JFK) |
| `destination` | string | 3-letter IATA airport code (e.g. LAX) |
| `date`        | string | ISO date YYYY-MM-DD (e.g. 2024-03-15) |
| `page_number` | int    | Optional, default 1 |
| `page_size`   | int    | Optional, default 10, max 100 |

**Example success (200):**

```json
{
  "itineraries": [
    {
      "segments": [
        {
          "flightNumber": "SP101",
          "origin": "JFK",
          "destination": "LAX",
          "departureTime": "2024-03-15T08:30:00-05:00",
          "arrivalTime": "2024-03-15T11:45:00-08:00",
          "price": 299.0
        }
      ],
      "layovers": [],
      "totalDurationMinutes": 375,
      "totalPrice": 299.0
    }
  ],
  "total_count": 1
}
```

**Example error (400):** invalid origin/destination, same origin and destination, or invalid date format.

### List airports

**GET** `/v1/skypath/airports`

Returns all airports in the dataset (code, name, city, country) for dropdowns.

### Health check

**GET** `/health`

Returns `{"status": "OK"}` when the service is up. Used for load balancers and container orchestration.

---

## Architecture Decisions

- **Preprocessing at startup:** `flights.json` is loaded once on application start. All timestamps are converted to UTC and flights are indexed by origin airport. This avoids repeated parsing and keeps request-time logic fast and simple.
- **UTC-only internal logic:** All comparisons (durations, layovers, ordering) use naive UTC datetimes. Local departure and arrival times are converted using each airport’s timezone at load, eliminating DST and offset issues in arithmetic.
- **In-memory index:** With a small dataset (e.g. ~25 airports, hundreds of flights), a database would add operational complexity with no real benefit. We use two structures at startup: an airport map (code → metadata) and an adjacency-style map (origin → list of flights). Lookup by origin is the main operation for search and is O(1); this fits the DFS traversal model.
- **Bounded DFS search:** With a maximum of three segments (two stops), a depth-limited DFS enumerates all valid itineraries. Results are sorted by total duration. Shortest-path algorithms (e.g. Dijkstra) are not used because we need all valid paths, not a single optimum.
- **Centralized connection rules:** Minimum and maximum layover rules and the same-airport constraint are implemented in a single place (`valid_connection()` in `search.py`), driven by constants in `constants.py`. This keeps behavior consistent and easy to change.
- **Query-parameter API:** Search uses query parameters (origin, destination, date, pagination) only, aligning with project conventions and keeping the API uniform for optional parameters.
- **Centralized error handling:** A global exception handler in the FastAPI app returns a consistent error shape and avoids leaking internals; validation errors (e.g. invalid origin/destination) return 400 with a clear message.
- **Frontend proxy in development:** The Vite dev server proxies `/v1` to the backend so the frontend can call the API without CORS issues during local development; production can use a similar reverse-proxy setup.

---

## Core Design Decisions (Our Approach)

### 1. Flights as a graph

The flight network is modeled as a **directed graph**:

- **Nodes** → airports  
- **Edges** → flights (with time, price, metadata)

An adjacency structure maps each airport to its outgoing flights (`flights_from`). This makes connection search a path-finding problem: connections, cycles, and layovers map cleanly to traversal and constraint checks.

### 2. DFS-based itinerary search

We use **depth-first search (DFS)** to enumerate all valid itineraries.

- **Why DFS:** The goal is to find *all* valid itineraries, not only the cheapest or shortest. DFS allows a hard stop (max 3 segments), early pruning of invalid paths, and straightforward enforcement of domain rules.
- **Constraints enforced during DFS:** maximum flights (≤ 3), no repeated flights (cycle prevention), valid layover duration, and first flight departs on the requested date (local time). This keeps the algorithm correct and explainable.

**Tradeoffs considered:** Dijkstra or A* would optimize a single metric (e.g. cost or time) and do not naturally enumerate all valid paths; for this prototype we prioritize correctness and clarity over single-path optimization.

### 3. Time handling strategy

We follow a strict rule:

- **All calculations** → UTC (naive `datetime` in code).
- **All date comparisons** → local airport time.

Each flight’s local departure/arrival is converted to UTC at ingestion. Durations and layovers are computed in UTC. The requested date is interpreted as the **local departure date** at the origin airport.

This avoids bugs from international date-line crossings, late-night departures, and mixed timezone arithmetic. **Dates are local concepts; times are global (UTC) concepts.**

### 4. Layover validation

Layovers are validated with fixed constants (minutes) for clarity and consistent `datetime` math:

| Rule              | Domestic | International |
|-------------------|----------|---------------|
| Minimum layover   | 45 min   | 90 min        |
| Maximum layover   | 6 hours  | 6 hours       |

A connection is **domestic** only if both the arriving and departing flights are within the same country (origin and destination country of each flight). Otherwise it is international and must satisfy the 90-minute minimum.

### 5. Backend–frontend separation

- **Backend (FastAPI):** search logic, time handling, itinerary construction, connection rules, pagination.
- **Frontend (React):** user input, calling the API, sorting, and presentation of segments, layovers, and total time/price.

---

## Tradeoffs

- **In-memory data:** Flights are loaded from JSON at startup; no database. Sufficient for the current scale and keeps deployment simple. No real-time updates or multi-source ingestion.
- **No per-request caching:** Each search recomputes itineraries from the in-memory index. With a bounded search space this remains inexpensive.
- **Strict date filtering:** Only itineraries whose first leg departs on the requested date (local time at origin) are included; arrival may be the next day. We do not support flexible-date search (e.g. ±3 days).
- **Graceful startup:** If `flights.json` is missing or fails to load, the app still starts and returns empty search results instead of failing on boot.
- **Query parameters only:** Search uses query parameters (`origin`, `destination`, `date`, `page_number`, `page_size`) rather than path parameters. This keeps the API uniform, aligns with project conventions, and makes optional parameters (e.g. pagination) easy to add. Path-style resources (e.g. `/search/JFK/LAX/2024-03-15`) were not chosen.
- **Naive UTC internally:** All duration and layover math uses UTC datetimes with `tzinfo` stripped after conversion. This avoids DST and offset bugs in arithmetic; local times are kept as strings for display only. We did not keep timezone-aware datetimes throughout the pipeline.
- **Pagination after full search:** We run the full DFS, collect all valid itineraries, sort by duration, then slice by `page_number`/`page_size`. Response size is bounded and clients get a consistent total count, but the server does full work every request. Early termination (e.g. top-K) was not implemented.
- **Single sort order:** Results are returned sorted by total duration only. Sort-by-price or sort-by-stops is not exposed in the API; the frontend can re-sort if needed. We prioritized a simple contract over multiple sort options.
- **Index by origin only:** The adjacency structure is `flights_from` (origin → list of flights). We do not maintain a reverse index (destination → flights). Sufficient for forward DFS from origin; bidirectional or destination-centric search would require additional indexes.
- **Same-airport connections:** A valid connection requires the same airport (prev flight’s destination equals next flight’s origin). Inter-airport transfers (e.g. JFK to LGA) are not supported; we treat this as the intended domain rule.
- **API versioning prefix:** Routes live under `/v1/skypath` so we can evolve the API without breaking existing clients. Slightly longer paths in exchange for clear versioning.

---

## Future Improvements

**Frontend**  
Add a full search UI with form inputs, itinerary cards, pricing display, and proper loading and error states.

**Testing**  
Expand unit coverage for connection rules (domestic vs international, boundary layovers) and add timezone edge-case tests (e.g., date-line crossings).

**Validation**  
Introduce stricter request validation and a consistent error response format.

**Observability**  
Add structured logging, metrics (latency, result count), and a health endpoint that verifies data loading.

**Data hygiene**  
Validate and optionally normalize known data issues (e.g., airport code typos, string-encoded prices) during load or via a preprocessing script.

---

## Dataset

The app ships with a static dataset (`flights.json`) of airports and flights (e.g. 25 airports, hundreds of flights). All times are normalized to UTC at load; the dataset is designed to exercise direct flights, domestic and international connections, and timezone/date-line cases.

---


