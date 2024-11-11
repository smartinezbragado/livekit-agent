import uvicorn
from fastapi import FastAPI
from src.api import v1


app = FastAPI()

app.include_router(v1.token.router)

if __name__ == "__main__":
    uvicorn.run("src.api.main:app", port=8000)