from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

Venues_Geners = db.Table('Venues_Geners',
                         db.Column('venue_id', db.Integer,
                                   db.ForeignKey('Venue.id')),
                         db.Column('Genres_id', db.Integer,
                                   db.ForeignKey('Genres.id'))
                         )

Artists_Geners = db.Table('Artists_Geners',
                          db.Column('Artist_id', db.Integer,
                                    db.ForeignKey('Artist.id')),
                          db.Column('Genres_id', db.Integer,
                                    db.ForeignKey('Genres.id'))
                          )


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Shows(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        "Artist.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        "Venue.id"), nullable=False)
    start_time = db.Column(db.DateTime(timezone=True), nullable=False)
    venues = db.relationship('Venue', backref="venue")
    artisit = db.relationship('Artist', backref="artis")


class Genres(db.Model):
    __tablename__ = 'Genres'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True)

    def __repr__(self):
        return f'<Genres id={self.id} name={self.name} >'


class Cities(db.Model):
    __tablename__ = 'Cities'
    id = db.Column(db.Integer, unique=True)
    city = db.Column(db.String(), primary_key=True)
    state = db.Column(db.String(), primary_key=True)
    venues = db.relationship('Venue', backref="list")
    Artists = db.relationship('Artist', backref="ArtistList")

    def __repr__(self):
        return f'<Cities id={self.id} city={self.city} state={self.state}>'


class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey(
        "Cities.id"), nullable=False)
    genres = db.relationship(
        'Genres',  secondary=Venues_Geners, backref="list")
    address = db.Column(db.String(), nullable=False)
    phone = db.Column(db.String(), nullable=False)
    website = db.Column(db.String(), nullable=False)
    image_link = db.Column(db.String(), nullable=False)
    facebook_link = db.Column(db.String(), nullable=False)
    seeking_talent = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(), nullable=False)
    shows = db.relationship(
        'Shows', backref="all_shows")

    def __repr__(self):
        return f"""
            <Venue id={self.id}
                    name={self.name}
                    city_id={self.city_id}
                    address={self.address}
                    phone={self.phone}
                    website={self.website}
                    image_link={self.image_link}
                    facebook_link={self.facebook_link}
                    seeking_talent={self.seeking_talent}
                    seeking_description={self.seeking_description}
                    >

                """


class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(),  nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey(
        "Cities.id"), nullable=False)
    genres = db.relationship(
        'Genres',  secondary=Artists_Geners, backref="ArtistList")
    phone = db.Column(db.String(),  nullable=False)
    website = db.Column(db.String(), nullable=False)
    image_link = db.Column(db.String(), nullable=False)
    facebook_link = db.Column(db.String(), nullable=False)
    seeking_venue = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(), nullable=False)
    shows = db.relationship(
        'Shows', backref="all_artist_shows")

    def __repr__(self):
        return f"""
            <Artist id={self.id}
                    name={self.name}
                    city_id={self.city_id}
                    phone={self.phone}
                    website={self.website}
                    image_link={self.image_link}
                    facebook_link={self.facebook_link}
                    seeking_venue={self.seeking_venue}
                    seeking_description={self.seeking_description}
                    >

                """
