# URL Shortening Service

A scalable URL shortening service built with a modular Flask architecture and backed by PostgreSQL and Redis.

The system supports short URL generation, custom aliases, fast redirects, and access tracking while emphasizing correctness, low-latency reads, and consistency under concurrent access.

## Overview

This service provides a RESTful API for:

- Creating, retrieving, updating, and deleting shortened URLs
- Redirecting short URLs to their original destinations
- Tracking URL access counts

The system is designed for:

- High read throughput
- Scalable URL generation

The repository intentionally focuses on implementing the core architecture while documenting how the system could evolve to support significantly larger workloads.

## System Goals

Note: The metrics and scaling targets below are architectural design targets and service-level objectives, not benchmarked or production-validated guarantees of the current implementation.

- **Low-Latency Redirects**
  - Target response time: <100ms for redirect requests

- **High Availability**
  - Design target: 99.99% uptime in a future replicated/failover deployment architecture

- **Scalability at Large Volume**
  - Projected capacity target: up to ~1B shortened URLs
  - Projected traffic target: ~500M redirects/day (~5.8K/sec average)
  - Projected peak throughput target: up to ~600K requests/second

## Features

- **Short, Unique, Efficient URL Generation**
  - Encodes up to ~1 billion URLs in ~6 characters, keeping generated URLs short and efficient
  - Ensures no collisions across all generated short URLs
  - Uses an atomic counter for fast, unique, and consistent short code creation under high concurrency

- **Fast Redirects with Access Tracking**
  - Short URLs resolve to their original destination URLs
  - URL access count increments with each visit

- **Optional Custom Aliases**
  - Supports user-defined short codes with validation and conflict handling

## Design Considerations

### Short, Unique, Efficient URL Generation

- Auto-generated short codes use a Redis-backed atomic counter and Base62 encoding, ensuring unique generated values without collisions.
- ~1 billion unique generated IDs can be represented in ~6 Base62 characters, allowing the system to scale to large volumes while keeping URLs short and efficient.
- Custom aliases are user-provided, validated, and enforced as unique.

### Fast Redirects

To support low-latency redirects at high read volume, the system uses Redis as an in-memory cache in front of the database.

- Uses a cache-aside (read-through) pattern for `shortCode → original URL` lookups
- Frequently accessed URLs remain cached in memory using an LRU eviction policy
- Cache hits avoid database reads, reducing load on the primary database under heavy redirect traffic
- Redirect requests still perform database writes for access count tracking, incurring database write latency

**Future optimization**: decouple access counting from the redirect path using buffered/asynchronous counter aggregation

### Future Scaling Considerations

The current implementation intentionally favors architectural simplicity while preserving a clear path toward larger-scale distributed deployment patterns.

At significantly larger scale, the system could evolve using strategies such as:

- Introducing a microservice architecture with independently scalable read and write services
- Horizontally scaling multiple service instances behind a load balancer
- Using database replication and failover for higher availability
- Using Redis counter batching to reduce network overhead during short code generation
- Allocating disjoint counter ranges across regions for multi-region deployments

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

### Alias Rules

- Aliases are normalized to lowercase
- Allowed characters: `a-z`, `0-9`, `_`, `-`
- Maximum length: 16 characters
- Aliases cannot start with `_`
- Reserved aliases are rejected: `api`, `shorten`, `redirect`, `admin`, `health`

### Example: Create Short URL

**Request Body**

```json
{
  "url": "https://example.com"
}
```

**Response (201)**

```json
{
  "id": 1,
  "url": "https://example.com",
  "shortCode": "_aZ91k",
  "createdAt": "2026-01-01T00:00:00Z",
  "updatedAt": "2026-01-01T00:00:00Z",
  "accessCount": 0
}
```

## Getting Started

### 1. Install Docker

Install Docker Desktop: https://www.docker.com/products/docker-desktop/

Verify installation:

```bash
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
  __init__.py
  config.py
  extensions.py
  api/
    __init__.py
    routes.py
    url/
      __init__.py
      constants.py
      controller.py
      model.py
      routes.py
      schema.py
      service.py
  core/
    __init__.py
    errors.py
migrations/
  versions/
tests/
  api/
  services/
  conftest.py
run.py
pyproject.toml
.env.example
Dockerfile
compose.yaml
```
