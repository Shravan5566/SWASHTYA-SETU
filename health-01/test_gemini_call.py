from app import create_app
from app.services.ai_service import call_gemini

app = create_app()
with app.app_context():
    resp = call_gemini("Reply with: SWASTHYA_SETU_AI_ONLINE")
    print("Gemini response:", resp)
