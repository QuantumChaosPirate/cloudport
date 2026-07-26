#FastAPI tools:(APIRouter, HTTPException, Depends):
    #APIROuter: router for grouping routes
    #HTTPException for returning error responses
    #Depends for dependency injection
from fastapi import APIRouter, HTTPException, Depends
#Azure tools: BlobServiceClient, generate_blob_sas, BlobSasPermissions:
#the storage client, the function that generates a SAS token, and the permissions object that controls what the token allows
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
#AzureError, which catches any Azure-related errors so we can handle them cleanly
from azure.core.exceptions import AzureError
#BaseModel, the Pydantic's base class for defining request and response shapes
from pydantic import BaseModel
#datetime, timezone, timedelta: Python's time tools, used to set when the presigned URL expires
from datetime import datetime, timezone, timedelta
#settings, which is our config object from config.py
from app.config import settings
#get_blob_service_client, our Azure connection from dependencies.py
from app.dependencies import get_blob_service_client
#uuid which generates unique IDs so two files with the same name never collide
import uuid
#logging which records errors to the log file so we can debug problems
import logging

#These import the 3 scanner functions which had been built, plus the authentication tools
#and database session so the quotas and update usage can be checked
from app.scanner import scan_blob, promote_to_production, delete_from_quarantine
from app.auth import get_current_user
from app.models.user import User
from sqlalchemy.orm import Session
from app.database import get_db

#logger, which creates a logger named after this file, used to record errors
logger = logging.getLogger(__name__)

#router, which all routes in this file start with /storage
router = APIRouter(prefix="/storage", tags=["storage"])

#The UploadRequest class defines what the frontend must send: a filename and a content type (e.g. image/jpeg)
class UploadRequest(BaseModel):
    filename: str
    content_type: str

#The UploadResponse class defines what the backend sends back: 
#the presigned URL, the object key (the file's unique path in storage), and how long until the URL expires
class UploadResponse(BaseModel):
    upload_url: str
    object_key: str
    expires_in: int
#The Pydantic automatically validates these, if the frontend sends the wrong types, FastAPI rejects the request before it even reaches our code


#@router.post, this is a POST endpoint because the frontend is sending data
#response_model=UploadResponse, FastAPI will validate and format the response using the UploadResponse model
@router.post("/presigned-upload", response_model=UploadResponse)

#Depends(get_blob_service_client), FastAPI automatically injects the Azure storage connection we defined in dependencies.py
async def generate_presigned_upload_url(
    request: UploadRequest,
    blob_client: BlobServiceClient = Depends(get_blob_service_client),
):
##Every uploaded file gets a unique path like uploads/a3f7c2.../photo.jpg. 
#The UUID in the middle ensures two files with the same name never overwrite each other.
    object_key = f"uploads/{uuid.uuid4()}/{request.filename}"

    try:
        account_key = blob_client.credential.account_key
        ##SAS (Shared Access Signature): Azure's version of a presigned URL. 
	#This is used to generate a token, which gives temporary write-only permission to one specific file in the quarantine container.
        sas_token = generate_blob_sas(
            account_name=settings.azure_storage_account_name,
            container_name=settings.quarantine_container_name,
            blob_name=object_key,
	    account_key=account_key,
	    #the token only allows uploading, not reading or deleting
            permission=BlobSasPermissions(write=True),
            #the token expires after 1 hour by default
	    expiry=datetime.now(timezone.utc) + timedelta(seconds=settings.presigned_url_expiry_seconds),
	#It points to the quarantine container, not production: the file gets scanned before it ever reaches production
        )

	#Combines the storage account URL, container name, file path, and SAS token into one complete URL
	#the frontend can use to upload directly to Azure, bypassing using our server entirely.
        upload_url = (
            f"https://{settings.azure_storage_account_name}.blob.core.windows.net"
            f"/{settings.quarantine_container_name}/{object_key}?{sas_token}"
        )

#In the case of failure with Azure, we the real error is internally logged but return a clean generic message to the user.
#This is important, as such internal error details musn't be shown to the frontend.
    except AzureError as e:
        logger.error(f"Failed to generate upload URL: {e}")
        raise HTTPException(status_code=500, detail="Could not generate upload URL")

    return UploadResponse(
        upload_url=upload_url,
        object_key=object_key,
        expires_in=settings.presigned_url_expiry_seconds,
    )


#The download endpointis the same pattern as upload but:
    #It's a GET request since we're retrieving data
    #It points to the production container, not quarantine: files are only downloaded that have passed the scanning
    #The token only has read=True permission
    #It expires after 5 minutes (300 seconds): much shorter than uploads since download links should be short-lived for security
@router.get("/presigned-download/{object_key:path}")
async def generate_presigned_download_url(
    object_key: str,
    blob_client: BlobServiceClient = Depends(get_blob_service_client),
):
    try:
        account_key = blob_client.credential.account_key

        sas_token = generate_blob_sas(
            account_name=settings.azure_storage_account_name,
            container_name=settings.production_container_name,
            blob_name=object_key,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + timedelta(seconds=300),
        )

        download_url = (
            f"https://{settings.azure_storage_account_name}.blob.core.windows.net"
            f"/{settings.production_container_name}/{object_key}?{sas_token}"
        )

    except AzureError as e:
        logger.error(f"Failed to generate download URL: {e}")
        raise HTTPException(status_code=500, detail="Could not generate download URL")

    return {"download_url": download_url}

################################################################ 
@router.post("/scan/{object_key:path}")
async def scan_and_promote(
    object_key: str,
    db: Session = Depends(get_db),
    blob_client: BlobServiceClient = Depends(get_blob_service_client),
    current_user: User = Depends(get_current_user),
):
    """
    Called after a file has been uploaded to quarantine.
    Scans the file with ClamAV and promotes to production if clean.
    """
    # Check user hasn't exceeded their storage quota
    blob = blob_client.get_blob_client(
        container=settings.quarantine_container_name,
        blob=object_key
    )

    #Obtains the file size from Azure, then checks if adding this file would push the user over their quota
    #If it does, the dile is deleted from quarantine and the request is rejected, then the error is deleted
    #(The deletion must be first, as we shouldn't keep files longer than bare minimum)
    blob_properties = blob.get_blob_properties()
    file_size = blob_properties.size

    if current_user.storage_used_bytes + file_size > current_user.storage_quota_bytes:
        delete_from_quarantine(object_key, blob_client)
        raise HTTPException(
            status_code=400,
            detail="Storage quota exceeded. File rejected."
        )

    # Check if upload approval is required for this user, it's for the parental control gate
    #Function is ran if the user account is of 'child' priveleges, the file stuck in quarantine until Admin or Owner approval
    if current_user.requires_upload_approval:
        raise HTTPException(
            status_code=403,
            detail="Your uploads require admin approval before processing."
        )

    # Scans the file, by calling scan_blob(), if file is infected then it's removed from quarantine
    #and a clear error message is returned to the user
    is_clean = scan_blob(object_key, blob_client)

    if not is_clean:
        delete_from_quarantine(object_key, blob_client)
        raise HTTPException(
            status_code=400,
            detail="File failed malware scan and has been rejected."
        )

    # Promote to production if the file passes all the checks
    promote_to_production(object_key, blob_client)

    # Update user's storage usage in database to reflect the new usage, keeps storage dashboard accurate
    current_user.storage_used_bytes += file_size
    db.commit()

    #Success message is returned, with the file key and size. Frontend uses object_key to generate a download URL later
    return {
        "message": "File scanned and uploaded successfully",
        "object_key": object_key,
        "file_size": file_size
    }
