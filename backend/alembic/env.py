#fileConfig: sets up logging so Alembic prints useful messages when running migrations
from logging.config import fileConfig
#engine_from_config: creates a database engine from the settings in alembic.ini
from sqlalchemy import engine_from_config
#pool: manages database connections efficiently
from sqlalchemy import pool
#context: Alembic's main object, controls how migrations run
from alembic import context
#Base: our SQLAlchemy base from database.py, this is how Alembic knows what tables exist
from app.database import Base
#user — imports our User model so Alembic can see the users table
from app.models import user

# Alembic config object, provides access to alembic.ini values
config = context.config

# Set up Python logging from the alembic.ini file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# This is the metadata object from our models
# Alembic uses this to detect what tables exist and what needs to change
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    # Run migrations without an active database connection
    # Used when you want to generate SQL scripts instead of running them directly
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        #Base.metadata contains a description of every table defined in our models.
        #Alembic compares this against what actually exists in the database to figure out what's changed and what migrations need to run.
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    # Run migrations with an active database connection
    # This is the normal mode — connects to PostgreSQL and applies changes directly
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

# Decide which mode to run in and execute:
    #For offline: Runs migrations without connecting to the database.
        #Instead of applying changes directly, it generates SQL scripts you could run manually. 
        #Useful for reviewing what changes will be made before applying them, or for environments where direct database access isn't available.
    #For online: The normal mode — connects directly to PostgreSQL and applies migrations immediately.
        #This is what runs on CloudPort installations when someone updates.
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
