
from .episode import Episode
# Contains TVShow class

class TVShow:
    # GLOBAL variables
    NEW_TV_SHOW_ADDED = False
    UPDATED_TV_SHOWS = False

    # data members
    tv_show_id = None
    tv_show_name = None
    created_date = None
    last_modified_date = None
    channel_name = None
    episodes = None
    newly_added = None

    # constructor
    def __init__(self, tv_show_id: int = None, tv_show_name: str = None, 
                 created_date: str = None,
                 last_modified_date: str = None,
                 channel_name: str = None,
                 episodes: Episode = None,
                 newly_added: bool = False) -> None:
        # assigning values to data members
        self.tv_show_id = tv_show_id
        self.tv_show_name = tv_show_name
        self.created_date = created_date
        self.last_modified_date = last_modified_date
        self.channel_name = channel_name
        self.episodes = episodes
        self.newly_added = newly_added

    # __str__
    def __str__(self):
        message = f'[TV SHOW] [{self.tv_show_name}] [{self.channel_name}] --> ['
        for episode in self.episodes:
            message = message + episode.__str__()
        message = message + ']'
        return message
    
    # get_year
    def get_year(self):
        "Tue May  6 13:32:56 2025"
        year = self.created_date[-4:]
        return year