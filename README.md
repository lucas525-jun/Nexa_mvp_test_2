# Nexa Task Manager - Technical Validation Test #2

**Author:** Lucas Song

A production-ready operational core MVP that demonstrates the complete Nexa workflow: Order Creation → Master Assignment → ADL Attachment → Order Completion.

## Features

- **Order Management**: Create and track service orders with location-based routing
- **Smart Master Assignment**: Intelligent algorithm based on distance, rating, and current load
- **ADL Enforcement**: Strict validation requiring GPS coordinates and timestamps before order completion
- **Haversine Distance**: Accurate distance calculation for proximity-based assignment
- **Modular Architecture**: Clean separation of concerns across routes, controllers, services, and repositories
- **SQLite Database**: Lightweight, zero-config persistence
- **RESTful API**: Complete JSON API with FastAPI and automatic OpenAPI documentation

## Architecture

```
nexa-master/
├── app/
│   ├── controllers/       # Request handlers
│   ├── services/          # Business logic (assignment algorithm, ADL validation)
│   ├── repositories/      # Data access layer
│   ├── models/            # SQLAlchemy models
│   ├── routes/            # API endpoints
│   ├── schemas/           # Pydantic request/response schemas
│   ├── database/          # Database configuration
│   ├── utils/             # Haversine distance helper
│   └── main.py            # FastAPI application
├── tests/                 # Unit tests
├── requirements.txt
└── README.md
```

## Data Model

### Master
```json
{
  "id": 1,
  "name": "John Smith",
  "rating": 4.5,
  "isAvailable": true,
  "geo": {
    "lat": 40.7128,
    "lng": -74.0060
  },
  "currentLoad": 2
}
```

### Order
```json
{
  "id": 1,
  "title": "Fix plumbing issue",
  "description": "Kitchen sink is leaking",
  "status": "assigned",
  "customer": {
    "name": "Jane Doe",
    "phone": "+1234567890"
  },
  "geo": {
    "lat": 40.7128,
    "lng": -74.0060
  },
  "assignedMasterId": 1,
  "createdAt": "2025-10-16T14:30:00",
  "updatedAt": "2025-10-16T14:35:00"
}
```

### ADL Media
```json
{
  "id": 1,
  "orderId": 1,
  "type": "photo",
  "url": "/uploads/order_1_photo.jpg",
  "gps": {
    "lat": 40.7128,
    "lng": -74.0060
  },
  "capturedAt": "2025-10-16T14:45:00Z",
  "meta": {
    "device": "iPhone 14",
    "fileSize": "2.5MB"
  }
}
```

## Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
# Clone or navigate to the nexa-master directory
cd nexa-master

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Database Initialization

The application automatically:
1. Creates SQLite database (`nexa_test2.db`) on startup
2. Creates all required tables
3. Seeds 5 sample masters with different locations and ratings

## Quick Demo - Complete Workflow

This section demonstrates the full workflow with **both successful and failing scenarios** to showcase ADL enforcement.

### Success Path (Full Workflow)

```bash
# 1. Create an order
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Fix plumbing issue",
    "description": "Kitchen sink is leaking",
    "customer": {"name": "Jane Doe", "phone": "+1234567890"},
    "geo": {"lat": 40.7128, "lng": -74.0060}
  }'
# Response: {"id": 1, "status": "new", ...}

# 2. Assign best available master (automatic selection)
curl -X POST http://localhost:8000/api/v1/orders/1/assign
# Response: {"id": 1, "status": "assigned", "assignedMasterId": 2, ...}

# 3. Attach ADL media with GPS and timestamp
curl -X POST http://localhost:8000/api/v1/orders/1/adl \
  -H "Content-Type: application/json" \
  -d '{
    "type": "photo",
    "url": "/uploads/order_1_photo.jpg",
    "gps": {"lat": 40.7128, "lng": -74.0060},
    "capturedAt": "2025-10-20T14:45:00Z",
    "meta": {"device": "iPhone 14"}
  }'
# Response: {"id": 1, "orderId": 1, "type": "photo", ...}

# 4. Complete the order (requires valid ADL)
curl -X POST http://localhost:8000/api/v1/orders/1/complete
# Response: {"id": 1, "status": "completed", ...}

# 5. View all masters with their current load
curl http://localhost:8000/api/v1/masters
# Response: [{"id": 1, "name": "John Smith", "currentLoad": 0, ...}, ...]
```

