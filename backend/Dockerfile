# SkyPath Backend - Flight Connection Search
# Responsibility: SkyPath Flight Connection Search
# Build from repo root (spotnana/): docker build -f backend/Dockerfile .

ARG PY_VERSION="3.12"

FROM python:${PY_VERSION}-slim

RUN pip install -U pip

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/skypath_backend/ ./skypath_backend/
COPY flights.json ./flights.json

ENV PYTHONPATH="/app:${PYTHONPATH}"
ENV SERVICE_NAME=skypath
ENV HOST=0.0.0.0
ENV PORT=9090

EXPOSE 9090

CMD ["uvicorn", "skypath_backend.app:app", "--host", "0.0.0.0", "--port", "9090"]
