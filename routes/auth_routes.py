from fastapi import APIRouter, HTTPException, Request
from datetime import datetime
import bcrypt
from utils.db_utils import users

router = APIRouter()

@router.post("/signup")
async def signup(request: Request):
    data = await request.json()
    email = data.get("email")

    if users.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_pw = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    data["password"] = hashed_pw
    data["itinerary_history"] = []
    data["created_at"] = datetime.now().isoformat()
    users.insert_one(data)
    return {"success": True, "message": "Signup successful"}

@router.post("/login")
async def login(request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    user = users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid password")

    return {"success": True, "message": "Login successful"}
