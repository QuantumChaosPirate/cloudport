#Imports APIRouter, which FastAPI's way of grouping related routes together. 
#Instead of defining all routes in the main.py, we split them into separate files by what they do: 
#Health checks in health.py, storage in storage.py etc.
from fastapi import APIRouter

#Creates a router with two settings:
#1. prefix="/health": every route in this file automatically starts with '/health', so our route becomes '/health/' rather than just '/'
#2. tags=["health"]: groups this route under the "health" label in the auto-generated API documentation
router = APIRouter(prefix="/health", tags=["health"])

#This defines a GET endpoint at /health/. 
#This is the route a monitoring tool hits, to check if the API is up.
@router.get("/")

#The function that runs when someone hits /health/.
#'async' means it runs asynchronously and won't block other requests while running
async def health_check():
    #Returns a simple JSON response. When the API is running, this returns successfully.
    #However, if the API is down, nothing returns at all, which is how the monitoring system knows something is wrong.
    return {
        "status": "healthy",
        "service": "CloudPort API"
    }

