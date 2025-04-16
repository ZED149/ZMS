

# this file includes the MessageGenerator class


class MessageGenerator:
    # Methods

    @classmethod
    # no_reply_movies_added
    def no_reply_movies_added(cls, receiver_name: str, list_of_movies: list
                              ,tv_shows: dict) -> str:
        """
        Returns a message containing the name of the receiver.
        :param receiver_name: Name of the receiver.
        :param list_of_movies: List containing name of movies to iterate and append on.
        :return message: Final string that contains the whole email body
        """

        include_movies = True
        include_tv_shows = True
        # check if movies list is empty dont include added movies section in the email
        if not list_of_movies:
            include_movies = False
        # check if tv shows dict is empty dont include in added tv_shows section in the email
        if not tv_shows:
            include_tv_shows = False
        
        # start generating email
        message = '''
<!DOCTYPE html>
  <html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Movie & TV Show Updates</title>
    <style>
      body {
        margin: 0;
        padding: 0;
        font-family: Arial, sans-serif;
        background-color: #f4f4f4;
      }
      .email-container {
        max-width: 600px;
        margin: 0 auto;
        background: #ffffff;
        border-radius: 8px;
        overflow: hidden;
      }
      .header {
        background-color: #111827;
        color: #ffffff;
        text-align: center;
        padding: 30px 20px 20px 20px;
      }
      .logo {
        max-width: 120px;
        margin-bottom: 10px;
      }
      .content {
        padding: 20px;
      }
      .section-title {
        font-size: 18px;
        font-weight: bold;
        margin-top: 30px;
        margin-bottom: 10px;
        color: #111827;
      }
      .movie {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
        border-bottom: 1px solid #e0e0e0;
        padding-bottom: 15px;
      }
      .movie img {
        width: 80px;
        height: auto;
        border-radius: 4px;
        margin-right: 15px;
      }
      .movie-details {
        flex: 1;
      }
      .movie-title {
        font-size: 16px;
        font-weight: bold;
        margin: 0;
      }
      .movie-info {
        font-size: 14px;
        color: #666666;
        margin-top: 4px;
      }
      .ceo-info {
        margin-top: 30px;
        padding: 15px;
        border-top: 1px solid #e0e0e0;
        font-size: 14px;
        color: #333333;
      }
      .ceo-name {
        font-weight: bold;
        margin-top: 10px;
      }
      .footer {
        text-align: center;
        font-size: 13px;
        color: #999999;
        padding: 20px;
      }
      @media (max-width: 600px) {
        .movie {
          flex-direction: column;
          align-items: flex-start;
        }
        .movie img {
          margin-bottom: 10px;
        }
      }
    </style>
  </head>
  <body>
    <div class="email-container">
      <div class="header">
        <img src="cid:image1" alt="Company Logo" class="logo">
        <h1>🎬 Weekly Movies & TV Show Updates</h1>
      </div>
      <div class="content">'''
    
        # adding receiver name to email
        message = message + f'<p>Hi {receiver_name},</p>'
    
        # appending it back to the email
        message = message + '''
      <p>We've just added some exciting new titles to our collection. Check them out below!</p>
        '''
        # check for movies
        if include_movies:
          message = message + '''
          <!-- Movies -->
          <div class="section-title">🎬 New Movies Added</div>

          <div class="movie">
          <div class="movie-details">
          '''
    
          # adding updated/added movies
          for movie in list_of_movies:
              message = message + f'<p class="movie-title">{movie}</p>'
                
          # appeding it back with the code
          message = message + '''
          </div>
        </div>'''
        
        # check for tv_shows
        if include_tv_shows:
          message = message + '''  
        <!-- Tv Shows -->
        <div class="section-title">📺 New TV Shows Added</div>

        <div class="movie">
        <div class="movie-details">
        '''
          
          # adding new tv shows 
          for key, val in tv_shows.items():
              message = message + f'<p class="movie-title">{key}</p>'

          # appending it back to the code
          message = message + '''
          </div>
        </div>'''

        # appending the footer part of the email
        message = message + '''
      <p>👉 <a href="#" style="color:#111827;text-decoration:none;font-weight:bold;">Browse full catalog</a></p>

      <div class="ceo-info">
        <p>Thank you for being part of our entertainment family!</p>
        <p class="ceo-name">Salman Ahmad<br>CEO, ZED</p>
        <!-- Optional CEO signature -->
        <!-- <img src="cid:image1" alt="CEO Signature" style="margin-top:10px;"> -->
      </div>
    </div>
    <div class="footer">
      You are receiving this email because you subscribed to updates.<br>
      <a href="#" style="color: #999;">Unsubscribe</a>
    </div>
  </div>
</body>
</html>
'''
        return message

    
