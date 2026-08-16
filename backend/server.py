from fastapi import FastAPI, APIRouter, Header, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import httpx


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

EMERGENT_AUTH_SESSION_URL = os.environ.get(
    'EMERGENT_AUTH_SESSION_URL',
    'https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data',
)
SESSION_TTL_DAYS = 7

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StatusCheckCreate(BaseModel):
    client_name: str


class SessionRequest(BaseModel):
    session_id: str


class PublicUser(BaseModel):
    user_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None
    auth_provider: str = "google"


class SessionResponse(BaseModel):
    session_token: str
    user: PublicUser


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _aware(dt: datetime) -> datetime:
    """Normalise a possibly-naive datetime (Mongo can return naive) to UTC-aware."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


async def _current_user(authorization: Optional[str]) -> dict:
    """Validate a Bearer session_token and return the user document.

    Raises 401 for any missing/invalid/expired session. We never re-verify the
    token against the Emergent API -- the session row is the source of truth.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Empty bearer token")

    session = await db.user_sessions.find_one({"session_token": token}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")

    if _aware(session["expires_at"]) < datetime.now(timezone.utc):
        await db.user_sessions.delete_one({"session_token": token})
        raise HTTPException(status_code=401, detail="Session expired")

    user = await db.users.find_one({"user_id": session["user_id"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@api_router.get("/")
async def root():
    return {"message": "NASUKI API", "status": "ok"}


@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_obj = StatusCheck(**input.dict())
    await db.status_checks.insert_one(status_obj.dict())
    return status_obj


@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    return [StatusCheck(**s) for s in status_checks]


@api_router.post("/auth/session", response_model=SessionResponse)
async def create_session(payload: SessionRequest):
    """Exchange a one-time Emergent `session_id` for a 7-day `session_token`.

    This is the ONLY place the backend talks to the Emergent auth API. The
    frontend must never call the Emergent endpoint directly.
    """
    session_id = (payload.session_id or "").strip()
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id required")

    try:
        async with httpx.AsyncClient(timeout=15.0) as http:
            resp = await http.get(
                EMERGENT_AUTH_SESSION_URL,
                headers={"X-Session-ID": session_id},
            )
    except httpx.HTTPError as exc:
        logger.error("Emergent session-data request failed: %s", type(exc).__name__)
        raise HTTPException(status_code=502, detail="Auth provider unavailable")

    if resp.status_code != 200:
        # Invalid / expired / already-used session_id.
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    data = resp.json()
    email = data.get("email")
    name = data.get("name")
    picture = data.get("picture")
    session_token = data.get("session_token")
    if not session_token or not email:
        raise HTTPException(status_code=401, detail="Incomplete auth response")

    now = datetime.now(timezone.utc)

    # Upsert user by email -- reuse the existing user_id, never duplicate.
    existing = await db.users.find_one({"email": email}, {"_id": 0})
    if existing:
        user_id = existing["user_id"]
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"name": name, "picture": picture, "updated_at": now}},
        )
    else:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        await db.users.insert_one(
            {
                "user_id": user_id,
                "email": email,
                "name": name,
                "picture": picture,
                "auth_provider": "google",
                "created_at": now,
                "updated_at": now,
            }
        )

    await db.user_sessions.insert_one(
        {
            "session_token": session_token,
            "user_id": user_id,
            "created_at": now,
            "expires_at": now + timedelta(days=SESSION_TTL_DAYS),
        }
    )

    return SessionResponse(
        session_token=session_token,
        user=PublicUser(
            user_id=user_id, email=email, name=name, picture=picture, auth_provider="google"
        ),
    )


@api_router.get("/auth/me", response_model=PublicUser)
async def get_me(authorization: Optional[str] = Header(default=None)):
    user = await _current_user(authorization)
    return PublicUser(
        user_id=user["user_id"],
        email=user.get("email"),
        name=user.get("name"),
        picture=user.get("picture"),
        auth_provider=user.get("auth_provider", "google"),
    )


@api_router.post("/auth/logout")
async def logout(authorization: Optional[str] = Header(default=None)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1].strip()
        if token:
            await db.user_sessions.delete_one({"session_token": token})
    return {"ok": True}


# Include the router in the main app
app.include_router(api_router)

_cors_origins = os.environ.get("CORS_ORIGINS", "*")
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[o.strip() for o in _cors_origins.split(",")] if _cors_origins != "*" else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@app.on_event("startup")
async def create_indexes():
    try:
        await db.users.create_index("email", unique=True, sparse=True)
        await db.users.create_index("user_id", unique=True)
        await db.user_sessions.create_index("session_token", unique=True)
        await db.user_sessions.create_index("user_id")
        await db.user_sessions.create_index("expires_at", expireAfterSeconds=0)
        logger.info("Mongo indexes ensured")
    except Exception as exc:  # pragma: no cover
        logger.error("Index creation failed: %s", exc)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
