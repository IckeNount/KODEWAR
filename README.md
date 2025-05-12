# KODEWAR

A modern web application built with Next.js frontend and Django backend, using Docker for containerization.

## Tech Stack

### Frontend

- Next.js
- React
- TypeScript

### Backend

- Django
- Django Channels
- Celery
- PostgreSQL
- Redis

### Infrastructure

- Docker
- Docker Compose
- Colima (for macOS)

## Prerequisites

- Docker
- Colima (for macOS users)
- Git

## Getting Started

1. Clone the repository:

   ```bash
   git clone <your-repo-url>
   cd KODEWAR
   ```

2. Start Colima (if using macOS):

   ```bash
   colima start
   ```

3. Build and start the services:

   ```bash
   docker-compose up --build
   ```

4. Access the applications:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Celery Flower (Monitoring): http://localhost:5555

## Project Structure

```
KODEWAR/
├── frontend/          # Next.js frontend application
├── backend/           # Django backend application
│   ├── config/       # Django project configuration
│   └── core/         # Django core application
├── docker-compose.yml # Docker Compose configuration
└── README.md         # Project documentation
```

## Development

### Frontend Development

The frontend is a Next.js application running on port 3000. Hot reloading is enabled for development.

### Backend Development

The Django backend runs on port 8000 with Celery for background tasks. The Celery worker is configured with event monitoring enabled.

### Database

PostgreSQL is used as the main database, running on port 5432.

### Message Broker

Redis is used as the message broker for Celery, running on port 6379.

## Monitoring

Celery Flower is available at http://localhost:5555 for monitoring tasks and workers.

## License

[Your chosen license]
