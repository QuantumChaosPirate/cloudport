import io
import clamd
import logging
from azure.storage.blob import BlobServiceClient
from app.config import settings

logger = logging.getLogger(__name__)

#Creates the connection between the ClamAV daemon via a Unix socket
#(for a fast connection between 2 programs on the same machine)
def get_clamd_client():
    """Connect to the ClamAV daemon via Unix socket"""
    return clamd.ClamdUnixSocket()

#The main scanning function, takes file key (i.e. path in blob storage) and Azure storage client
#Returns true if it's clean, false if infected
def scan_blob(object_key: str, blob_service_client: BlobServiceClient) -> bool:
    """
    Downloads a file from quarantine, scans it with ClamAV.
    Returns True if clean, False if infected.
    """
    try:
        # Download file from quarantine container into memory
        #(It's not saved to disk, kept in memory for faster and cleaner performance)
        quarantine_client = blob_service_client.get_blob_client(
            container=settings.quarantine_container_name,
            blob=object_key
        )
        blob_data = quarantine_client.download_blob().readall()

        # Scan the file data with ClamAV
        #('intsream': the data is being streamed to ClamAV rather than pointing it at a file on disk)
        #(Result comes back as a status [OK or FOUND] and a reason [the malware name if found])
        #[The io.BytesIO wraps the bytes data in a file-like object which can be read properly by ClamAV's instream
        cd = get_clamd_client()
        result = cd.instream(io.BytesIO(blob_data))
        status, reason = result["stream"]

        #ClamAV outputs "OK" when the file is clean,
        #anthing else would mean that malware had beem detected, the reason will contain malware name which will get logged
        if status == "OK":
            logger.info(f"File {object_key} is clean")
            return True
        else:
            logger.warning(f"File {object_key} is infected: {reason}")
            return False
    #In the case of an error (likely due to ClamAV being down, network error, etv.),
    #The function was returned 'False' and the file is trated as infected
    #This is because of the fail safe principle, rejecting when in doubt even if the file is safe to prevent an infection
    except Exception as e:
        logger.error(f"Scan failed for {object_key}: {e}")
        # If scanning fails, treat as infected to be safe
        return False

#This function is called when a file passes the scan, moved from 'quarantine' to 'production' stages
def promote_to_production(object_key: str, blob_service_client: BlobServiceClient) -> None:
    """
    Moves a clean file from quarantine to production container.
    """
    source_client = blob_service_client.get_blob_client(
        container=settings.quarantine_container_name,
        blob=object_key
    )
    dest_client = blob_service_client.get_blob_client(
        container=settings.production_container_name,
        blob=object_key
    )

    # Copy from quarantine to production
    source_url = source_client.url
    dest_client.start_copy_from_url(source_url)

    # Delete from quarantine
    source_client.delete_blob()
    logger.info(f"File {object_key} promoted to production")
#Copy & Delete, since as of time of production, Azure doesn't have a 'move' operation
#File is only removed from quarantie after it's safely copied in productiom


#This function is called when a file fails the scan, file is just deleted from qurantine and never pushed to production
def delete_from_quarantine(object_key: str, blob_service_client: BlobServiceClient) -> None:
    """
    Deletes an infected file from quarantine.
    """
    quarantine_client = blob_service_client.get_blob_client(
        container=settings.quarantine_container_name,
        blob=object_key
    )
    quarantine_client.delete_blob()
    logger.warning(f"Infected file {object_key} deleted from quarantine")
