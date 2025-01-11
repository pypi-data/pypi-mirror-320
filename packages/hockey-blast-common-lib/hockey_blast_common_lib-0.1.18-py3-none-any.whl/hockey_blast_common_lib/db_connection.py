# import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database connection parameters per organization
DB_PARAMS = {
    "frontend": {
        "dbname": "hockey_blast",
        "user": "frontend_user",
        "password": "hockey-blast",
        "host": "localhost",
        "port": 5432
    },

    "frontend-sample-db": {
        "dbname": "hockey_blast_sample",
        "user": "frontend_user",
        "password": "hockey-blast",
        "host": "localhost",
        "port": 5432
    },

    "boss": {
        "dbname": "hockey_blast",
        "user": "boss",
        "password": "WrongPassword",
        "host": "localhost",
        "port": 5432
    },

}

def get_db_params(config_name):
    if config_name not in DB_PARAMS:
        raise ValueError(f"Invalid organization: {config_name}")
    return DB_PARAMS[config_name]

def create_session(config_name):
    db_params = get_db_params(config_name)
    db_url = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}"
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session()
