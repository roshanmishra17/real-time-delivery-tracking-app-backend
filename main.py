import asyncio
from fastapi import FastAPI
from sqlalchemy.orm import Session
from Service.redis_subscriber import redis_listener
from api import ws_secure_router
from core.redis_client import get_redis
import models.models as models
from database import SessionLocal, engine
from router import agent, auth, location, orders, users,admin_agents,admin_stats
from utils import hash_pass
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

models.Base.metadata.create_all(bind=engine)
redis_task = None 



origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],   # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],   # Authorization, Content-Type, etc.
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(agent.router)
app.include_router(orders.router)
app.include_router(ws_secure_router.router)
app.include_router(location.router)
app.include_router(admin_agents.router)
app.include_router(admin_stats.router)


@app.on_event("startup")
def create_initial_admin():
    db: Session = SessionLocal()
    try:
        # Check if admin already exists
        admin = db.query(models.User).filter(
            models.User.role == models.UserRole.admin
        ).first()

        if not admin:
            hashed_password = hash_pass("roshan123")

            new_admin = models.User(
                name="Admin",
                email="roshanway@gmail.com",
                password=hashed_password,
                role=models.UserRole.admin
            )

            db.add(new_admin)
            db.commit()
            print("Admin user created.")

    except Exception as e:
        print("Error creating admin:", e)

    finally:
        db.close()


@app.on_event("startup")
async def startup_event():
    global redis_task
    redis_task = asyncio.create_task(redis_listener())

@app.on_event("shutdown")
async def shutdown_event():
    global redis_task
    if redis_task:
        redis_task.cancel()

@app.get('/')
def test():
    return {"message" : "Hello world"}  