

# including important libraries
from media_manager import MediaManager
import os
from dotenv import load_dotenv

# loading enviournmental variables into our scope
load_dotenv(dotenv_path="media_manager/.env")

# GLOBAL
DB_NAME = os.getenv('DB_NAME')

# MAIN
if __name__ == "__main__":
    print("Working")

    # Instanciating MediaManager
    o = MediaManager(db_name=DB_NAME)

    # setting sending email and commiting to DB flag = False
    flag = False
    
    # perform this only if flag is True
    if flag:
        # creating movies table in the db
        o.cmtid(DB_NAME)

        # adding all movies to the db
        o.amtd(True, "media_manager/movies/", DB_NAME)

        # creating tv_shows table in the db
        o.ctstid(DB_NAME)
        
        # adding tv_shows to the db
        o.atstd(True, "media_manager/tv_shows/", DB_NAME)

        # creating emails table in the db
        o.cetid(DB_NAME)

        # adding emails to the DB
        o.aetd(file="emails.xlsx", db_name=DB_NAME)


    # Now need to create and then send emails
    movies = []
    tv_shows = {}
    # crawling the directory for new movies
    movies = o.amtd(False, "media_manager/not_uploaded/movies/", db_name=DB_NAME)
    tv_shows = o.atstd(False, "media_manager/not_uploaded/tv_shows/", db_name=DB_NAME)
    print("Movies: ")
    print(movies)
    print("TV Shows: ")
    print(tv_shows)
    # creating emails
    o.MESSAGE = o.ce(db_name=DB_NAME, movies_list=movies, tv_shows=tv_shows)
    flag = o.se(message=o.MESSAGE)
    if flag:
        o.commit()
    else:
        print("email not send and not committed to the DB.")


