from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import os

from db import SessionLocal, Base, engine
from models import ChatHistory
from groq import Groq

# Load environment variables from .env file
load_dotenv()

# Access the env variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PORT = int(os.getenv("PORT", 8000))
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")
GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", 100))

# Add this check here
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found in environment variables.")

# Create tables if not exist
Base.metadata.create_all(bind=engine)

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Request model for chat
class ChatRequest(BaseModel):
    prompt: str

# Home page
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# Health check HTML page
@app.get("/health", response_class=HTMLResponse)
def health_page(request: Request):
    return templates.TemplateResponse("health.html", {"request": request})

# Health check API
@app.get("/health-check")
def health_check():
    return {"status": "OK"}

# Chat HTML page
@app.get("/chat", response_class=HTMLResponse)
def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

# Chat completion API
@app.post("/chat-completion")
def chat_completion(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Answer concisely and briefly: {request.prompt}",
                }
            ],
            model=GROQ_MODEL,  # double-check the model name if necessary
            max_tokens=GROQ_MAX_TOKENS  # Limit the response length
        )

        reply = chat_completion.choices[0].message.content

        # Save to DB
        chat_entry = ChatHistory(prompt=request.prompt, response=reply)
        db.add(chat_entry)
        db.commit()
        db.refresh(chat_entry)

        return {"completion": reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Chat history API
@app.get("/chat-history", response_class=HTMLResponse)
def chat_history_page(request: Request, db: Session = Depends(get_db)):
    chats = db.query(ChatHistory).order_by(ChatHistory.created_at.desc()).all()
    return templates.TemplateResponse("chat_history.html", {"request": request, "chats": chats})
