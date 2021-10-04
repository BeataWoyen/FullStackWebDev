# ----------------------------------------------------------------------------#
# Imports & setups
# ----------------------------------------------------------------------------#
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(14), nullable=False)
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(500))

    # debugging - will print the id and name of each venue
    def __repr__(self):
        return f'<Venue ID: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, address:' \
               f' {self.address}, phone: {self.phone}, genres: {self.genres}, image_link: {self.image_link}, ' \
               f'website: {self.website}, facebook_link: {self.facebook_link}, seeking_talent: {self.seeking_talent}, ' \
               f'seeking_description: {self.seeking_description}, shows: {self.show}>'


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(14), nullable=False)
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(500))

    # debugging - will print the id and name of each artist
    def __repr__(self):
        return f'<Artist ID: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, ' \
               f'phone: {self.phone}, genres: {self.genres}, image_link: {self.image_link}, ' \
               f'website: {self.website}, facebook_link: {self.facebook_link}, seeking_venue: {self.seeking_venue}, ' \
               f'seeking_description: {self.seeking_description}, shows: {self.show}>'


class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    artist = db.relationship('Artist', backref='show', lazy=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    venue = db.relationship('Venue', backref='show', lazy=True)
    start_time = db.Column(db.DateTime(), nullable=False)
