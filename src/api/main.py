import uvicorn

from src.api import v1
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

app.include_router(v1.talent.router)
app.include_router(v1.token.router)
app.include_router(v1.notifications.router)
app.include_router(v1.vectorstore.router)  # Added vectorstore router

if __name__ == "__main__":
    uvicorn.run("src.api.main:app", port=8000)