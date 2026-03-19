# Travel Planner API

A backend service built with FastAPI and SQLite to manage travel projects and places, integrated with the Art Institute of Chicago API.

## Features
- **Projects**: Create, read, update, and delete travel projects.
- **Places**: Add places (artworks) from the Art Institute to projects. Validates existence via external API.
- **Limits**: Maximum 10 places per project.
- **Caching**: Results from the Art Institute API are cached to minimize external load.
- **Authentication**: Basic Authentication implemented (use `admin` and `secret`).

## Setup and Running

### Using Docker
1. Ensure Docker and Docker Compose are installed.
2. Build and run the container:
   ```bash
   docker-compose up --build
   ```
3. The API will be available at `http://localhost:8000`.

### Local Setup
1. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation
Once the application is running, Swagger UI is available at:
`http://localhost:8000/docs`

## Postman Collection
A fully configured Postman collection is included in the repository:
`postman_collection.json`
Import this file into Postman to test the endpoints. Note that it uses Basic Auth configured at the collection level (credentials: `admin` / `secret`).
