# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import babel
import dateutil.parser
from datetime import datetime
from sqlalchemy import desc
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from forms import *
import logging
from logging import Formatter, FileHandler


# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#


app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# the models need to be imported after the app is created
from models import db, Venue, Artist, Show
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    new_venues = Venue.query.order_by(desc('id')).limit(10).all()
    new_artists = Artist.query.order_by(desc('id')).limit(10).all()

    return render_template('pages/home.html', new_venues=new_venues, new_artists=new_artists)


#  Venues
#  -------------------------------------------------------------------------- #

@app.route('/venues')
def venues():
    venues = Venue.query.all()
    areas = Venue.query.distinct(Venue.city, Venue.state).order_by('state', 'city').all()
    data = []
    for area in areas:
        data.append({
            "city": area.city,
            "state": area.state,
            "venues": [{
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len([show for show in venue.show if show.start_time > datetime.now()])
            } for venue in venues if
                venue.city == area.city and venue.state == area.state]
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['GET', 'POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    venue_results = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()

    data = []
    for venue in venue_results:
        data.append({
            "id": venue.id,
            "name": venue.name
        })
    results = {
        "count": len(venue_results),
        "data": data
    }
    return render_template('pages/search_venues.html', results=results, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    upcoming_shows = db.session.query(Show).join(Venue). \
        filter(
        Show.venue_id == venue_id,
        Show.start_time > datetime.now()
    ).all()
    past_shows = db.session.query(Show).join(Venue). \
        filter(
        Show.venue_id == venue_id,
        Show.start_time < datetime.now()
    ).all()

    upcoming_shows_count = len(upcoming_shows)
    past_shows_count = len(past_shows)

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "city": venue.city,
        "state": venue.state,
        "address": venue.address,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_venue": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "upcoming_shows_count": upcoming_shows_count,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": past_shows_count,
        "past_shows": past_shows
    }

    artist_search_term = request.args.get('artist_search_term', 'null')
    artist_results = Artist.query.filter(Artist.name.ilike('%' + artist_search_term + '%')).all()
    artist_data = []
    for artist in artist_results:
        artist_data.append({
            "id": artist.id,
            "name": artist.name
        })
    results = {
        "count": len(artist_results),
        "artist_search_term": artist_search_term,
        "artist_data": artist_data
    }

    return render_template('pages/show_venue.html', venue=data, results=results)


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
        name = request.form.get("name")
        city = request.form.get("city")
        state = request.form.get("state")
        address = request.form.get("address")
        phone = request.form.get("phone")
        genres = request.form.getlist("genres")
        image_link = request.form.get("image_link")
        website = request.form.get("website")
        facebook_link = request.form.get("facebook_link")
        seeking_talent = "seeking_talent" in request.form
        seeking_description = request.form.get("seeking_description")
        new_venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres,
                          image_link=image_link, website=website, facebook_link=facebook_link,
                          seeking_talent=seeking_talent, seeking_description=seeking_description)
        db.session.add(new_venue)
        db.session.commit()
        flash(('The venue ' + request.form['name'] + ' was successfully listed!'), 'alert-success')
    except:
        flash(('An error occurred. The venue ' + request.form['name'] + ' could not be listed.'), 'alert-danger')
        db.session.rollback()
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash('Success! The venue has been deleted.', 'alert-success')
    except:
        flash('An error occurred. The venue could not be deleted.', 'alert-danger')
        db.session.rollback()
    finally:
        db.session.close()
    return render_template('pages/home.html')


#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    return render_template('pages/artists.html', artists=Artist.query.all())


@app.route('/artists/search', methods=['GET', 'POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    artist_results = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
    data = []
    for artist in artist_results:
        data.append({
            "id": artist.id,
            "name": artist.name
        })
    results = {
        "count": len(artist_results),
        "data": data
    }
    return render_template('pages/search_artists.html', results=results, search_term=request.form.get(
        'search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)

    upcoming_shows = db.session.query(Show).join(Venue). \
        filter(
        Show.artist_id == artist_id,
        Show.start_time > datetime.now()
    ).all()
    past_shows = db.session.query(Show).join(Venue). \
        filter(
        Show.artist_id == artist_id,
        Show.start_time < datetime.now()
    ).all()

    upcoming_shows_count = len(upcoming_shows)
    past_shows_count = len(past_shows)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "upcoming_shows_count": upcoming_shows_count,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": past_shows_count,
        "past_shows": past_shows
    }

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    try:
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        phone = request.form.get('phone')
        genres = request.form.getlist('genres')
        image_link = request.form.get('image_link')
        website = request.form.get('website')
        facebook_link = request.form.get('facebook_link')
        seeking_venue = "seeking_venue" in request.form
        seeking_description = request.form.get('seeking_description')
        new_artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, image_link=image_link,
                            website=website, facebook_link=facebook_link, seeking_venue=seeking_venue,
                            seeking_description=seeking_description)
        db.session.add(new_artist)
        db.session.commit()
        flash(('Artist ' + request.form['name'] + ' was successfully edited!'), 'alert-success')
    except:
        flash(('An error occurred.  Artist: ' + request.form['name'] + ' could not be edited.'), 'alert-danger')
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm(request.form)
    try:
        venue = Venue.query.get(venue_id)
        name = request.form.get("name", venue.name)
        city = request.form.get("city", venue.city)
        state = request.form.get("state", venue.state)
        address = request.form.get("address", venue.address)
        phone = request.form.get("phone", venue.phone)
        genres = request.form.getlist("genres", venue.genres)
        image_link = request.form.get("image_link", venue.image_link)
        website = request.form.get("website", venue.website)
        facebook_link = request.form.get("facebook_link", venue.facebook_link)
        seeking_talent = "seeking_talent" in request.form
        seeking_description = request.form.get("seeking_description", venue.seeking_description)
        edited_venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres,
                             image_link=image_link, website=website, facebook_link=facebook_link,
                             seeking_talent=seeking_talent, seeking_description=seeking_description)
        db.session.add(edited_venue)
        db.session.commit()
        flash(('The venue ' + request.form['name'] + ' was successfully listed!'), 'alert-success')
    except:
        flash(('An error occurred. The venue ' + request.form['name'] + ' could not be listed.'), 'alert-danger')
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form)
    try:
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        phone = request.form.get('phone')
        genres = request.form.getlist('genres')
        image_link = request.form.get('image_link')
        website = request.form.get('website')
        facebook_link = request.form.get('facebook_link')
        seeking_venue = "seeking_venue" in request.form
        seeking_description = request.form.get('seeking_description')
        new_artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, image_link=image_link,
                            website=website, facebook_link=facebook_link, seeking_venue=seeking_venue,
                            seeking_description=seeking_description)
        db.session.add(new_artist)
        db.session.commit()
        flash(('Artist ' + request.form['name'] + ' was successfully listed!'), 'alert-success')
    except:
        flash(('An error occurred.  Artist: ' + request.form['name'] + ' could not be listed.'), 'alert-danger')
        db.session.rollback()
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.route('/artists/<int:artist_id>/delete', methods=['POST'])
def delete_artist(artist_id):
    try:
        artist = Artist.query.get(artist_id)
        db.session.delete(artist)
        db.session.commit()
        flash('Success! The artist has been deleted.', 'alert-success')
    except:
        flash('An error occurred. The artist could not be deleted.', 'alert-danger')
        db.session.rollback()
    finally:
        db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # all upcoming shows ordered so the next closest upcoming show starts the list and then
    # as we progress down the list the show dates get farther out
    shows = Show.query.filter(Show.start_time > datetime.now()).order_by('start_time').all()
    return render_template('pages/shows.html', shows=shows)


@app.route('/shows/create', methods=['GET'])
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)
    try:
        artist_id = request.form.get("artist_id")
        venue_id = request.form.get("venue_id")
        start_time = request.form.get("start_time")
        new_show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
        db.session.add(new_show)
        db.session.commit()
        flash('The show was successfully listed!', 'alert-success')
    except:
        flash('An error occurred. The show could not be created.', 'alert-danger')
        db.session.rollback()
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.route('/shows/search', methods=['GET', 'POST'])
def search_shows():
    search_term = request.form.get('search_term', '')
    venue_results = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
    artist_results = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
    all_results = venue_results + artist_results

    venue_data = []
    artist_data = []
    for venue in venue_results:
        venue_data.append({
            "id": venue.id,
            "name": venue.name,
            "image_link": venue.image_link,
            "num_upcoming_shows": len([show for show in venue.show if show.start_time > datetime.now()]),
            "upcoming_shows": [{
                "start_time": show.start_time,
                "artist_id": show.artist_id
            } for show in venue.show if show.start_time > datetime.now()]
        })
    for artist in artist_results:
        artist_data.append({
            "id": artist.id,
            "name": artist.name,
            "image_link": artist.image_link,
            "num_upcoming_shows": len([show for show in artist.show if show.start_time > datetime.now()]),
            "upcoming_shows": [{
                "start_time": show.start_time,
                "artist_id": show.artist_id
            } for show in artist.show if show.start_time > datetime.now()]
        })
    data = venue_data + artist_data
    results = {
        "count": len(all_results),
        "data": data,
        "venue_data": venue_data,
        "artist_data": artist_data
    }

    return render_template('pages/search_shows.html', results=results, search_term=request.form.get('search_term', ''))


#  Error Handling
#  ----------------------------------------------------------------

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


# ---------------------------------------------------------------------------- #
# Launch.
# ---------------------------------------------------------------------------- #

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
