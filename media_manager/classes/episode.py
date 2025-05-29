

# contains Episode class

class Episode:
    # data members
    episode_name = None
    created_date = None

    # constructor
    def __init__(self, episode_name: str = None, created_date: str = None) -> None:
        # assigning values to data members
        self.episode_name = episode_name
        self.created_date = created_date

    # __str__
    def __str__(self):
        return f"{self.episode_name}, "