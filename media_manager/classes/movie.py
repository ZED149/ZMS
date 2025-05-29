

# Contains Movie class


class Movie:
    # data members
    movie_name = None
    release_year = None
    genres = None
    rating = None
    small_cover_image = None

    # constructor
    def __init__(self, movie_name: str = None, release_year: str = None, 
                 genres: str = None, rating: str = None,
                 small_cover_image: str = None):
        # initializing data members
        self.movie_name = movie_name
        self.release_year = release_year
        self.genres = genres
        self.rating = rating
        self.small_cover_image = small_cover_image

    # __str__
    def __str__(self):
        message = f'[MOVIE] [{self.movie_name}] ({self.release_year}) ({self.rating}/10)'
        return message