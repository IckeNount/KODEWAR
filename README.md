# Monorepo Project

This is a monorepo containing a Next.js frontend and Django backend with Channels and Celery.

## Project Structure

```
.
├── frontend/          # Next.js frontend application
├── backend/          # Django backend application
├── docker-compose.yml # Docker services configuration
└── README.md         # This file
```

## Services

- **Frontend**: Next.js application running on port 3000
- **Backend**: Django application with Channels and Celery running on port 8000
- **PostgreSQL**: Database running on port 5432
- **Redis**: Cache and message broker running on port 6379

## Prerequisites

- Docker
- Docker Compose

## Getting Started

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Start the services:

   ```bash
   docker-compose up
   ```

3. Access the applications:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## Development

- Frontend development files are in the `frontend/` directory
- Backend development files are in the `backend/` directory
- Each service has its own Dockerfile for building the container

## Environment Variables

The following environment variables are configured in docker-compose.yml:

### Backend

- `DEBUG`: Django debug mode
- `DJANGO_SETTINGS_MODULE`: Django settings module
- `DATABASE_URL`: PostgreSQL connection URL
- `REDIS_URL`: Redis connection URL

### Frontend

- `NODE_ENV`: Node.js environment

### Database

- `POSTGRES_DB`: PostgreSQL database name
- `POSTGRES_USER`: PostgreSQL username
- `POSTGRES_PASSWORD`: PostgreSQL password
