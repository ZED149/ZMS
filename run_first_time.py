

# Run this file only for the first time before executing the main script



# including important libraries
from media_manager import MediaManager
import os
from dotenv import load_dotenv

# loading enviournmental variables into our scope
load_dotenv(dotenv_path="media_manager/.env")

# GLOBAL Variables
DB_NAME = os.getenv('DB_NAME')
VERBOSITY = True
EMAIL_FILE = os.getenv("EMAIL_FILE")

# MAIN
if __name__ == "__main__":
    print("Script initiated...")
    print(f"DB NAME: {DB_NAME}")

    # Instanciating MediaManager object
    o = MediaManager(verbosity=VERBOSITY, db_name=DB_NAME, logger_name="Salman Ahmad")

    # setting sending email and commiting to DB flag = False
    flag = False

    # creating email table in the DB
    o.cetid(verbosity=VERBOSITY, db_name=DB_NAME)
    # adding emails to the db
    o.aetd(verbosity=VERBOSITY, file=EMAIL_FILE, db_name=DB_NAME)

    # creating movies table in the DB
    o.cmtid(verbosity=VERBOSITY, db_name=DB_NAME)
    
    # creating tv_shows table in the DB
    o.ctstid(verbosity=VERBOSITY, db_name=DB_NAME)

    o.commit()
