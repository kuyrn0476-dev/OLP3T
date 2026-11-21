from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="OL.P3T API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://olp3t-damion-7429.vercel.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

@app.get("/")
def home():
    return {"service": "OL.P3T", "status": "online"}

@app.get("/api/health")
def health():
    return {"status": "online", "api": "connected"}

