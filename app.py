#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel

from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *

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
  term = request.form.get("search_term", " ")
  query = Venue.query.filter(Venue.name.ilike(f"%{term}%")).all()
  response = {
    "count": len(query),
    "data": [
      venue.search for venue in query
    ]
  }
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = Venue.query.get(venue_id).complete
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

  # print("form", form.seeking_talent.data, request.form["seeking_talent"], vars(form))
  print(vars(form))
  try:
      new_venue = Venue(
        name=request.form["name"],
        city=request.form["city"],
        state=request.form["state"],
        address=request.form["address"],
        phone=request.form["phone"],
        genres=request.form.getlist("genres"),
        facebook_link=request.form["facebook_link"],
        seeking_talent=form["seeking_talent"].data,
        seeking_description=request.form["seeking_description"]
      )

      print(new_venue)

      db.session.add(new_venue)
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
      print("error occurred")
      flash('An error occurred. Venue ' +
            request.form['name'] + " could not be listed")
      db.session.rollback()
  finally:
      db.session.close()
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
      flash('Venue was successfully deleted!')
      jsonify({ "error": None, "data": "ok" })
  except:
      flash("An error occurred. Venue could not be deleted")
      db.session.rollback()
      jsonify({ "error": 400, "data": None })
  finally:
      db.session.close()
  return render_template('pages/home.html')

#  ----------------------------------------------------------------
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
  term = request.form.get("search_term", " ")
  query = Artist.query.filter(Artist.name.ilike(f"%{term}%")).all()
  response = {
    "count": len(query),
    "data": [
      artist.search for artist in query
    ]
  }
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  artist = Artist.query.get(artist_id).complete
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
  form = ArtistForm(request.form)
  try:
      artist = Artist.query.filter_by(id = artist_id).first()

      artist.name = form.name.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.genres = form.genres.data
      artist.facebook_link = form.facebook_link.data
      artist.seeking_venue = form.seeking_venue.data
      artist.seeking_description = form.seeking_description.data

      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was succesfully edited!')
  except:
      flash('An error occurred. Artist ' +
            request.form['name'] + "could not be listed")
      db.session.rollback()
  finally:
      db.session.close()
  
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter_by(id = venue_id).first().complete
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  try:
      venue = Venue.query.filter_by(id = venue_id).first()

      venue.name = form.name.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.address = form.address.data
      venue.phone = form.phone.data
      venue.genres = form.genres.data
      venue.facebook_link = form.facebook_link.data
      venue.seeking_talent = form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data

      print(venue)

      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was succesfully edited!')
  except:
      flash('An error occurred. Venue ' +
            request.form['name'] + "could not be listed")
      db.session.rollback()
  finally:
      db.session.close()
  
  return redirect(url_for('show_venue', venue_id=venue_id))

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  try:
      artist = artist.query.get(artist_id)
      db.session.delete(artist)
      db.session.commit()
      flash('artist was successfully deleted!')
  except:
      flash("An error occurred. artist could not be deleted")
      db.session.rollback()
  finally:
      db.session.close()
  return render_template('pages/home.html')

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
  form = ArtistForm(request.form)
  try:
      new_artist = Artist(
        name=request.form["name"],
        city=request.form["city"],
        state=request.form["state"],
        phone=request.form["phone"],
        genres=request.form.getlist("genres"),
        facebook_link=request.form["facebook_link"],
        
        seeking_venue=form["seeking_venue"].data,
        seeking_description=request.form["seeking_description"]
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
  } for show in Show.query.order_by(Show.start_time.desc()).all()]
  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
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
