"""Parista FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.modules.chat import routes  # noqa: F401  (registers routes on startup)

app = FastAPI(
    title="Parista API",
    description="Grounded conflict analysis assistant",
    version="0.1.0",
)

# CORS for the React frontend (Vercel/Netlify deploy)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict to frontend origin in production
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (chat routes will be added in US1+)
app.include_router(routes.router, prefix="/api")