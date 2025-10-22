# main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from dotenv import load_dotenv
import os, bcrypt
from google import genai
import requests
from datetime import datetime

load_dotenv()

app = FastAPI()

# Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["voyage_vista"]
users = db["users"]

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
genai_client = genai.Client(api_key=GEMINI_API_KEY)


@app.get("/")
def home():
    return {"message": "VoyageVista Backend is running 🚀"}


@app.post("/signup")
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


@app.post("/login")
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


@app.get("/user/{email}")
def get_user(email: str):
    user = users.find_one({"email": email}, {"_id": 0, "password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/user/update")
async def update_user(request: Request):
    data = await request.json()
    email = data.get("email")
    updates = {k: v for k, v in data.items() if k != "email" and v is not None}
    users.update_one({"email": email}, {"$set": updates})
    return {"success": True, "message": "Profile updated successfully"}


def get_weather(destination):
    """Fetch weather data from OpenWeatherMap API"""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={destination}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "temp": round(data["main"]["temp"]),
                "humidity": data["main"]["humidity"],
                "condition": data["weather"][0]["main"],
                "windSpeed": round(data["wind"]["speed"] * 3.6)  # Convert m/s to km/h
            }
    except Exception as e:
        print(f"Weather API error: {e}")
    return None


@app.post("/itinerary")
async def generate_itinerary(request: Request):
    data = await request.json()
    destination = data.get("destination")
    days = data.get("days")
    interests = data.get("interests")
    budget = data.get("budget", "moderate")
    meal_preference = data.get("mealPreference", "no-preference")
    user_email = data.get("email")

    # Fetch weather information
    weather_data = get_weather(destination)

    # Get user history for context
    user_history = ""
    if user_email:
        user = users.find_one({"email": user_email}, {"_id": 0, "itinerary_history": 1})
        if user and "itinerary_history" in user and len(user["itinerary_history"]) > 0:
            last_trips = user["itinerary_history"][-3:]  # Last 3 trips
            user_history = "\n\nUser's Previous Travel Style: Based on past trips, the user enjoys personalized experiences."

    # Budget mapping
    budget_details = {
        "budget": "Budget-friendly options (₹5,000-15,000/day). Focus on affordable accommodations, local transport, street food, and free/low-cost attractions.",
        "moderate": "Moderate budget (₹15,000-35,000/day). Mix of comfort hotels, mid-range restaurants, guided tours, and popular attractions.",
        "luxury": "Luxury experience (₹35,000+/day). Premium hotels, fine dining, private tours, spa experiences, and exclusive activities."
    }

    # Meal preference details
    meal_details = {
        "vegetarian": "All meal recommendations should be strictly vegetarian.",
        "non-vegetarian": "Include both vegetarian and non-vegetarian options with local specialties.",
        "vegan": "All recommendations should be vegan-friendly (no animal products).",
        "no-preference": "Include diverse food options based on local cuisine."
    }

    # Weather context
    weather_context = ""
    if weather_data:
        weather_context = f"\n\nCurrent Weather: Temperature is {weather_data['temp']}°C, {weather_data['condition']}. Consider this for outdoor activities and packing suggestions."

    prompt = f"""
    Create a highly detailed and personalized {days}-day travel itinerary for {destination}.

    **Travel Preferences:**
    - Primary Interests: {interests}
    - Budget: {budget_details.get(budget, budget_details['moderate'])}
    - Meal Preference: {meal_details.get(meal_preference, meal_details['no-preference'])}
    {weather_context}
    {user_history}

    **Please provide:**

    1. **Overview & Best Time to Visit**
       - Brief introduction to {destination}
       - Best seasons to visit and why
       - Local customs and etiquette tips

    2. **Day-by-Day Detailed Itinerary:**
       For each day, include:
       - **Morning (6 AM - 12 PM):** Activity/attraction with timing, estimated cost, and why it's recommended
       - **Afternoon (12 PM - 5 PM):** Activity/attraction with lunch recommendation
       - **Evening (5 PM - 10 PM):** Activity/attraction with dinner recommendation
       - **Estimated Daily Budget:** Breakdown of costs

    3. **Restaurant Recommendations:**
       - Must-try local dishes
       - Specific restaurant names with specialties (aligned with meal preference)
       - Price range for each

    4. **Accommodation Suggestions:**
       - 3 hotel options (budget-appropriate) with approximate prices
       - Best areas to stay in {destination}

    5. **Transportation:**
       - How to get around (metro, taxi, bike rental, etc.)
       - Estimated transportation costs
       - Tips for using local transport

    6. **Packing List:**
       - Essential items based on current weather
       - Cultural considerations for clothing

    7. **Money-Saving Tips:**
       - Local tricks to save money
       - Free attractions or experiences

    8. **Safety & Emergency:**
       - Important emergency numbers
       - Safety tips for tourists
       - Common scams to avoid

    9. **Total Estimated Budget:**
       - Comprehensive breakdown for the entire trip

    Make it engaging, practical, and personalized! Use emojis to make it visually appealing.
    """

    try:
        response = genai_client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt
        )
        itinerary_text = response.text

        # Save to user history with metadata
        if user_email:
            itinerary_record = {
                "destination": destination,
                "days": days,
                "interests": interests,
                "budget": budget,
                "itinerary": itinerary_text,
                "created_at": datetime.now().isoformat()
            }
            users.update_one(
                {"email": user_email},
                {"$push": {"itinerary_history": itinerary_record}}
            )

        return {
            "success": True,
            "itinerary": itinerary_text,
            "weather": weather_data
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/suggested-trips")
async def get_suggested_trips(request: Request):
    """Generate AI-powered trip suggestions based on user history and preferences"""
    data = await request.json()
    user_email = data.get("email")
    
    # Get user data
    user_context = ""
    if user_email:
        user = users.find_one({"email": user_email}, {"_id": 0, "itinerary_history": 1, "interests": 1})
        if user and "itinerary_history" in user:
            # Analyze user's past trips
            past_destinations = [trip.get("destination", "") for trip in user["itinerary_history"]]
            past_interests = [trip.get("interests", "") for trip in user["itinerary_history"]]
            user_context = f"\nUser has previously visited: {', '.join(past_destinations)}\nUser interests: {', '.join(past_interests)}"

    prompt = f"""
    Generate 6 diverse and exciting travel destination recommendations for a user.
    {user_context}

    For EACH destination, provide:
    1. **Destination Name**
    2. **Tagline:** One catchy line (10-15 words)
    3. **Highlights:** 4-5 key attractions/experiences (bullet points)
    4. **Best Time to Visit:** Specific months and why
    5. **Estimated Budget:** 3-day trip cost range in INR (budget/moderate/luxury)
    6. **Ideal For:** Type of travelers (adventure seekers, couples, families, solo travelers, etc.)
    7. **Must-Try Experience:** One unique thing you can only do here
    8. **Travel Tip:** One insider tip

    Make recommendations diverse (different continents, different types of experiences - beach, mountains, cultural, adventure, etc.)
    Avoid destinations the user has already visited.

    Format the response as a JSON array with these exact keys:
    [
      {{
        "destination": "string",
        "tagline": "string",
        "highlights": ["string", "string", ...],
        "bestTime": "string",
        "budget": "string",
        "idealFor": "string",
        "mustTry": "string",
        "travelTip": "string",
        "image": "emoji (use relevant travel emoji)"
      }}
    ]

    Return ONLY the JSON array, no other text.
    """

    try:
        response = genai_client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt
        )
        
        # Extract JSON from response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        
        import json
        trips = json.loads(response_text)
        
        return {
            "success": True,
            "trips": trips
        }

    except Exception as e:
        # Fallback to default suggestions if AI fails
        default_trips = [
            {
                "destination": "Santorini, Greece",
                "tagline": "Where blue domes meet endless azure seas",
                "highlights": ["Iconic white-washed buildings", "Stunning sunset views at Oia", "Ancient Akrotiri ruins", "Volcanic beaches"],
                "bestTime": "April-October for perfect weather",
                "budget": "₹35,000-70,000 for 3 days",
                "idealFor": "Couples, photographers, luxury travelers",
                "mustTry": "Watch sunset from Oia castle with local wine",
                "travelTip": "Book accommodation in Oia or Fira for best views",
                "image": "🏛️"
            },
            {
                "destination": "Kyoto, Japan",
                "tagline": "Ancient temples and cherry blossoms in perfect harmony",
                "highlights": ["1000+ Buddhist temples", "Geisha districts", "Bamboo forest walks", "Traditional tea ceremonies"],
                "bestTime": "March-April (cherry blossoms) or October-November (fall colors)",
                "budget": "₹40,000-80,000 for 3 days",
                "idealFor": "Culture enthusiasts, photographers, peaceful retreats",
                "mustTry": "Early morning visit to Fushimi Inari shrine",
                "travelTip": "Buy a Kyoto bus pass for unlimited travel",
                "image": "⛩️"
            },
            {
                "destination": "Banff, Canada",
                "tagline": "Turquoise lakes and majestic Rocky Mountains",
                "highlights": ["Lake Louise", "Moraine Lake", "Wildlife spotting", "Gondola rides"],
                "bestTime": "June-September for hiking, December-March for skiing",
                "budget": "₹50,000-100,000 for 3 days",
                "idealFor": "Adventure seekers, nature lovers, outdoor enthusiasts",
                "mustTry": "Sunrise at Moraine Lake",
                "travelTip": "Book accommodation 6 months in advance",
                "image": "🏔️"
            }
        ]
        
        return {
            "success": True,
            "trips": default_trips,
            "note": "Showing default suggestions"
        }


@app.get("/user-stats/{email}")
def get_user_stats(email: str):
    """Get user travel statistics"""
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