### Failure Scenarios - ADL Enforcement

#### ❌ Scenario 1: Complete Order Without ADL

```bash
# Create and assign order
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "geo": {"lat": 40.7128, "lng": -74.0060}}'
# Response: {"id": 2, "status": "new", ...}

curl -X POST http://localhost:8000/api/v1/orders/2/assign
# Response: {"id": 2, "status": "assigned", ...}

# Try to complete WITHOUT attaching ADL - FAILS
curl -X POST http://localhost:8000/api/v1/orders/2/complete
# Response: 400 Bad Request
# {"detail": "Cannot complete order: valid ADL media with GPS coordinates and timestamp is required"}
```

#### ❌ Scenario 2: ADL Missing GPS Latitude

```bash
curl -X POST http://localhost:8000/api/v1/orders/2/adl \
  -H "Content-Type: application/json" \
  -d '{
    "type": "photo",
    "url": "/uploads/photo.jpg",
    "gps": {"lng": -74.0060},
    "capturedAt": "2025-10-20T14:45:00Z"
  }'
# Response: 400 Bad Request
# {"detail": "GPS coordinates (gps_lat, gps_lng) are required"}
```

#### ❌ Scenario 3: ADL Missing GPS Longitude

```bash
curl -X POST http://localhost:8000/api/v1/orders/2/adl \
  -H "Content-Type: application/json" \
  -d '{
    "type": "photo",
    "url": "/uploads/photo.jpg",
    "gps": {"lat": 40.7128},
    "capturedAt": "2025-10-20T14:45:00Z"
  }'
# Response: 400 Bad Request
# {"detail": "GPS coordinates (gps_lat, gps_lng) are required"}
```

#### ❌ Scenario 4: ADL Missing Timestamp

```bash
curl -X POST http://localhost:8000/api/v1/orders/2/adl \
  -H "Content-Type: application/json" \
  -d '{
    "type": "photo",
    "url": "/uploads/photo.jpg",
    "gps": {"lat": 40.7128, "lng": -74.0060}
  }'
# Response: 400 Bad Request
# {"detail": "Timestamp (captured_at) is required in ISO format"}
```

### ADL Requirements Summary

| Field | Required | Validation | Error (400) |
|-------|----------|------------|-------------|
| `gps.lat` | ✅ Yes | Must be present | "GPS coordinates (gps_lat, gps_lng) are required" |
| `gps.lng` | ✅ Yes | Must be present | "GPS coordinates (gps_lat, gps_lng) are required" |
| `capturedAt` | ✅ Yes | ISO timestamp | "Timestamp (captured_at) is required in ISO format" |
| `type` | ✅ Yes | "photo" or "video" | Pydantic validation error |
| `url` | ✅ Yes | Non-empty string | Pydantic validation error |
| `meta` | ❌ No | Optional dictionary | N/A |

## API Endpoints

### Base URL
```
http://localhost:8000/api/v1
```

### 1. Create Order
**POST** `/api/v1/orders`

Create a new order in the system.

**Request Body:**
```json
{
  "title": "Fix plumbing issue",
  "description": "Kitchen sink is leaking",
  "customer": {
    "name": "Jane Doe",
    "phone": "+1234567890"
  },
  "geo": {
    "lat": 40.7128,
    "lng": -74.0060
  }
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "title": "Fix plumbing issue",
  "description": "Kitchen sink is leaking",
  "status": "new",
  "customer": {
    "name": "Jane Doe",
    "phone": "+1234567890"
  },
  "geo": {
    "lat": 40.7128,
    "lng": -74.0060
  },
  "assignedMasterId": null,
  "createdAt": "2025-10-16T14:30:00",
  "updatedAt": "2025-10-16T14:30:00"
}
```

