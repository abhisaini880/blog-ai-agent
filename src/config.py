from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    BASE_URL = os.getenv("BASE_URL")
    API_KEY = os.getenv("API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


config = Config()
