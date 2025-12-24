from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI

from hotel.db import engine
from hotel.routers import bookings, customers, rooms

# Use absolute path for database
DB_FILE_PATH = f"sqlite:///{Path(__file__).parent / 'hotel_snap.db'}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine.init_db(DB_FILE_PATH)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello": "World"}


# Include routers
app.include_router(rooms.router)
app.include_router(customers.router)
app.include_router(bookings.router)  
