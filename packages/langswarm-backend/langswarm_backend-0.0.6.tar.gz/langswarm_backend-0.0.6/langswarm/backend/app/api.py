from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from langswarm.core.factory.agents import AgentFactory

# Set environment variables
#os.environ['OPENAI_API_KEY'] = 'your-openai-api-key'

# Create a LangChain agent
agent = AgentFactory.create(
    name="example_agent",
    agent_type="langchain-openai",
    model="gpt-4o-mini-2024-07-18"
)

class Message(BaseModel):
    sender: str
    content: str

# In-memory message store
chat_window: List[Message] = []

def setup_routes(app: FastAPI):
    @app.post("/send-message")
    def send_message(message: Message):
        chat_window.append(message)
        # Use the agent to respond to queries
        return agent.chat(message.content)

    @app.get("/get-messages")
    def get_messages():
        return chat_window
