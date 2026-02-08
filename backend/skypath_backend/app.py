#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Copyright          :   Mihir Raj
File               :   app.py
Description        :   SkyPath Flight Connection Search - Backend service
Responsibility     :   SkyPath Flight Connection Search
Author             :   Mihir Raj
Version            :   1
"""

import asyncio
import logging
import os
import traceback
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from skypath_backend.core.health import default_router
from skypath_backend.routes.search_routes import search_router
from skypath_backend.utils.flight_loader import load_flights_and_airports

logger = logging.getLogger("uvicorn")
logger.setLevel(os.environ.get("LOG_LEVEL", "DEBUG"))

SERVICE_NAME = os.environ.get("SERVICE_NAME", "skypath")
logger.info("SERVICE_NAME: %s", SERVICE_NAME)

app = FastAPI(
    docs_url=f"/v1/{SERVICE_NAME}/docs",
    openapi_url=f"/v1/{SERVICE_NAME}/openapi.json",
    title="SkyPath Flight Connection Search",
    description="Search valid flight itineraries (direct, 1-stop, 2-stop) with connection rules.",
    version="1.0",
)

app.include_router(default_router, tags=["Health Check"], prefix="")
app.include_router(search_router, tags=["Search"], prefix=f"/v1/{SERVICE_NAME}")


@app.on_event("startup")
async def startup_event() -> None:
    """Load flights.json and build indices once at startup."""
    try:
        base = Path(__file__).resolve().parent
        for candidate in (
            base.parent.parent / "flights.json",
            base.parent / "flights.json",
            Path("/app/flights.json"),
        ):
            if candidate.exists():
                data_path = candidate
                break
        else:
            data_path = None
        if data_path is None or not data_path.exists():
            logger.warning("flights.json not found; search will return empty results")
            app.state.airport_map = {}
            app.state.flights_from = {}
            app.state.airports_list = []
            return
        airport_map, flights_from, airports_list = load_flights_and_airports(data_path)
        app.state.airport_map = airport_map
        app.state.flights_from = flights_from
        app.state.airports_list = airports_list
        logger.info("Loaded %s airports, %s flight origins", len(airport_map), len(flights_from))
    except Exception as e:
        logger.warning("Flight data load failed: %s", str(e))
        app.state.airport_map = {}
        app.state.flights_from = {}
        app.state.airports_list = []


@app.on_event("shutdown")
async def shutdown_event() -> None:
    try:
        # SkyPath uses in-memory flight data; no DB/Redis connections to close
        pass
    except asyncio.exceptions.CancelledError:
        pass


@app.exception_handler(Exception)
async def global_error_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    error_dict = {
        "message": "The service encountered an error which we could not handle now.",
        "code": 31500,
    }
    if isinstance(exc, ValueError):
        error_dict["code"] = "400"
        error_dict["message"] = f"Invalid value provided: {str(exc)}"
        error_dict["detail"] = str(exc)
        status_code = status.HTTP_400_BAD_REQUEST
    else:
        status_code = 500

    if os.environ.get("LOG_LEVEL", "DEBUG") == "DEBUG":
        error_dict["detail"] = str(exc)
        error_dict["traceback"] = traceback.format_exc()
    logger.exception("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=status_code,
        content=error_dict,
    )


if __name__ == "__main__":
    uvicorn.run("skypath_backend.app:app", host="0.0.0.0", port=9090, reload=True)
