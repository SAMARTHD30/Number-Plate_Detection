from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis
from app.api.routes import router as api_router

app = FastAPI(
    title="License Plate Detection API",
    description="API for detecting and processing license plates in images",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize rate limiter
@app.on_event("startup")
async def startup():
    redis_client = redis.from_url("redis://localhost", encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_client)

# Include API routes with rate limiting
app.include_router(
    api_router,
    dependencies=[Depends(RateLimiter(times=10, minutes=1))]  # 10 requests per minute
)

@app.get("/")
async def root():
    return {"message": "Welcome to License Plate Detection API"}