### 2. Assign Master to Order
**POST** `/api/v1/orders/{order_id}/assign`

Automatically assigns the best available master based on:
1. **Nearest distance** (Haversine formula)
2. **Higher rating** (tiebreaker if distances are close)
3. **Lower current load** (tiebreaker if ratings are close)

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Fix plumbing issue",
  "status": "assigned",
  "assignedMasterId": 2,
  "assignedMaster": {
    "id": 2,
    "name": "Maria Garcia",
    "rating": 4.8,
    "isAvailable": true,
    "geo": {
      "lat": 40.7589,
      "lng": -73.9851
    }
  },
  ...
}
```

### 3. Attach ADL Media
**POST** `/api/v1/orders/{order_id}/adl`

Attach photo or video evidence with GPS and timestamp.

**Request Body:**
```json
{
  "type": "photo",
  "url": "/uploads/order_1_photo.jpg",
  "gps": {
    "lat": 40.7128,
    "lng": -74.0060
  },
  "capturedAt": "2025-10-16T14:45:00Z",
  "meta": {
    "device": "iPhone 14",
    "fileSize": "2.5MB"
  }
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "orderId": 1,
  "type": "photo",
  "url": "/uploads/order_1_photo.jpg",
  "gps": {
    "lat": 40.7128,
    "lng": -74.0060
  },
  "capturedAt": "2025-10-16T14:45:00Z",
  "meta": {
    "device": "iPhone 14",
    "fileSize": "2.5MB"
  }
}
```

### 4. Complete Order
**POST** `/api/v1/orders/{order_id}/complete`

Mark order as completed. **Requires valid ADL with GPS and timestamp.**

**Response (200 OK):**
```json
{
  "id": 1,
  "status": "completed",
  ...
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "Cannot complete order: valid ADL media with GPS coordinates and timestamp is required"
}
```

### 5. Get Order
**GET** `/api/v1/orders/{order_id}`

Retrieve full order with assigned master and ADL media.

**Example Request:**
```bash
curl http://localhost:8000/api/v1/orders/1
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Fix plumbing issue",
  "description": "Kitchen sink is leaking",
  "status": "completed",
  "customer": {
    "name": "Jane Doe",
    "phone": "+1234567890"
  },
  "geo": {
    "lat": 40.7128,
    "lng": -74.0060
  },
  "assignedMasterId": 2,
  "assignedMaster": {
    "id": 2,
    "name": "Maria Garcia",
    "rating": 4.8,
    "isAvailable": true,
    "geo": {
      "lat": 40.7589,
      "lng": -73.9851
    },
    "currentLoad": 3
  },
  "adlMedia": [
    {
      "id": 1,
      "orderId": 1,
      "type": "photo",
      "url": "/uploads/order_1_photo.jpg",
      "gps": {
        "lat": 40.7128,
        "lng": -74.0060
      },
      "capturedAt": "2025-10-16T14:45:00Z",
      "meta": {
        "device": "iPhone 14",
        "fileSize": "2.5MB"
      }
    }
  ],
  "createdAt": "2025-10-16T14:30:00",
  "updatedAt": "2025-10-16T14:50:00"
}
```

### 6. Get All Masters
**GET** `/api/v1/masters`

List all masters with availability and current load.

**Example Request:**
```bash
curl http://localhost:8000/api/v1/masters
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "John Smith",
    "rating": 4.5,
    "isAvailable": true,
    "geo": {
      "lat": 40.7128,
      "lng": -74.0060
    },
    "currentLoad": 2
  },
  {
    "id": 2,
    "name": "Maria Garcia",
    "rating": 4.8,
    "isAvailable": true,
    "geo": {
      "lat": 40.7589,
      "lng": -73.9851
    },
    "currentLoad": 1
  }
]
```

## Complete Workflow Example

### Using cURL

```bash
# 1. Create an order
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Fix electrical wiring",
    "description": "Outlet not working",
    "customer": {"name": "John Doe", "phone": "+1234567890"},
    "geo": {"lat": 40.7128, "lng": -74.0060}
  }'

