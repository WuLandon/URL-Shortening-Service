# URL Shortening Service API Scaffold

Production-ready Flask scaffold for a URL Shortening Service API using a layered architecture and blueprint-based routing.

## Current Scope

This repository currently includes only project structure and placeholders:
- App factory with environment-based config loading
- Blueprint registration and endpoint stubs
- Controller/service/model/schema layer placeholders
- Extension setup placeholder for future database integration
- Basic centralized error handling

Not implemented yet:
- URL shortening business logic
- Database models and persistence
- Payload validation rules
- Redirect behavior

## Project Structure

```text
app/
  __init__.py              # app factory
  config.py                # environment configs
  extensions.py            # db placeholder init

  api/
    __init__.py
    routes.py              # top-level API blueprint registration

    url/
      __init__.py
      routes.py            # endpoint handler stubs
      controller.py        # request/response orchestration placeholder
      service.py           # business logic placeholder
      model.py             # domain model placeholders
      schema.py            # validation placeholder

  core/
    utils.py               # shared helpers placeholder
    errors.py              # custom errors + handlers

run.py                     # app entry point
requirements.txt
.env.example
README.md
```

## Endpoints (Stubbed)

All routes are mounted under `/api/v1` and currently return `501 Not Implemented`.

- `POST /api/v1/shorten`
- `GET /api/v1/shorten/<shortCode>`
- `PUT /api/v1/shorten/<shortCode>`
- `DELETE /api/v1/shorten/<shortCode>`
- `GET /api/v1/shorten/<shortCode>/stats`

## Local Setup

1. Create a virtual environment and activate it.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy environment template:
   ```bash
   cp .env.example .env
   ```
4. Run the app:
   ```bash
   python run.py
   ```

## Notes for Next Steps

- Replace `app/extensions.py` placeholder with SQLAlchemy initialization.
- Implement validation in `app/api/url/schema.py`.
- Add business logic in `app/api/url/service.py`.
- Wire controller to service and return concrete API payloads.
