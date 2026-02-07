from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.main import api_router
from config.settings import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for LangChain-powered applications",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.all_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 