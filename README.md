# Finance Tracker API

A FastAPI-based personal finance tracking application that follows 12-Factor app principles.

## Features

- User authentication and authorization
- Transaction management (create, read, update, delete)
- Category management for transactions
- Support for multiple currencies
- Secure password hashing and JWT authentication

## 12-Factor App Principles Implementation

1. **Codebase**: One codebase tracked in Git
2. **Dependencies**: Explicitly declared in requirements.txt
3. **Config**: Environment variables for all configuration
4. **Backing Services**: Database treated as attached resource
5. **Build, Release, Run**: Clearly separated stages in Dockerfile
6. **Processes**: Stateless application design
7. **Port Binding**: Self-contained with port configuration
8. **Concurrency**: Horizontally scalable
9. **Disposability**: Fast startup and graceful shutdown
10. **Dev/Prod Parity**: Docker ensures consistency
11. **Logs**: Structured logging to stdout
12. **Admin Processes**: Separate scripts for admin tasks

## Getting Started

### Prerequisites

- Python 3.9+
- Docker and Docker Compose (optional)

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd finance-tracker
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a .env file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

### Using Docker

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

The API will be available at http://localhost:8000

### API Documentation

Once the application is running, you can access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Run tests with pytest:
```bash
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 