# Save the order ID from response (e.g., 1)

# 2. Assign master to order
curl -X POST http://localhost:8000/api/v1/orders/1/assign

# 3. Attach ADL media
curl -X POST http://localhost:8000/api/v1/orders/1/adl \
  -H "Content-Type: application/json" \
  -d '{
    "type": "photo",
    "url": "/uploads/order_1_photo.jpg",
    "gps": {"lat": 40.7128, "lng": -74.0060},
    "capturedAt": "2025-10-16T14:45:00Z",
    "meta": {"device": "iPhone"}
  }'

# 4. Complete the order
curl -X POST http://localhost:8000/api/v1/orders/1/complete

# 5. View the completed order
curl http://localhost:8000/api/v1/orders/1
```

### Using Python

```python
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

# 1. Create order
response = requests.post(f"{BASE_URL}/orders", json={
    "title": "Fix electrical wiring",
    "description": "Outlet not working",
    "customer": {"name": "John Doe", "phone": "+1234567890"},
    "geo": {"lat": 40.7128, "lng": -74.0060}
})
order = response.json()
order_id = order["id"]
print(f"Order created: {order_id}")

# 2. Assign master
response = requests.post(f"{BASE_URL}/orders/{order_id}/assign")
print(f"Master assigned: {response.json()['assignedMasterId']}")

# 3. Attach ADL
response = requests.post(f"{BASE_URL}/orders/{order_id}/adl", json={
    "type": "photo",
    "url": "/uploads/photo.jpg",
    "gps": {"lat": 40.7128, "lng": -74.0060},
    "capturedAt": datetime.utcnow().isoformat() + "Z",
    "meta": {"device": "iPhone"}
})
print(f"ADL attached: {response.json()['id']}")

# 4. Complete order
response = requests.post(f"{BASE_URL}/orders/{order_id}/complete")
print(f"Order completed: {response.json()['status']}")

# 5. Get full order details
response = requests.get(f"{BASE_URL}/orders/{order_id}")
print(response.json())
```

## Master Assignment Algorithm

The system uses a multi-criteria selection algorithm:

```python
def find_best_master(order_lat, order_lng):
    # Get all available masters
    # For each master:
    #   - Calculate Haversine distance to order
    #   - Get current load (active orders)

    # Sort by:
    #   1. Distance (ascending) - nearest first
    #   2. Rating (descending) - higher rating wins ties
    #   3. Load (ascending) - lower load wins final ties

    return best_master_id
```

## ADL Validation & Enforcement

Before an order can be completed, the system enforces strict ADL requirements:
- ✅ At least one ADL media must be attached
- ✅ ADL must have valid GPS coordinates (lat, lng)
- ✅ ADL must have valid timestamp (capturedAt in ISO format)
- ❌ Otherwise, completion fails with 400 error

### ADL Enforcement Examples

#### Scenario 1: Complete Order Without ADL (FAILS)

```bash
# Create and assign order
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Order", "customer": {"name": "John"}, "geo": {"lat": 40.7128, "lng": -74.0060}}'
# Returns: {"id": 1, ...}

curl -X POST http://localhost:8000/api/v1/orders/1/assign
# Returns: {"id": 1, "assignedMasterId": 2, ...}

