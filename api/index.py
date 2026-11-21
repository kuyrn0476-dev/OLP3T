
import os
import secrets
import httpx

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from itsdangerous import URLSafeTimedSerializer, BadSignature

app = FastAPI(title="OL.P3T")

CLIENT_ID = os.environ["1573527625861959762"]
CLIENT_SECRET = os.environ["-MwSf7SFHi3XvUvmRbrEFkqxuUp3bpLL"]
REDIRECT_URI = os.environ["	https://api-orcin-pi.vercel.app/api/discord/callback"]
SESSION_SECRET = os.environ["5428382381122527309546234471220903406239"]

signer = URLSafeTimedSerializer(SESSION_SECRET)

@app.get("/api/health")
def health():
    return {"status": "online", "api": "connected"}

@app.get("/api/discord/login")
def discord_login():
    state = secrets.token_urlsafe(32)
    signed_state = signer.dumps(state, salt="discord-oauth")

    url = (
        "https://discord.com/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        "&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        "&scope=identify"
        f"&state={state}"
    )

    response = RedirectResponse(url)
    response.set_cookie(
        "oauth_state",
        signed_state,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=600
    )
    return response

@app.get("/api/discord/callback")
def discord_callback(request: Request, code: str, state: str):
    signed_state = request.cookies.get("oauth_state")

    if not signed_state:
        raise HTTPException(400, "Missing OAuth state")

    try:
        expected_state = signer.loads(
            signed_state,
            salt="discord-oauth",
            max_age=600
        )
    except BadSignature:
        raise HTTPException(400, "Invalid or expired OAuth state")

    if not secrets.compare_digest(state, expected_state):
        raise HTTPException(400, "OAuth state mismatch")

    token_response = httpx.post(
        "https://discord.com/api/oauth2/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=15
    )
    token_response.raise_for_status()
    access_token = token_response.json()["access_token"]

    profile_response = httpx.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=15
    )
    profile_response.raise_for_status()
    profile = profile_response.json()

    response = JSONResponse({
        "success": True,
        "discord_id": profile["id"],
        "username": profile["username"]
    })
    response.delete_cookie("oauth_state")
    return response
