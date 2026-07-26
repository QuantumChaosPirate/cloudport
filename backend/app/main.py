#Imports the prometheus instrumentator needed for making the cost calculations
from prometheus_fastapi_instrumentator import Instrumentator
#Imports the main FastAPI class: this is what creates the actual application.
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
#Imports our settings object so we can use the API title and version which was defined in config.py
from app.config import settings
#Imports both routers we just built. This is how main.py knows about all the routes defined in the other files.
#Note: imported the auth, users, wizard, files & dashboard to be accessed
from app.routers import storage, health, auth, users, wizard, files, dashboard

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
#Mounts the dashboard & display menu
app.mount("/dashboard/static", StaticFiles(directory="../dashboard/static"), name="dashboard-static")

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
#The file approval system router
app.include_router(files.router)
#The dasboard menu & display router
app.include_router(dashboard.router)


#This will send the user directly to the login dashboard of the cloudport instance
from fastapi.responses import RedirectResponse

@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard/")

# Expose /metrics endpoint for Prometheus to scrape
Instrumentator().instrument(app).expose(app)

