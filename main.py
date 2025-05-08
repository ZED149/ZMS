

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

    # Instanciating MediaManager object
    o = MediaManager(verbosity=VERBOSITY, db_name=DB_NAME, logger_name="Salman Ahmad")

    # setting sending email and commiting to DB flag = False
    flag = False

    # crawling the directory for new movies
    movies = o.amtd(verbose=True, path="media_manager/not_uploaded/movies/", db_name=DB_NAME)
    # crawling the directory for new or updated tv_shows
    tv_shows = o.nmtatstd(verbosity=True, db_name=DB_NAME, path="media_manager/not_uploaded/tv_shows/updated/")
    print("Movies: ")
    for movie in movies:
        print(movie)
    print("TV Shows: ")
    for ts in tv_shows:
        print(ts)
    # sending emails to receipents
    flag = o.send_emails(verbose=True, db_name=DB_NAME, movies_list=movies, tv_shows=tv_shows)
    if flag:
        print("Being committed to the DB.")
        o.commit(verbosity=True)
    else:
        print("email not send and not committed to the DB.")