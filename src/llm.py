from src.config import config
from langchain_openai import ChatOpenAI


def get_llm():
    return ChatOpenAI(
        model=config.MODEL_NAME, base_url=config.BASE_URL, api_key=config.API_KEY
    )
