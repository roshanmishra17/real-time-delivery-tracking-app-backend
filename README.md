# Real-Time Delivery Tracking Backend

Backend service for a real-time delivery tracking application.  
This API handles order management, driver location updates, and streams real-time delivery status using WebSockets and REST endpoints.

## 🚀 Key Features

- User authentication and authorization (JWT)
- REST APIs for orders and delivery management
- Real-time location updates via WebSockets
- Broadcasts delivery status and location to connected clients
- Scalable architecture for live tracking

## 🧰 Tech Stack

- Python
- **FastAPI** — high-performance Python web framework
- Uvicorn — ASGI server
- WebSockets for two-way real-time communication
- PostgreSQL

## 📁 Project Structure
```text
RTDT/
├── api/
│   ├── ws_secure_router.py   # Secure WebSocket routing and access control
│   └── __pycache__/
│
├── App/
│   ├── router/               # Application-level route grouping
│   ├── location_helper.py    # Location-related helper logic
│   ├── oauth.py              # OAuth authentication helpers
│
├── core/
│   ├── distance.py           # Distance and geo-calculation utilities
│   ├── jwt_helper.py         # JWT token creation and validation
│   ├── redis_client.py       # Redis client configuration and connection
│   └── __pycache__/
│
├── models/
│   ├── models.py             # Database models
│   └── __pycache__/
│
├── router/
│   ├── admin_agents.py       # Admin routes for managing delivery agents
│   ├── admin_stats.py        # Admin statistics and analytics routes
│   ├── agent.py              # Delivery agent-related routes
│   ├── auth.py               # Authentication routes
│   ├── location.py           # Location update and tracking routes
│   ├── orders.py             # Order management routes
│   ├── users.py              # User management routes
│   ├── __init__.py
│   └── __pycache__/
│
├── Service/
│   ├── redis_subscriber.py   # Subscribes to Redis Pub/Sub for real-time updates
│   ├── ws_permission.py      # WebSocket authentication and permission checks
│   └── __pycache__/
│
├── ws/
│   ├── manager.py            # WebSocket connection manager
│   └── __pycache__/
│
├── config.py                 # Application configuration
├── database.py               # Database connection and session management
├── enums.py                  # Enum definitions used across the app
├── location_helper.py        # Shared location helper utilities
├── oauth.py                  # Authentication helpers
├── schemas.py                # Pydantic request/response schemas
├── services.py               # Shared service-level abstractions
├── utils.py                  # Common utility functions
├── main.py                   # FastAPI application entry point
│
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not committed)
├── .gitignore                # Git ignore rules
└── venv/                     # Local virtual environment (ignored)

```

## 📌 How to Run Locally
```bash
git clone https://github.com/roshanmishra17/real-time-delivery-tracking-app-backend.git
cd real-time-delivery-tracking-app-backend

python -m venv venv

.\venv\Scripts\activate

pip install -r requirements.txt

uvicorn main:app --reload
```

## API Documentation

Swagger UI is available at:

http://localhost:8000/docs

## Environment Variables

Create a `.env` file in the project root with the following values:

```env
DATABASE_URL=postgresql://user:password@host:port/db
SECRET_KEY=your_secret_key
ALGORITHM=HS256
REDIS_URL=your_redis_url
ACCESS_TOKEN_TIME=60
```

## Author
Roshan Mishra  
BSc Computer Science Student  
Frontend & Backend Developer
GitHub: https://github.com/roshanmishra17
