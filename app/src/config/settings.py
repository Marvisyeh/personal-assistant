from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "LangChain API Template"
    API_V1_STR: str = "/api/v1"
    
    # CORS settings
    all_cors_origins: List[str] = ["*"]
    
    
    # Model settings
    DEFAULT_MODEL: str = "gpt-4o-mini"
    DEFAULT_MODEL_PROVIDER: str = "openai"
    

settings = Settings()

def get_settings() -> Settings:
    return settings