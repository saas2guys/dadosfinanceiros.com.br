# Django Polygon.io Proxy Service

A high-performance Django REST API proxy service that forwards HTTP requests and WebSocket connections to Polygon.io API with JWT authentication.

## Features

- JWT Authentication
- Async HTTP request forwarding
- WebSocket connection proxying
- Connection pooling
- Redis integration
- Comprehensive logging
- Health checks
- Docker support
- Production-ready configuration

## Prerequisites

- Python 3.8+
- Redis
- UV (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone git@github.com:iklobato/proxy_project.git
cd proxy_project
```

2. Create a virtual environment and install dependencies:
```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

3. Run migrations:
```bash
uv run ./manage.py migrate
```

4. Create a superuser:
```bash
uv run ./manage.py createsuperuser
```

## Configuration

The service uses the following environment variables:
- `POLYGON_API_KEY`: Your Polygon.io API key
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

## Usage

1. Start the development server:
```bash
uv run ./manage.py runserver
```

2. Get a JWT token:
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

3. Use the token to access endpoints:

### REST API Endpoints

- List stocks:
```bash
curl http://localhost:8000/api/v3/stocks/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

- Get stock details:
```bash
curl http://localhost:8000/api/v3/stocks/AAPL/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

- Get stock trades:
```bash
curl http://localhost:8000/api/v3/stocks/AAPL/trades/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

- Generic proxy endpoint:
```bash
curl http://localhost:8000/api/v3/proxy/reference/tickers \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### WebSocket Endpoints

Connect to WebSocket endpoints:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/stocks/?token=YOUR_JWT_TOKEN');
```

## Docker Deployment

1. Build the image:
```bash
docker-compose build
```

2. Start the services:
```bash
docker-compose up -d
```

## Monitoring

- Health check endpoint: `http://localhost:8000/health/`
- Logs are stored in the `logs` directory

## Performance Optimization

The service includes several performance optimizations:
- Async views for high concurrency
- Connection pooling for HTTP and WebSocket connections
- Redis caching
- Streaming responses for large payloads

## Security

- JWT Authentication required for all endpoints
- CORS configuration
- Rate limiting
- Secure headers

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 