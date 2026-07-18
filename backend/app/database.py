#Imports the engine creator, which connects to PostgreSQL
from sqlalchemy import create_engine
#Imports the base class that all our database models will inherit from. It's what links the Python classes to actual database tables.
from sqlalchemy.ext.declarative import declarative_base
#Imports the session factory. A session is a temporary conversation with the database: open, run, then close
from sqlalchemy.orm import sessionmaker
from app.config import settings
#Creates the actual connection to PostgreSQL using the DATABASE_URL from the .env file, which is the one persistent connection the entire app uses.
engine = create_engine(settings.database_url)

#Creates a session factory bound to our engine:
    #'autocommit=False': changes aren't saved automatically, it has to be explicitly committed.
        #This gives control, if something goes wrong mid-operation, it can roll back.
    #'autoflush=False': SQLAlchemy won't automatically send pending changes to the database before every query. Again, gives more control to the user.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Creates the base class that all the models will inherit from,
#when SQLAlchemy sees the class inheriting from Base, it knows that class represents a database table.
Base = declarative_base()

#A function that provides a database session to any route that needs one.
def get_db():
    #new session opened
    db = SessionLocal()
    try:
        #passes the session to whoever called this function
        yield db
    finally:
        #guarantees the session is closed after the request finishes, even if an error occurred
        db.close()

#The 'yield' makes this a generator function, FastAPI uses this pattern with 'Depends()' to automatically manage database sessions for each request.