# Try to complete without ADL
curl -X POST http://localhost:8000/api/v1/orders/1/complete
```

**Response (400 Bad Request):**
```json
{
  "detail": "Cannot complete order: valid ADL media with GPS coordinates and timestamp is required"
}
```

#### Scenario 2: Attach ADL Missing GPS Coordinates (FAILS)

```bash
# Try to attach ADL without GPS
curl -X POST http://localhost:8000/api/v1/orders/1/adl \
  -H "Content-Type: application/json" \
  -d '{
    "type": "photo",
    "url": "/uploads/photo.jpg",
    "capturedAt": "2025-10-16T14:45:00Z"
  }'
```

**Response (400 Bad Request):**
```json
{
  "detail": "GPS coordinates (gps_lat, gps_lng) are required"
}
```

#### Scenario 3: Attach ADL Missing Latitude Only (FAILS)

```bash
# Try to attach ADL with incomplete GPS (missing lat)
curl -X POST http://localhost:8000/api/v1/orders/1/adl \
  -H "Content-Type: application/json" \
  -d '{
    "type": "photo",
    "url": "/uploads/photo.jpg",
    "gps": {"lng": -74.0060},
    "capturedAt": "2025-10-16T14:45:00Z"
  }'
```

**Response (400 Bad Request):**
```json
{
  "detail": "GPS coordinates (gps_lat, gps_lng) are required"
}
```

#### Scenario 4: Attach ADL Missing Longitude Only (FAILS)

```bash
# Try to attach ADL with incomplete GPS (missing lng)
curl -X POST http://localhost:8000/api/v1/orders/1/adl \
  -H "Content-Type: application/json" \
  -d '{
    "type": "photo",
    "url": "/uploads/photo.jpg",
    "gps": {"lat": 40.7128},
    "capturedAt": "2025-10-16T14:45:00Z"
  }'
```

**Response (400 Bad Request):**
```json
{
  "detail": "GPS coordinates (gps_lat, gps_lng) are required"
}
```

#### Scenario 5: Attach ADL Missing Timestamp (FAILS)

```bash
# Try to attach ADL without capturedAt
curl -X POST http://localhost:8000/api/v1/orders/1/adl \
  -H "Content-Type: application/json" \
  -d '{
    "type": "photo",
    "url": "/uploads/photo.jpg",
    "gps": {"lat": 40.7128, "lng": -74.0060}
  }'
```

**Response (400 Bad Request):**
```json
{
  "detail": "Timestamp (captured_at) is required in ISO format"
}
```

#### Scenario 6: Complete Order With Valid ADL (SUCCESS)

```bash
# Attach ADL with all required fields
curl -X POST http://localhost:8000/api/v1/orders/1/adl \
  -H "Content-Type: application/json" \
  -d '{
    "type": "photo",
    "url": "/uploads/order_1_photo.jpg",
    "gps": {"lat": 40.7128, "lng": -74.0060},
    "capturedAt": "2025-10-16T14:45:00Z",
    "meta": {"device": "iPhone 14"}
  }'
# Returns: {"id": 1, "orderId": 1, ...}

# Now complete the order
curl -X POST http://localhost:8000/api/v1/orders/1/complete
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Test Order",
  "status": "completed",
  "customer": {"name": "John"},
  "geo": {"lat": 40.7128, "lng": -74.0060},
  "assignedMasterId": 2,
  "assignedMaster": {...},
  "adlMedia": [
    {
      "id": 1,
      "orderId": 1,
      "type": "photo",
      "url": "/uploads/order_1_photo.jpg",
      "gps": {"lat": 40.7128, "lng": -74.0060},
      "capturedAt": "2025-10-16T14:45:00Z",
      "meta": {"device": "iPhone 14"}
    }
  ],
  "createdAt": "2025-10-16T14:30:00",
  "updatedAt": "2025-10-16T14:50:00"
}
```

### Summary: ADL Requirements

| Field | Required | Validation | Error Message |
|-------|----------|------------|---------------|
| `gps.lat` | ✅ Yes | Must be present | "GPS coordinates (gps_lat, gps_lng) are required" |
| `gps.lng` | ✅ Yes | Must be present | "GPS coordinates (gps_lat, gps_lng) are required" |
| `capturedAt` | ✅ Yes | Must be valid ISO timestamp | "Timestamp (captured_at) is required in ISO format" |
| `type` | ✅ Yes | Must be "photo" or "video" | Pydantic validation error |
| `url` | ✅ Yes | Must be non-empty string | Pydantic validation error |
| `meta` | ❌ No | Optional dictionary | N/A |

**All three core fields (gps.lat, gps.lng, capturedAt) must be present for order completion to succeed.**

## Running Tests

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=term-missing
```

