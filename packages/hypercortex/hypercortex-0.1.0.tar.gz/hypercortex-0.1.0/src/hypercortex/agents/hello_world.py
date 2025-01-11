import os

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

os.environ["GEMINI_API_KEY"] = "AIzaSyBqQsF_Tk7dp-S3iri0E__2DTzYmOZ0DD4"

llm = os.getenv("LLM_MODEL", "deepseek/deepseek-chat")

# model = OpenAIModel(
#     model_name=llm,
#     base_url="https://openrouter.ai/api/v1",
#     api_key=os.getenv("OPEN_ROUTER_API_KEY"),
# )


agent = Agent(
    "gemini-1.5-flash", system_prompt="Hello, I'm a Python agent. What's your name?"
)
