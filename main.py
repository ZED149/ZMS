

# including important libraries
from media_manager import MediaManager
import os
from dotenv import load_dotenv

# loading enviournmental variables into our scope
load_dotenv(dotenv_path="media_manager/.env")

# GLOBAL
MOVIES_DB = os.getenv('MOVIES_DB')

# MAIN
if __name__ == "__main__":
    print("Working")
    o = MediaManager()
    
    # creating movies table in the db
    # o.cmtid(MOVIES_DB)

    # adding all movies to the db
    o.amtd("media_manager/movies/", MOVIES_DB)
    