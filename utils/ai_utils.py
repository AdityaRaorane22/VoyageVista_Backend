import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.api_key = GEMINI_API_KEY

def generate_text(prompt: str):
    response = genai.generate_text(
        model="gemini-2.0-flash-exp",
        prompt=prompt
    )
    return response.result
