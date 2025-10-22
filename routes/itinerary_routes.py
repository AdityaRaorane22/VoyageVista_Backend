from fastapi import APIRouter, Request
from utils.db_utils import users
from utils.ai_utils import genai_client
from utils.weather_utils import get_weather
from datetime import datetime
import json

router = APIRouter()


@router.post("/")
async def generate_itinerary(request: Request):
    data = await request.json()
    destination = data.get("destination")
    days = int(data.get("days", 3))
    interests = data.get("interests", "")
    budget = data.get("budget", "moderate")
    meal_preference = data.get("mealPreference", "no-preference")
    user_email = data.get("email")

    if not destination:
        return {"success": False, "error": "Destination is required."}

    weather_data = get_weather(destination)

    user_history = ""
    if user_email:
        user = users.find_one({"email": user_email}, {"_id": 0, "itinerary_history": 1})
        if user and "itinerary_history" in user and len(user["itinerary_history"]) > 0:
            user_history = (
                "\n\nUser's Previous Travel Style: Based on past trips, "
                "the user enjoys personalized experiences."
            )

    prompt = (
        f"Create a detailed {days}-day travel itinerary for {destination} "
        f"for a traveler interested in {interests}. Budget: {budget}, Meal preference: {meal_preference}."
        f"{user_history}"
    )

    try:
        # correct usage
        response = genai_client.generate_text(
            model="gemini-2.0-flash-exp",
            prompt=prompt,
            temperature=0.7,
            max_output_tokens=1024
        )
        itinerary_text = response.output_text

        if user_email:
            itinerary_record = {
                "destination": destination,
                "days": days,
                "interests": interests,
                "budget": budget,
                "itinerary": itinerary_text,
                "created_at": datetime.now().isoformat()
            }
            users.update_one({"email": user_email}, {"$push": {"itinerary_history": itinerary_record}})

        return {"success": True, "itinerary": itinerary_text, "weather": weather_data}

    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/suggested-trips")
async def get_suggested_trips(request: Request):
    data = await request.json()
    user_email = data.get("email")

    user_context = ""
    if user_email:
        user = users.find_one({"email": user_email}, {"_id": 0, "itinerary_history": 1})
        if user and "itinerary_history" in user:
            past_destinations = [trip.get("destination", "") for trip in user["itinerary_history"]]
            if past_destinations:
                user_context = f"\nUser has visited: {', '.join(past_destinations)}"

    prompt = (
        f"Generate 6 diverse travel destination recommendations for a traveler."
        f"{user_context}"
        f"Return only a JSON array of destination names."
    )

    try:
        response = genai_client.generate_text(
            model="gemini-2.0-flash-exp",
            prompt=prompt,
            temperature=0.7,
            max_output_tokens=512
        )
        response_text = response.output_text.strip()

        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]

        try:
            trips = json.loads(response_text)
        except json.JSONDecodeError:
            trips = []

        return {"success": True, "trips": trips}

    except Exception as e:
        return {"success": False, "error": str(e)}
