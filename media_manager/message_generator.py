

# this file includes the MessageGenerator class

import os
from dotenv import load_dotenv
from .classes import Movie, TVShow

# loading our enviournment
load_dotenv(dotenv_path="/home/salman/ZMS/media_manager/.env")

class MessageGenerator:
  # Private data members
  __link_to_full_catalog = os.getenv("SERVER_IP")
  # Methods

  @classmethod
  # no_reply_movies_added
  def no_reply_movies_added(cls, receiver_name: str, list_of_movies: Movie
                            ,tv_shows: TVShow) -> str:
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
      
      # starting generating email
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
        <div class="section-title">🎬 New Movies Added</div>'''
        for movie in list_of_movies:
          if movie.release_year == None:
              message = message + '''
            <div class="movie">
              <img src="#" alt="Avatar 2 Poster">
              <div class="movie-details">'''
              message = message + f'''<p class="movie-title">{movie.movie_name}</p>
              <p class="movie-info"></p>
              </div>
            </div> 
  '''
          else:
            message = message + f'''
            <div class="movie">
              <img src="{movie.small_cover_image}" alt="Avatar 2 Poster">
              <div class="movie-details">'''
            message = message + f'''<p class="movie-title">{movie.movie_name}</p>
              <p class="movie-info"> {movie.genres[0]} | {movie.release_year} | Rating: {movie.rating}</p>
              </div>
            </div>
          '''

      # check for tv_shows
      if include_tv_shows:
        # Newly Added TV Shows
        if tv_shows[0].NEW_TV_SHOW_ADDED:
            message = message + '''  
            <!-- Tv Shows -->
            <div class="section-title">📺 New TV Shows Added</div>''' 
            for tv_show in tv_shows:
                message = message + '''<div class="movie">
                <div class="movie-details">'''
                if tv_show.newly_added:
                  message = message + f'''<p class="movie-title">{tv_show.tv_show_name}</p>
                  <p class="movie-info">{tv_show.get_year()} | {tv_show.channel_name}</p>
              </div>
            </div>'''
        
        # Recenlty Updated TV Shows
        if tv_shows[0].UPDATED_TV_SHOWS:
            message = message + '''<div class="section-title">♻️ Recently Updated TV Shows</div>'''
            for tv_show in tv_shows:
              if not tv_show.newly_added:
                  message = message + '''<div class="movie">
                  <div class="movie-details">'''
                  message = message + f'''<p class="movie-title">{tv_show.tv_show_name}</p>
                  <p class="movie-info">{tv_show.get_year()} | {tv_show.channel_name}</p>
              </div>
            </div>'''

      # appending the footer part of the email
      message = message + f'''
    <p>👉 <a href="{cls.__link_to_full_catalog}" style="color:#111827;text-decoration:none;font-weight:bold;">Browse full catalog</a></p>

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

  @classmethod
  # error_in_zms (zms ==> ZED Media Server)
  def error_in_zms(cls, a_name, error: Exception) -> str:
      '''
        Generates an email markup with the error provided, to be send to the admin.
      '''
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
      <h1>Admin Management and Execution Panel</h1>
    </div>
'''
      message = message + f'''
<div class="content">
      <p>Hi {a_name},</p>
      <p>An Error occurred during the execution of ZMS automation script.</p>

      <div class="section-title">Error: {error.__class__.__name__}</div>

      <div class="movie">
        <div class="movie-details">
          <p class="movie-title">Error Details</p>
          <p class="movie-info">{error.__traceback__.tb_frame.f_code.co_filename} | {error.__traceback__.tb_frame.f_code.co_name} | {error.__traceback__.tb_lineno}</p>
        </div>
      </div>
'''
      message = message + '''
<div class="ceo-info">
        <p>Thank you for being part of our entertainment family!</p>
        <p class="ceo-name">Salman Ahmad<br>CEO, ZED</p>
        <!-- Optional CEO signature -->
        <!-- <img src="https://via.placeholder.com/100x40?text=Signature" alt="CEO Signature" style="margin-top:10px;"> -->
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