## Project Structure Details

### Layers

1. **Routes** (`app/routes/`): Define API endpoints and HTTP methods
2. **Controllers** (`app/controllers/`): Handle requests, validate input
3. **Services** (`app/services/`): Business logic (assignment, validation)
4. **Repositories** (`app/repositories/`): Database operations
5. **Models** (`app/models/`): SQLAlchemy ORM models
6. **Schemas** (`app/schemas/`): Pydantic validation models

### Key Files

- `app/utils/distance.py`: Haversine distance calculation
- `app/database/config.py`: Database setup and seeding
- `app/services/order_service.py`: Order lifecycle management
- `app/services/master_service.py`: Master assignment algorithm

## Technologies Used

- **FastAPI** 0.109.0 - Modern async web framework
- **SQLAlchemy** 2.0.25 - ORM for database operations
- **Pydantic** 2.5.3 - Data validation
- **Uvicorn** 0.27.0 - ASGI server
- **SQLite** - Embedded database
- **Python** 3.9+

## Design Decisions

1. **SQLite over PostgreSQL**: Simpler setup for validation phase, easy to run locally
2. **Synchronous SQLAlchemy**: Adequate for SQLite, simpler than async
3. **Modular Architecture**: Clear separation enables easy testing and maintenance
4. **Haversine Distance**: Accurate geographic distance without external APIs
5. **Strict ADL Validation**: Ensures data integrity before order completion
6. **Sample Data Seeding**: Enables immediate testing without manual setup

## Security

### Current State
This MVP is designed for **technical validation and testing purposes**. The following security considerations apply:

- **No Authentication**: The API is currently open. For production, implement JWT-based authentication or OAuth 2.0.
- **CORS Enabled**: All origins are allowed (`allow_origins=["*"]`). Restrict this to specific domains in production.
- **No Rate Limiting**: Implement rate limiting to prevent abuse in production environments.
- **Environment Variables**: Use `.env` files for configuration (already in `.gitignore`). Never commit secrets.

### Best Practices for Development

1. **Secrets Management**: Never commit API keys, tokens, or credentials to Git. Use environment variables and `.env` files.
2. **Pre-commit Hooks**: The project includes `detect-private-key` hook to prevent accidental commits of secrets.
3. **CI/CD Secrets**: GitHub Actions secrets are properly used for `CODECOV_TOKEN` (see `.github/workflows/ci.yml`).
4. **Database**: SQLite database files (`*.db`) are excluded in `.gitignore`.

### Production Checklist (Future)

When deploying to production:
- [ ] Add authentication and authorization (JWT, OAuth 2.0)
- [ ] Restrict CORS to specific allowed origins
- [ ] Implement rate limiting and request throttling
- [ ] Use HTTPS for all endpoints
- [ ] Add input sanitization and validation
- [ ] Implement audit logging for sensitive operations
- [ ] Use environment-based configuration with secrets management (AWS Secrets Manager, HashiCorp Vault, etc.)

## Future Enhancements

- Real-time master location tracking
- WebSocket notifications for order updates
- File upload support for ADL media
- Authentication and authorization
- Order history and analytics
- Master availability scheduling
- Rate limiting and API throttling

## License

This project is created for Nexa technical validation purposes.
