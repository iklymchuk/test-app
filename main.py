from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

from hotel.db import engine
from hotel.routers import bookings, customers, rooms

# Use absolute path for database
DB_FILE_PATH = f"sqlite:///{Path(__file__).parent / 'hotel_snap.db'}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine.init_db(DB_FILE_PATH)
    yield


app = FastAPI(lifespan=lifespan)

# Include routers
app.include_router(rooms.router)
app.include_router(customers.router)
app.include_router(bookings.router)


mcp = FastApiMCP(
    app,
    include_operations=[
        "get_all_rooms",
        "get_room_by_id",
        "create_room",
        "get_all_customers",
        "get_customer_by_id",
        "create_customer",
        "update_customer",
        "get_all_bookings",
        "get_booking_by_id",
        "create_booking",
        "delete_booking",
    ],
)
# mcp.mount_http()
mcp.mount_sse()
