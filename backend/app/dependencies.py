#Imports the BlobServiceClient class from Azure's Python library,
#which is the main object used to connect to Azure Blob Storage, this manages the storage account used
from azure.storage.blob import BlobServiceClient

#Imports the lru_cache decorator, (LRU: Least Recently Used)
#a caching tool which holds the result of a function so it doesn't rerun it unnecessarily
from functools import lru_cache

#Imports the settings object which was just created in config.py,
#So the connection string stored there could be used
from app.config import settings

#This decorator means the function only runs once, when the first time it's called.
#After that, Python will return the cached result, instead of constantly creating a new connection,
#Important since creating a new connection to Azure on every single request would be slow and wasteful.
@lru_cache()

#Defines a function that returns a BlobServiceClient. 
#The -> BlobServiceClient part is a type hint which tells other developers and tools what type of object this function returns.
def get_blob_service_client() -> BlobServiceClient:
    #Creates and returns a BlobServiceClient using the connection string from the settings.
    #This connection string contains everything Azure needs to authenticate and connect to your storage account.
    return BlobServiceClient.from_connection_string(
        settings.azure_storage_connection_string
    )
