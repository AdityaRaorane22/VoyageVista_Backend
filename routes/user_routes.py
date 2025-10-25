from fastapi import APIRouter, HTTPException, Request
from utils.db_utils import users

router = APIRouter()

@router.get("/{email}")
def get_user(email: str):
    user = users.find_one({"email": email}, {"_id": 0, "password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/update")
async def update_user(request: Request):
    data = await request.json()
    email = data.get("email")
    updates = {k: v for k, v in data.items() if k != "email" and v is not None}
    users.update_one({"email": email}, {"$set": updates})
    return {"success": True, "message": "Profile updated successfully"}

@router.get("/stats/{email}")
def get_user_stats(email: str):
    user = users.find_one({"email": email}, {"_id": 0, "itinerary_history": 1})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    history = user.get("itinerary_history", [])
    total_trips = len(history)
    total_days = sum([int(trip.get("days", 0)) for trip in history])
    destinations = [trip.get("destination", "") for trip in history]

    return {
        "success": True,
        "stats": {
            "totalTrips": total_trips,
            "totalDays": total_days,
            "destinations": destinations,
            "recentTrip": history[-1] if history else None
        }
    }



@router.get("-stats/{email}")
def get_user_stats_compat(email: str):
    user = users.find_one({"email": email}, {"_id": 0, "itinerary_history": 1})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    history = user.get("itinerary_history", [])
    total_trips = len(history)
    total_days = sum([int(trip.get("days", 0)) for trip in history])
    destinations = [trip.get("destination", "") for trip in history]
    return {
        "success": True,
        "stats": {
            "totalTrips": total_trips,
            "totalDays": total_days,
            "destinations": destinations,
            "recentTrip": history[-1] if history else None
        }
    }
