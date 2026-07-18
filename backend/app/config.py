from pydantic_settings import BaseSettings
#The BaseSettings class is imported and used for our Settings class to read values for env variables and .env automatically

#A Settings class which inherits from BaseSettings, acts as a container for all the config values which backend need to run
class Settings(BaseSettings):
    #Azure Storage settings

    #Connects backend to the Azure storage acc, no default value makes it compulsory for an acc for the app to run
    azure_storage_connection_string: str
    azure_storage_account_name: str

    #Names of the 2 storage containers for "quarantine" & "production", so the user doesn't need to touch them unless to change names
    quarantine_container_name: str = "quarantine"
    production_container_name: str = "production"
    
    #The database access
    database_url: str

    #API settings: Metadata about the APU
    api_title: str = "CloudPort API"
    api_version: str = "0.1.0"
    
    # Presigned URL expiry (1 hour default)
    presigned_url_expiry_seconds: int = 3600

    #This Config class tells the pydantic-settings to search for an .env file and loads values from it
    #This makes it so instead of setting env variables manually each time, it's put in the .env file and the app picks them up automatically 
    class Config:
        env_file = ".env"

#Creates an instance of the Settings class that the entire app imports & uses, a single point of truth for all configuration
settings = Settings()

