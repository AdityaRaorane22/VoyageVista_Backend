from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth_routes import router as auth_router
from routes.user_routes import router as user_router
from routes.itinerary_routes import router as itinerary_router

app = FastAPI(title="VoyageVista API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, tags=["Authentication"])
app.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(itinerary_router, prefix="/itinerary", tags=["Itinerary"])

# Add this line to also include itinerary routes at root level
app.include_router(itinerary_router, tags=["Itinerary Root"])

@app.get("/")
def home():
    return {"message": "VoyageVista Backend is running"}
