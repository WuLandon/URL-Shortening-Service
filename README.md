# URL Shortening Service

A RESTful API for creating, managing, and resolving shortened URLs.
Built with Flask, PostgreSQL, and Redis, the service focuses on correctness, validation, and consistency under concurrent access.

## Overview

This service provides core URL shortening functionality:

- Create, retrieve, update, and delete shortened URLs
- Redirect short codes to their original destinations
- Track access counts for each URL

The system is designed with a layered architecture and emphasizes data integrity, predictable behavior under concurrency, and clear separation of concerns.

---

## Features

1. **Globally unique short codes**: Ensures no collisions across all generated URLs

2. **Compact short codes at scale**: Encodes up to ~1 billion URLs in ~6 characters, keeping links short and efficient

3. **Efficient code generation**: Uses an atomic counter for fast, consistent creation under high concurrency

4. **Custom aliases**: Supports user-defined short codes with validation and conflict handling

5. **Redirects with access tracking**: Resolves short URLs to their original destination while incrementing access counts

---

## Architecture

- **Routes (`routes.py`)** — HTTP layer (routing and response handling)
- **Controller (`controller.py`)** — request orchestration
- **Service (`service.py`)** — business logic and database interaction
- **Schema (`schema.py`)** — input validation and normalization
- **Model (`model.py`)** — SQLAlchemy ORM models

---

## Design Considerations

### Short Code Generation

- Short codes are generated using a Redis-backed atomic counter and Base62 encoding, guaranteeing uniqueness without collisions.
- 1 billion unique IDs can be represented in ~6 characters, allowing the system to scale to large volumes while keeping URLs short and efficient.

---

## Tech Stack

- **Backend:** Flask, Flask-SQLAlchemy
- **Database:** PostgreSQL
- **Caching / ID Generation:** Redis
- **Migrations:** Alembic (Flask-Migrate)
- **Testing & Linting:** Pytest, Ruff

---

## API Reference

Base URL: `/api/v1`

### Endpoints

#### Create Short URL

`POST /shorten`

- **Request Body**

```json
{
  "url": "https://example.com"
}
```

- **Response (201)**

```json
{
  "id": 1,
  "url": "https://example.com",
  "shortCode": "_aZ91k",
  "createdAt": "2026-01-01T00:00:00Z",
  "updatedAt": "2026-01-01T00:00:00Z"
}
```

---

#### Retrieve URL Metadata

`GET /shorten/<shortCode>`

- **Response (200)** — URL metadata
- **Response (404)** — not found

---

#### Update Short URL

`PUT /shorten/<shortCode>`

- Updates destination URL and/or alias

- **Response (200)** — updated resource

- **Response (404)** — not found

---

#### Delete Short URL

`DELETE /shorten/<shortCode>`

- **Response (204)** — deleted
- **Response (404)** — not found

---

#### Redirect

`GET /shorten/<shortCode>/redirect`

- Redirects to the original URL

- Increments access count

- **Response (302)** — redirect

- **Response (404)** — not found

---

## Getting Started

### 1. Install Dependencies

```bash
pip install -e ".[dev]"
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Required variables:

- `DATABASE_URL`
- `REDIS_URL`
- `SECRET_KEY`
- `FLASK_ENV`

---

### 3. Run Migrations

```bash
flask db upgrade
```

---

### 4. Start the Server

```bash
python run.py
```

---

## Usage Example

```bash
curl -X POST http://localhost:5000/api/v1/shorten \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

---

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
