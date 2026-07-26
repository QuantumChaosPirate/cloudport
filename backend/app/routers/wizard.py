from fastapi import APIRouter, Depends, HTTPException
#HTMLResponse: lets FastAPI return an HTML page instead of JSON
#StaticFiles: serves static files, such as CSS and Js
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app.models.user import User, UserRole
from app.auth import hash_password
#subprocess: allows Python run external commands, used to trigger the Jellyfin setup script
#os: allows Python to interact with the OS, mostly used to check if files exist
import subprocess
import os

router = APIRouter(prefix="/wizard", tags=["wizard"])

#Defines what exactly the wizard frontend must end.
#Pydantic validates all fields automatically, if anything is missing or wron type,
#FastAPI rejects the request before it reaches our code
class SetupRequest(BaseModel):
    azure_account_name: str
    azure_connection_string: str
    domain: str
    email: EmailStr
    storage_quota_bytes: int
    username: str
    owner_email: EmailStr
    password: str
    jellyfin_password: str

#When a person visits /wizard for the first time, this endpoint reads the index.html file
#and sends it to the browser, response_class=HTMLResponse tells FastAPI to send HTML instead of JSON
@router.get("/", response_class=HTMLResponse)
async def wizard_page():
    """
    Serves the setup wizard HTML page.
    Only accessible before CloudPort is configured.
    """
    # Check if already configured
    #If it does, Cloudport has already beemn set up and therefore, drops the install wizard since it would overwrite the existing installation
    if os.path.exists("../config/.cloudport_configured"):
        raise HTTPException(
            status_code=403,
            detail="CloudPort is already configured."
        )

    with open("../wizard/templates/index.html", "r") as f:
        return HTMLResponse(content=f.read())


@router.post("/setup")
async def run_setup(request: SetupRequest, db: Session = Depends(get_db)):
    """
    Receives setup data from the wizard frontend and configures CloudPort.
    """
    # Check if already configured
    if os.path.exists("../config/.cloudport_configured"):
        raise HTTPException(
            status_code=403,
            detail="CloudPort is already configured."
        )

    # Check no users exist yet [acts as a second check]
    #If there is, the setup wizard is dropped, as that would mean there is already an installation
    if db.query(User).count() > 0:
        raise HTTPException(
            status_code=400,
            detail="CloudPort has already been set up."
        )

    # Create the Owner account usinf the credentials given in the wizard form
    owner = User(
        email=request.owner_email,
        username=request.username,
        hashed_password=hash_password(request.password),
        role=UserRole.owner,
        storage_quota_bytes=request.storage_quota_bytes,
    )
    db.add(owner)
    db.commit()
    db.refresh(owner)

    # Trigger Jellyfin setup script with the provided credentials
    subprocess.Popen([
        "/bin/bash",
        "../jellyfin/jellyfin-setup.sh"
    ], env={
        **os.environ,
        "JELLYFIN_ADMIN_USERNAME": request.username,
        "JELLYFIN_ADMIN_PASSWORD": request.jellyfin_password,
    })
    # Write Azure credentials to .env file
    env_path = "../.env"
    with open(env_path, "r") as f:
        env_content = f.read()

    env_content = env_content.replace(
        "AZURE_STORAGE_CONNECTION_STRING=your-azure-storage-connection-string",
        f"AZURE_STORAGE_CONNECTION_STRING={request.azure_connection_string}"
    )
    env_content = env_content.replace(
        "AZURE_STORAGE_ACCOUNT_NAME=your-storage-account-name",
        f"AZURE_STORAGE_ACCOUNT_NAME={request.azure_account_name}"
    )
    env_content = env_content.replace(
        "DOMAIN=yourdomain.com",
        f"DOMAIN={request.domain}"
    )

    with open(env_path, "w") as f:
        f.write(env_content)

    # Mark CloudPort as configured, blocks the wizard to run again permanently
    os.makedirs("../config", exist_ok=True)
    open("../config/.cloudport_configured", "w").close()

    return {
        "message": "CloudPort configured successfully",
        "username": request.username
    }
