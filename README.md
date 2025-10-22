#  VoyageVista Backend 

**VoyageVista** is an AI-powered travel planning backend built using **FastAPI**, **MongoDB**, and **Gemini AI**.  
It dynamically generates personalized itineraries, destination recommendations, and user travel insights — all with real-time weather integration.  

---

##  Features

1. **User Authentication** — Signup & Login using bcrypt encryption  
2. **AI-Powered Itinerary Generation** — Personalized trip plans using Gemini AI  
3. **Smart Destination Suggestions** — Recommends unique places based on user history  
4. **Weather Integration** — Live weather data for chosen destinations  
5. **MongoDB Storage** — Keeps user profiles, itineraries, and stats  
6. **Modular Codebase** — Clean structure for scalability and maintenance  

---

##  Tech Stack

- **Backend Framework:** FastAPI  
- **Database:** MongoDB  
- **AI Engine:** Google Gemini (via `google-generativeai`)  
- **Environment Management:** python-dotenv  
- **Security:** bcrypt  
- **API Layer:** REST APIs (JSON responses)  

---

##  Project Structure


backend/
│
├── main.py
├── .env
├── .gitignore
├── requirements.txt
│
├── routes/
│ ├── init.py
│ ├── auth_routes.py
│ ├── itinerary_routes.py
│ ├── user_routes.py
│
└── utils/
├── init.py
├── db.py
├── ai_utils.py
├── weather_utils.py


---

##  Environment Variables

Create a `.env` file in your project root and add the following:

```bash
MONGO_URI=your_mongodb_connection_string
GEMINI_API_KEY=your_gemini_api_key
WEATHER_API_KEY=your_openweathermap_api_key


Make sure your .env file is added to .gitignore so it doesn’t get uploaded to GitHub!

 Installation & Setup
# 1️⃣ Clone the repository
git clone https://github.com/AdityaRaorane22/VoyageVista_Backend.git
cd VoyageVista_Backend

# 2️⃣ Create virtual environment
python -m venv venv
venv\Scripts\activate      # on Windows
# OR
source venv/bin/activate   # on Mac/Linux

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ Run FastAPI server
uvicorn main:app --reload

🌐 API Endpoints
Endpoint	Method	Description
/	GET	Health check
/auth/signup	POST	Register new user
/auth/login	POST	Login existing user
/user/{email}	GET	Get user data
/user/update	POST	Update user profile
/user-stats/{email}	GET	Get user travel statistics
/itinerary	POST	Generate personalized itinerary
/itinerary/suggested-trips	POST	AI-powered trip recommendations


 Contributing

Contributions are welcome!
If you'd like to improve this backend or add new features, fork the repo and create a pull request.

 Author

Aditya Raorane
Email: adityanraorane@gmail.com

GitHub: AdityaRaorane22



Acknowledgments

FastAPI

MongoDB

Google Gemini

OpenWeatherMap API

