from fastapi import FastAPI
from routes import router
from models import create_db

create_db()

app = FastAPI()
app.include_router(router)






