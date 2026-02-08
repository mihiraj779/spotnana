# SkyPath: Flight Connection Search Engine

SkyPath is a backend service that searches valid flight itineraries—direct, one-stop, and two-stop—while enforcing connection rules and handling timezones correctly.

The service loads a static flight schedule, normalizes times to UTC, and computes all valid routes for a given origin, destination, and date.

---

## Features

- Direct, 1-stop, and 2-stop itinerary search
- Timezone-aware duration and layover calculations
- Clear connection rules (minimum/maximum layovers, same-airport constraint)
- Deterministic, fully in-memory search (no external dependencies)
- REST API with interactive documentation
- **Health check API** (in `core/`) for liveness and orchestration

---

## Project Structure

```
spotnana/
├── backend/
│   ├── skypath_backend/
│   │   ├── app.py
│   │   ├── constants.py
│   │   ├── core/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── utils/
│   │   └── tests/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── routes/
│   │   └── services/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── flights.json
├── instructions.md
└── docker-compose.yml
```

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

```
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

## Architecture Decisions

**Preprocessing at startup**  
`flights.json` is loaded once on application start. All timestamps are converted to UTC and flights are indexed by origin airport. This avoids repeated parsing and keeps request-time logic fast and simple.

**UTC-only internal logic**  
All comparisons (durations, layovers, ordering) are done using naive UTC datetimes. Local departure and arrival times are converted using each airport’s timezone, eliminating daylight-saving and offset issues.

**Bounded DFS search**  
With a small dataset (~260 flights) and a maximum of three segments, a depth-limited DFS (max two stops) is used to enumerate all valid itineraries. Results are sorted by total duration. Shortest-path algorithms are unnecessary because all valid paths are required.

**Centralized connection rules**  
Minimum and maximum layover rules and the same-airport constraint are implemented in a single `valid_connection()` function, driven by constants. This ensures consistent behavior across all searches.

**Query-parameter API**  
Search is performed using query parameters (origin, destination, date), aligning with the project’s API conventions.

---

## Tradeoffs

**In-memory data only**  
Flights are loaded from JSON rather than a database. This is sufficient for the assignment’s scale and keeps deployment simple.

**No per-request caching**  
Each search recomputes itineraries from the in-memory index. Given the bounded search space, this is inexpensive and predictable.

**Strict date filtering**  
Only itineraries whose first leg departs on the requested date are included. Arrival may occur on the following day.

**Graceful startup behavior**  
If `flights.json` is missing or fails to load, the application still starts and returns empty search results rather than failing on boot.

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
