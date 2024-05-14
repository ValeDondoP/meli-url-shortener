from fastapi import FastAPI
from app.routers.url import router as url_router

app = FastAPI()
# Configurar repositorios


app.include_router(url_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)