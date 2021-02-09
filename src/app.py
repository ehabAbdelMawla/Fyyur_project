#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
# db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Secondary Tables.
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    # date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(value, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/', methods=['GET', 'POST', 'DELETE'])
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    return render_template('pages/venues.html', areas=filter(lambda city: len(city.venues) > 0,
                                                             Cities.query.order_by("id").all()))


@ app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get("search_term", '')
    result = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

    response = {}
    response["count"] = len(result)
    response["data"] = result

    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@ app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

    venue = Venue.query.get(venue_id)

    past_shows = list(filter(isPast, venue.shows))
    upcoming_shows = list(filter(isUpComing, venue.shows))
    venueCity = Cities.query.filter_by(id=venue.city_id).first()

    return render_template('pages/show_venue.html', venue=venue, cityObj=venueCity, past_shows=past_shows, upcoming_shows=upcoming_shows)


#  Create Venue
#  ----------------------------------------------------------------
@ app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
        city = workOnCity(request)

        geners = workOnGeners(request)

        seeking_talent = workOnSeekingTalent(request)

        venue = Venue(name=request.form['name'],
                      city_id=city.id,
                      genres=geners,
                      address=request.form['address'],
                      phone=request.form['phone'],
                      website=request.form['website_link'],
                      image_link=request.form['image_link'],
                      facebook_link=request.form['facebook_link'],
                      seeking_talent=seeking_talent,
                      seeking_description=request.form['seeking_description'],
                      )

        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')


@ app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        ven = Venue.query.get(venue_id)
        db.session.delete(ven)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for("index"))

#  Artists
#  ----------------------------------------------------------------


@ app.route('/artists')
def artists():

    return render_template('pages/artists.html', artists=Artist.query.order_by("id").all())


@ app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get("search_term", '')
    result = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

    response = {}
    response["count"] = len(result)
    response["data"] = result

    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

    artist = Artist.query.filter_by(id=artist_id).first()
    past_shows = list(filter(isPast, artist.shows))
    upcoming_shows = list(filter(isUpComing, artist.shows))
    artistCity = Cities.query.filter_by(id=artist.city_id).first()
    return render_template('pages/show_artist.html', artist=artist, cityObj=artistCity, past_shows=past_shows, upcoming_shows=upcoming_shows)

#  Update
#  ----------------------------------------------------------------


@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    artistsCity = Cities.query.filter_by(id=artist.city_id).first()

    return render_template('forms/edit_artist.html', form=form, artist=artist, cityObj=artistsCity, selectedGeners=json.dumps(list(map(lambda gener: gener.name, artist.genres))))


@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    try:
        city = workOnCity(request)

        geners = workOnGeners(request)

        seeking_venue = workOnSeekingTalent(request)
        # ... Update Values
        editartist = Artist.query.get(artist_id)
        editartist.name = request.form['name']
        editartist.city_id = city.id
        editartist.genres = geners
        editartist.phone = request.form['phone']
        editartist.website = request.form['website_link']
        editartist.image_link = request.form['image_link']
        editartist.facebook_link = request.form['facebook_link']
        editartist.seeking_talent = seeking_venue
        editartist.seeking_description = request.form['seeking_description']
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    venueCity = Cities.query.filter_by(id=venue.city_id).first()
    return render_template('forms/edit_venue.html', form=form, venue=venue, cityObj=venueCity, selectedGeners=json.dumps(list(map(lambda gener: gener.name, venue.genres))))


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
        city = workOnCity(request)

        geners = workOnGeners(request)

        seeking_talent = workOnSeekingTalent(request)
    # ... Update Values
        editVenue = Venue.query.get(venue_id)
        editVenue.name = request.form['name']
        editVenue.city_id = city.id
        editVenue.genres = geners
        editVenue.address = request.form['address']
        editVenue.phone = request.form['phone']
        editVenue.website = request.form['website_link']
        editVenue.image_link = request.form['image_link']
        editVenue.facebook_link = request.form['facebook_link']
        editVenue.seeking_talent = seeking_talent
        editVenue. seeking_description = request.form['seeking_description']
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    try:
        city = workOnCity(request)
        geners = workOnGeners(request)
        seeking_venue = workOnSeekingTalent(request)

        artist = Artist(
            name=request.form['name'],
            city_id=city.id,
            genres=geners,
            phone=request.form['phone'],
            website=request.form['website_link'],
            image_link=request.form['image_link'],
            facebook_link=request.form['facebook_link'],
            seeking_venue=seeking_venue,
            seeking_description=request.form['seeking_description']
        )
        print(artist)
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except Exception as e:
        db.session.rollback()
        print(e)
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')

# Delete Artists


@ app.route('/artists/<int:artists_id>', methods=['DELETE'])
def delete_artist(artists_id):
    try:
        artist = Artist.query.get(artists_id)
        db.session.delete(artist)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for("index"))

#  Shows
#  ----------------------------------------------------------------


@ app.route('/shows')
def shows():
    return render_template('pages/shows.html', shows=Shows.query.order_by("id").all())


@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
        artistAvailability = isArtistAvailability(
            request.form["artist_id"], request.form["start_time"])
        print(artistAvailability)
        print(artistAvailability)
        print(artistAvailability)
        print(artistAvailability)
        if artistAvailability:
            newShow = Shows(
                artist_id=request.form["artist_id"],
                venue_id=request.form["venue_id"],
                start_time=request.form["start_time"]
            )
            db.session.add(newShow)
            db.session.commit()
            # on successful db insert, flash success
            flash('Show was successfully listed!')
        else:
            flash(
                f'Artist is Not Available in { dateutil.parser.parse(request.form["start_time"]).date()}')
    except Exception as ex:
        db.session.rollback()
        print(ex)
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')


#  Help Methods
def addCityIfNotExist(cityObj):
    """
    Add City Record if not exists and return object if exist
    """
    try:
        db.session.add(cityObj)
        db.session.commit()
        return cityObj
    except:
        db.session.rollback()
        cityFullObject = Cities.query.filter(Cities.city == cityObj.city).filter(
            Cities.state == cityObj.state).first()
        return cityFullObject


def workOnCity(request):
    city = Cities(id=(Cities.query.count()+1),
                  city=request.form['city'],
                  state=request.form['state'])
    return addCityIfNotExist(city)


def addGenersIFNotExists(geners=[]):
    """
    Add geners Name in Geners Table if not exists and append object if exist
    """
    result = []
    temp = None
    for gener in geners:
        try:
            temp = Genres(name=gener)
            db.session.add(temp)
            db.session.commit()
            result.append(temp)
        except:
            db.session.rollback()
            exitGener = Genres.query.filter(Genres.name == gener).first()
            result.append(exitGener)
    return result


def workOnGeners(request):
    geners = request.form.to_dict(flat=False)["genres"]
    return addGenersIFNotExists(geners)


def workOnSeekingTalent(request):
    seeking_talent = False
    try:
        seeking_talent = request.form['seeking_talent'] == 'y'
    except:
        seeking_talent = False
    finally:
        return seeking_talent
#----------------------------------------------------------------------------#
# Date Comarison
#----------------------------------------------------------------------------#


def isPast(show):
    return show.start_time <= datetime.now(timezone.utc)


def isUpComing(show):
    return show.start_time > datetime.now(timezone.utc)

#----------------------------------------------------------------------------#
# Time Availability
#----------------------------------------------------------------------------#


def isArtistAvailability(artist_id, date):
    artist = Artist.query.get(artist_id)
    newShowDay = dateutil.parser.parse(date)
    for show in artist.shows:
        if show.start_time.date() == newShowDay.date():
            return False
    return True

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
