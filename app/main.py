from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from app.api.endpoints import auth, transactions, categories
from app.core.config import settings
from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.db.init_db import init_db

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize database with default data
try:
    db = SessionLocal()
    init_db(db)
    db.close()
except Exception as e:
    print(f"Error initializing database: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Security scheme for Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(
    transactions.router,
    prefix=f"{settings.API_V1_STR}/transactions",
    tags=["transactions"]
)
app.include_router(
    categories.router,
    prefix=f"{settings.API_V1_STR}/categories",
    tags=["categories"]
)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Finance Tracker API",
        "docs": "/docs",
        "redoc": "/redoc"
    } 