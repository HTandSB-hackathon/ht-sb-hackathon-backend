# Copilot Instructions

This repository contains a backend project. Please provide code completions and suggestions based on the following structure and guidelines.

## Technology Stack

- **Language & Framework**: Python + FastAPI  
- **Environment Variables Management**: Pydantic (`BaseSettings`)  
- **Database**: PostgreSQL  
- **Migration Management**: Alembic

## Project Structure

- **app/** - Main application directory
  - **api/** - API route definitions
    - **v1/** - API version 1 endpoints
      - **endpoints/** - Individual endpoint modules
  - **core/** - Core application settings and utilities
  - **crud/** - Database CRUD operations
  - **db/** - Database setup and session management
  - **migrations/** - Alembic migration scripts
  - **models/** - SQLAlchemy models
  - **schemas/** - Pydantic schemas for request/response models

- **k8s/** - Kubernetes deployment files
- **test/** - Test files
- **tools/** - Utility tools
- **docker-compose.yaml** - Local development environment
- **alembic.ini** - Alembic configuration

## Development Guidelines

- Follow FastAPI's standard structure for **routing, dependency injection, and exception handling**.
- Manage environment variables using `pydantic.BaseSettings`, loading them from `.env` files and centralizing configuration in settings classes.
- Use `SQLAlchemy` for PostgreSQL connections, with asynchronous implementations (`asyncpg` or `Databases` library).
- Implement **schema migrations** with Alembic. Consider automated generation and version management.

## Code Style and Best Practices

- Define endpoints using `async def` with asynchronous processing in mind.
- Implement dependency injection for DB session management using `Depends(get_db)`.
- Configure Alembic's `env.py` to target `Base.metadata` for automatic migrations.
- Pass PostgreSQL connection strings and sensitive information via `.env` files, avoiding hardcoding.

## Additional Notes

- Ensure type safety in schema definitions (`pydantic.BaseModel`).
- Follow existing code organization patterns:
  - Use separate modules for different domain entities (e.g., user.py, tasuki.py)
  - Maintain separation between models (SQLAlchemy) and schemas (Pydantic)
  - Keep core business logic in the appropriate layers