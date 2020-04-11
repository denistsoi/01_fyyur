import datetime
from app import db

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
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String)

    show = db.relationship("Show", backref="venue", lazy=True)

    def __repr__(self):
      return f"<Venue {self.name} {self.seeking_talent}>"

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
      upcoming_shows = db.session.query(Show).filter(Show.venue_id == self.id, Show.start_time > datetime.datetime.utcnow())
      past_shows = db.session.query(Show).filter(Show.venue_id == self.id, Show.start_time < datetime.datetime.utcnow())
      
      return {
        "id": self.id,
        "name": self.name,
        "genres": self.genres,
        "city": self.city,
        "state": self.state,
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

    @property
    def search(self):
      upcoming_shows = db.session.query(Show).filter(Show.venue_id == self.id, Show.start_time > datetime.datetime.utcnow())
      return {
        "id": self.id,
        "name": self.name,
        "num_of_upcoming_shows": upcoming_shows.count()
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

    seeking_venue = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(120), nullable=True)

    @property
    def complete(self):
      upcoming_shows = db.session.query(Show).filter(Show.artist_id == self.id, Show.start_time > datetime.datetime.utcnow())
      past_shows = db.session.query(Show).filter(Show.artist_id == self.id, Show.start_time < datetime.datetime.utcnow())

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
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for show in upcoming_shows.all()],
        "upcoming_shows_count": upcoming_shows.count(),
        "past_shows": [{ 
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for show in past_shows.all()],
        "past_shows_count": past_shows.count()
      }

    @property
    def search(self):
      upcoming_shows = db.session.query(Show).filter(Show.venue_id == self.id, Show.start_time > datetime.datetime.utcnow())
      return {
        "id": self.id,
        "name": self.name,
        "num_of_upcoming_shows": upcoming_shows.count()
      }

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())

    def __repr__(self):
        return f"<Show {self.start_time}>"