# FastAPI Example Application

A simple FastAPI application for GitHub Actions testing and development.

## Features

- Basic CRUD-like operations for items
- Health check endpoint
- In-memory storage (resets on server restart)

## Setup

1. Clone the repository
2. Make the startup script executable:
   ```bash
   chmod +x startup.sh
   ```
3. Run the startup script (it will handle the virtual environment setup):
   ```bash
   ./startup.sh
   ```
   The first time you run this, it will:
   - Create a Python virtual environment
   - Install all required dependencies
   - Start the FastAPI development server

   On subsequent runs, it will simply activate the existing virtual environment and start the server.

## Running the Application

Start the development server:

```bash
uvicorn main:app --reload
```

The application will be available at `http://127.0.0.1:8000`

## API Endpoints

- `GET /`: Welcome message
- `GET /health`: Health check endpoint
- `GET /items/{item_id}`: Get an item by ID
- `POST /items/`: Create a new item

## API Documentation

- Interactive API docs (Swagger UI): `http://127.0.0.1:8000/docs`
- Alternative API docs (ReDoc): `http://127.0.0.1:8000/redoc`

## Example Usage

Create a new item:
```bash
curl -X POST "http://127.0.0.1:8000/items/" \
  -H "Content-Type: application/json" \
  -d '{"name":"Example Item","description":"This is an example","price":9.99}'
```

Get an item:
```bash
curl "http://127.0.0.1:800x/items/1"
```