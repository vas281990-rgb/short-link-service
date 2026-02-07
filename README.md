# URL Shortener 🔗

A simple and fast service for shortening links, built with Python using FastAPI and SQLite.

## Features

- Shorten long URLs into compact links
- Redirect from short links to original URLs
- Create custom short links
- Link click statistics
- Link deletion
- Logging of all operations
- Full test coverage

## Technologies

- **Python 3.12+**
- **FastAPI** - a modern web framework
- **SQLite3** - embedded database (no ORM)
- **Pytest** - testing framework
- **Uvicorn** - ASGI server

## Installation and Setup

### 1. Clone the repository
```bash
git clone https://github.com/vas281990-rgb/short-link-service.git
cd url-shortener
```

### 2. Install dependencies
```bash
pip install -e .
pip install -e ".[dev]"
```

### 3. Run the application
```bash
uvicorn app.main:app --reload
```

The application will be available at: **http://127.0.0.1:8000**

### 4. API Documentation

Open in your browser:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## API Usage

### Shorten a link

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com"}'
```

**Response:**
```json
{
  "short_url": "http://localhost:8000/AbCd12",
  "original_url": "https://www.example.com/"
}
```

### Shorten a link with a custom code

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com", "custom_code": "mylink"}'
```

**Response:**
```json
{
  "short_url": "http://localhost:8000/mylink",
  "original_url": "https://www.example.com/"
}
```

### Access a short link

Simply open it in your browser or use curl:
```bash
curl -L "http://127.0.0.1:8000/AbCd12"
```

You will be automatically redirected to the original URL (HTTP 307)

### Get link statistics

**Request:**
```bash
curl "http://127.0.0.1:8000/stats/AbCd12"
```

**Response:**
```json
{
  "short_code": "AbCd12",
  "original_url": "https://www.example.com/",
  "clicks": 5,
  "created_at": "2026-02-07 05:46:23"
}
```

### Delete a link

**Request:**
```bash
curl -X DELETE "http://127.0.0.1:8000/AbCd12"
```

**Response** HTTP 204 No Content

## Running Tests
```bash
pytest -v
```

To run with code coverage:
```bash
pytest --cov=app --cov-report=html
```

## Project Structure
```
url-shortener/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application and endpoints
│   ├── database.py      # Работа с SQLite database interactions
│   └── config.py        # Configuration and logging
├── tests/
│   ├── __init__.py
│   └── test_api.py      # API tests
├── pyproject.toml       # Project dependencies
├── README.md
└── .gitignore
```

## Database

The application automatically creates a shortener.db file upon the first launch

**Сurls table schema:**

| Колонка      | Тип       | Описание                          |
|--------------|-----------|-----------------------------------|
| id           | INTEGER   | Primary Key                   |
| short_code   | TEXT      | Unique short code (6 characters) |
| original_url | TEXT      | Original long URL         |
| created_at   | TIMESTAMP | Creation date and time          |
| clicks       | INTEGER   | Number of link redirects   |

## Logging

All events are logged to:
- **Console* (stdout)
- **File** `app.log`

Log format:
```
2026-02-07 05:46:23,123 - app.config - INFO - Created short URL: AbCd12 -> https://example.com
```

## HTTP Response Codes

|Code | Description                             |
|-----|---------------------------------------|
| 200 | OK - Successful request                 |
| 201 | Created - Link successfully created     |
| 204 | No Content - Successful deletion     |
| 307 | Temporary Redirect - Redirect to URL  |
| 400 | Bad Request - Invalid request   |
| 404 | Not Found - Link not found        |
| 422 | Validation Error - Data validation error  |
| 500 | Internal Server Error - Server error|

## Implementation Details

- **Short Code Generation**: Uses 6 random characters (letters + digits).
- **Uniqueness**: Checks if a code exists before creation.
- **Atomicity**: All DB operations are transactional.
- **Security**: URL validation via Pydantic.
- **Performance**: Index on the short_code field for fast lookups.

## Future Improvements

1. **Caching** - Redis for frequent redirects.
2. **Analytics** - Detailed stats (referrer, geo, device).
3. **Expiration** - Automatic deletion of old links.
4. **Rate limiting** - Limiting requests per IP.
5. **API keys** - User authentication.
6. **Custom Domains** - Support for branded domains.
7. **QR Codes** - Generate QR codes for links.
8. **Batch Operations** - Bulk link creation.

## License

MIT License

## Author - Anastasiia Polukhina

Created as a technical assessment to demonstrate Python and FastAPI development skills.