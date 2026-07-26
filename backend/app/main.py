#Imports the main FastAPI class: this is what creates the actual application.
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
#Imports our settings object so we can use the API title and version which was defined in config.py
from app.config import settings
#Imports both routers we just built. This is how main.py knows about all the routes defined in the other files.
#Note: imported the auth, users, wizard & files to be accessed
from app.routers import storage, health, auth, users, wizard, files

#Creates the FastAPI application instance.
#The title, version, and description show up in the auto-generated API documentation at /docs
#Which is useful for anyone building on top of CloudPort later.
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Self-hostable personal cloud platform API",
)

#Mounts the static files for the wizard frontend
app.mount("/static", StaticFiles(directory="../wizard/static"), name="static")

#Registers both routers with the app.
#This is what makes the routes actually accessible.
#Without these lines, FastAPI wouldn't know the /health/ and /storage/ routes exist even though we defined them.
app.include_router(health.router)
app.include_router(storage.router)
#The auth router
app.include_router(auth.router)
#The user settings router
app.include_router(users.router)
#The installation wizard router
app.include_router(wizard.router)
#The file approval system routher
app.include_router(files.router)


#A simple landing page for the API.
#When someone visits the root URL / they get a welcome message and a pointer to /docs where the full API documentation lives.
#FastAPI generates that documentation automatically from the code.
@app.get("/")
async def root():
    return {
        "message": "Welcome to CloudPort API",
        "version": settings.api_version,
        "docs": "/docs"
    }
