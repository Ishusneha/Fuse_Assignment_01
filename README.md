# Finance Tracker API

A FastAPI-based microservice for tracking personal finances, implementing 12-Factor app principles.

## Features

- User authentication with JWT tokens
- Transaction management (income/expenses)
- Category management
- Financial summaries and reports
- SQLite database (configurable for PostgreSQL)
- Docker containerization
- Comprehensive test suite

## Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Git

## Local Development Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd finance-tracker
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Alternative Documentation: http://localhost:8000/redoc

## Docker Setup

1. Build and run using Docker Compose:
```bash
docker-compose up --build
```

The API will be available at http://localhost:8000

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | Database connection string | sqlite:///./finance_tracker.db |
| SECRET_KEY | JWT secret key | your-secret-key-here |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token expiration time | 30 |
| EXCHANGE_RATE_API_KEY | API key for currency conversion | None |

## Project Structure

```
finance-tracker/
├── app/
│   ├── api/
│   │   └── endpoints/
│   ├── core/
│   ├── db/
│   ├── models/
│   └── schemas/
├── tests/
├── docker/
├── .env
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Testing

Run tests using pytest:
```bash
pytest
```

For test coverage:
```bash
pytest --cov=app tests/
```

## API Endpoints

### Authentication
- POST `/auth/register` - Register new user
- POST `/auth/token` - Login and get access token

### Transactions
- GET `/api/v1/transactions/` - List transactions
- POST `/api/v1/transactions/` - Create transaction
- GET `/api/v1/transactions/{id}` - Get transaction details
- PUT `/api/v1/transactions/{id}` - Update transaction
- DELETE `/api/v1/transactions/{id}` - Delete transaction

### Categories
- GET `/api/v1/categories/` - List categories
- POST `/api/v1/categories/` - Create category
- GET `/api/v1/categories/{id}` - Get category details

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 