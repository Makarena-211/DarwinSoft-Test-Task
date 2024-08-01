from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import routes
import models
from database import engine
app = FastAPI()
models.Base.metadata.create_all(bind=engine)
app.include_router(routes.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"])
