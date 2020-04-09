#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import datetime

from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    
    genres = db.Column(db.ARRAY(db.String))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))

    show = db.relationship("Show", backref="venue", lazy=True)

    def __repr__(self):
      return f"<Venue {self.name}>"

    @property
    def area(self):
      return {
        "city": self.city,
        "state": self.state
      }

    @property
    def serialize(self):
      return {
        "id": self.id,
        "name": self.name, 
      }

    @property
    def complete(self):
      upcoming_shows = db.session.query(Show).filter(Show.venue_id == self.id, Show.start_time > datetime.utcnow())
      past_shows = db.session.query(Show).filter(Show.venue_id == self.id, Show.start_time < datetime.utcnow())
      
      return {
        "id": self.id,
        "name": self.name,
        "genres": self.genres,
        "address": self.address,
        "phone": self.phone,
        "website": self.website,
        "facebook_link": self.facebook_link,
        "seeking_talent": self.seeking_talent,
        "seeking_description": self.seeking_description,
        "image_link": self.image_link,
        "upcoming_shows": [{ 
          "artist_id": show.artist_id, 
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for show in upcoming_shows.all()],
        "upcoming_shows_count": upcoming_shows.count(),
        "past_shows": [{ 
          "artist_id": show.artist_id, 
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for show in past_shows.all()],
        "past_shows_count": past_shows.count()
      }

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    
    show = db.relationship("Show", backref="artist", lazy=True)

    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)

    @property
    def complete(self):
      upcoming_shows = db.session.query(Show).filter(Show.venue_id == self.id, Show.start_time > datetime.utcnow())
      past_shows = db.session.query(Show).filter(Show.venue_id == self.id, Show.start_time < datetime.utcnow())

      return {
        "id": self.id,
        "name": self.name,
        "city": self.city,
        "state": self.state,
        "phone": self.phone,
        "website": self.website,
        "image_link": self.image_link,
        "facebook_link": self.facebook_link,
        "seeking_venue": self.seeking_venue,
        "seeking_description": self.seeking_description,
        "upcoming_shows": [{ 
          "artist_id": show.artist_id, 
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for show in upcoming_shows.all()],
        "upcoming_shows_count": upcoming_shows.count(),
        "past_shows": [{ 
          "artist_id": show.artist_id, 
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for show in past_shows.all()],
        "past_shows_count": past_shows.count()
      }

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Show {self.start_time}>"

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format,  locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  ----------------------------------------------------------------
#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  areas = [v.area for v in Venue.query.distinct(Venue.city, Venue.state).all()]
  for area in areas:
    area["venues"] = [
      v.serialize for v in Venue.query.filter_by(
        city = area["city"], 
        state = area["state"]
      ).all()
    ]
  return render_template('pages/venues.html', areas=areas, raw=str(areas))


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = Venue.query.filter_by(id = venue_id).first().complete
  return render_template('pages/show_venue.html', venue=venue)

#  ----------------------------------------------------------------
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  try:
      new_venue = Venue(
        name=request.form["name"],
        city=request.form["city"],
        state=request.form["state"],
        address=request.form["address"],
        phone=request.form["phone"],
        genres=request.form.getlist("genres"),
        facebook_link=request.form["facebook_link"]
      )

      db.session.add(new_venue)
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
      flash('An error occurred. Venue ' +
            request.form['name'] + "could not be listed")
      db.session.rollback()
  finally:
      db.session.close()
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  artist = Artist.query.filter_by(id = artist_id).first().complete
  return render_template("pages/show_artist.html", artist=artist)

#  ----------------------------------------------------------------
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter_by(id = artist_id).first().complete
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter_by(id = venue_id).first().complete
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  ----------------------------------------------------------------
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Artist record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  try:
      new_artist = Artist(
        name=request.form["name"],
        city=request.form["city"],
        state=request.form["state"],
        phone=request.form["phone"],
        genres=request.form.getlist("genres"),
        facebook_link=request.form["facebook_link"]
      )

      db.session.add(new_artist)
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
      flash('An error occurred. Venue ' +
            request.form['name'] + "could not be listed")
      db.session.rollback()
  finally:
      db.session.close()

  return render_template('pages/home.html')

#  ----------------------------------------------------------------
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():  
  shows = [{
    "venue_id": show.venue_id,
    "artist_id": show.artist_id,
    "artist_name": Artist.query.filter_by(id=show.artist_id).one().name,
    "venue_name": Venue.query.filter_by(id=show.venue_id).one().name,
    "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
  } for show in Show.query.order_by("start_time").all()]
  print(shows)
  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  try:
      new_show = Show(
        artist_id=request.form["artist_id"],
        venue_id=request.form["venue_id"],
        start_time=request.form["start_time"]
      )

      db.session.add(new_show)
      db.session.commit()
      # on successful db insert, flash success
      flash('Show was successfully listed!')
  except:
      flash('An error occurred. Venue ' +
            request.form['name'] + "could not be listed")
      db.session.rollback()
  finally:
      db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
