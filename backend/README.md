# CoolCity Planner Backend

AI-powered urban heat island analysis backend using FastAPI, TwelveLabs, Vellum, and Google Gemini.

## Features

- **Satellite Image Analysis**: Upload satellite images for AI-powered urban feature detection
- **TwelveLabs Integration**: Advanced computer vision for identifying buildings, vegetation, surfaces, and infrastructure
- **Urban Heat Risk Assessment**: Analyze heat absorption patterns and urban heat island risks
- **RESTful API**: Clean FastAPI endpoints for frontend integration
- **Background Processing**: Asynchronous image processing with status tracking

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py          # API endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Application configuration
│   │   └── logging.py         # Logging setup
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py         # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   └── twelve_labs_client.py  # TwelveLabs API client
│   └── __init__.py
├── logs/                      # Application logs
├── uploads/                   # Uploaded images
├── static/                    # Static files
├── main.py                    # FastAPI application
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
└── README.md
```

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the example environment file and configure your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
TWELVE_LABS_API_KEY=your_twelve_labs_api_key_here
VELLUM_API_KEY=your_vellum_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
NASA_API_KEY=your_nasa_api_key_here
```

### 3. Run the Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Core Endpoints

- `GET /` - API information
- `GET /health` - Health check with configuration status

### Analysis Endpoints

- `POST /api/upload` - Upload satellite image for analysis
- `GET /api/status/{task_id}` - Check analysis status
- `GET /api/results/{task_id}` - Get analysis results
- `DELETE /api/cleanup/{task_id}` - Clean up task data

### API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Usage Example

### 1. Upload Image

```bash
curl -X POST "http://localhost:8000/api/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@satellite_image.jpg"
```

Response:
```json
{
  "success": true,
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "Image uploaded successfully. Analysis started.",
  "processing_time_estimate": 180
}
```

### 2. Check Status

```bash
curl -X GET "http://localhost:8000/api/status/123e4567-e89b-12d3-a456-426614174000"
```

### 3. Get Results

```bash
curl -X GET "http://localhost:8000/api/results/123e4567-e89b-12d3-a456-426614174000"
```

## Urban Features Detected

The system detects and analyzes:

- **Buildings**: Type (residential/commercial/industrial), height estimates, materials
- **Vegetation**: Parks, trees, green spaces with health scores
- **Surfaces**: Road materials, heat absorption coefficients
- **Infrastructure**: Roads, highways, bridges, parking areas

## Development

### Mock Data Mode

If TwelveLabs API key is not configured, the system will automatically use mock data for testing and development.

### Logging

Application logs are stored in the `logs/` directory:
- `logs/app.log` - Application logs

### Error Handling

The API provides comprehensive error handling with:
- HTTP status codes
- Detailed error messages
- Request validation
- Processing status tracking

## Dependencies

- **FastAPI**: Web framework
- **TwelveLabs**: Computer vision API
- **OpenCV**: Image processing
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server
- **httpx**: Async HTTP client

## License

This project is part of the CoolCity Planner application for urban heat island analysis.
