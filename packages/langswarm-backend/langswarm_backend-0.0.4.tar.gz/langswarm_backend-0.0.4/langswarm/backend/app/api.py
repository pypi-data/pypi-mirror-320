from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

class Message(BaseModel):
    sender: str
    content: str

# In-memory message store
chat_window: List[Message] = []

def setup_routes(app: FastAPI):
    @app.post("/send-message")
    def send_message(message: Message):
        chat_window.append(message)
        return {"status": "success", "message": "Message received."}

    @app.get("/get-messages")
    def get_messages():
        return chat_window
