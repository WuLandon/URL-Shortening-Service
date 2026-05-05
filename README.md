# URL Shortening Service

A RESTful API for creating, managing, and resolving shortened URLs.
Built with Flask, PostgreSQL, and Redis, the service focuses on correctness, validation, and consistency under concurrent access.

## Overview

This service provides core URL shortening functionality:

- Create, retrieve, update, and delete shortened URLs
- Redirect short codes to their original destinations
- Track access counts for each URL

## System Goals

- **Global Uniqueness**
  - Each short code maps to exactly one URL

- **Low-Latency Redirects**
  - Target response time < 100ms

- **High Availability**
  - 99.99% uptime (availability > strict consistency)

- **Scalability at Large Volume**
  - Supports up to ~1B shortened URLs
  - ~100M daily active users
  - ~500M redirects/day (~5.8K/sec average)
  - Handles peak traffic up to ~600K requests/second

## Features

- **Short, Unique, Efficient Code Generation**
  - Encodes up to ~1 billion URLs in ~6 characters, keeping links short and efficient
  - Ensures no collisions across all generated URLs
  - Uses an atomic counter for fast, consistent creation under high concurrency

- **Fast Redirects with Access Tracking**
  - Resolves short URLs to their original destination while incrementing access counts

- **Custom Aliases**
  - Supports user-defined short codes with validation and conflict handling

## Design Considerations

### Short, Unique, Efficient Code Generation

- Short codes are generated using a Redis-backed atomic counter and Base62 encoding, guaranteeing uniqueness without collisions.
- ~1 billion unique IDs can be represented in ~6 characters, allowing the system to scale to large volumes while keeping URLs short and efficient.

### Fast Redirects

- To ensure low-latency redirects, the system uses an in-memory cache (Redis) in front of the database
- Cache-aside (read-through) pattern:
  - Check cache for `shortCode → original URL`
  - Cache Hit → return immediately
  - Cache Miss → query database, then populate cache

- LRU eviction policy:
  - Keeps frequently accessed URLs in memory
  - Automatically evicts less-used entries under memory pressure

## API Reference

Base URL (local): `http://localhost:5000/api/v1`

### Endpoints

| Method | Endpoint                        | Description                    |
| ------ | ------------------------------- | ------------------------------ |
| POST   | `/shorten`                      | Create a short URL             |
| GET    | `/shorten/{shortCode}`          | Retrieve URL metadata          |
| PUT    | `/shorten/{shortCode}`          | Update URL and/or alias        |
| DELETE | `/shorten/{shortCode}`          | Delete a short URL             |
| GET    | `/shorten/{shortCode}/redirect` | Redirect to original URL (302) |

### Example: Create Short URL

**Request Body**

```json
{
  "url": "https://example.com"
}
```

**Response (201)**

```
{
  "id": 1,
  "url": "https://example.com",
  "shortCode": "_aZ91k",
  "createdAt": "2026-01-01T00:00:00Z",
  "updatedAt": "2026-01-01T00:00:00Z"
}
```

## Getting Started

### 1. Install Docker

Install Docker Desktop: https://www.docker.com/products/docker-desktop/

Verify installation:

```
docker --version
docker compose version
```

### 2. Configure Environment

The default values are preconfigured for Docker. No modifications required.

```bash
cp .env.example .env
```

### 3. Start Services

```bash
docker compose up --build
```

### 4. Access the Application

The API will be available at: [http://localhost:5000](http://localhost:5000)

See the [API Reference](#api-reference) section for available endpoints.

### 5. Stop Services

```bash
docker compose down
```

To reset all data (including database and Redis):

```bash
docker compose down -v
```

## Usage Example

```bash
curl -X POST http://localhost:5000/api/v1/shorten \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

## Tech Stack

- **Backend:** Flask, Flask-SQLAlchemy
- **Database:** PostgreSQL
- **Caching / Short Code Generation:** Redis
- **Migrations:** Alembic (Flask-Migrate)
- **Testing & Linting:** Pytest, Ruff

## Architecture

- **Routes (`routes.py`)** — HTTP layer (routing and response handling)
- **Controller (`controller.py`)** — request orchestration
- **Service (`service.py`)** — business logic and database interaction
- **Schema (`schema.py`)** — input validation and normalization
- **Model (`model.py`)** — SQLAlchemy ORM models

## Project Structure

```text
app/
  config.py
  extensions.py
  api/
    routes.py
    url/
      controller.py
      model.py
      routes.py
      schema.py
      service.py
  core/
    errors.py
    utils.py
migrations/
tests/
run.py
pyproject.toml
.env.example
```
