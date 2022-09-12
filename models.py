from ariadne import QueryType, MutationType
from uuid import uuid4
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    )
import os

db = SQLAlchemy()
mutation = MutationType()
query = QueryType()

database_path="postgresql://postgres:seoisoe5i73@localhost:5432/gamereviewsdb"

def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)

#----------Models----------
class User(db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(40), nullable=False)
    password = Column(String(40), nullable=False)
    username = Column(String(25), nullable=False)
    reviews = db.relationship(
        'Review',
        cascade = 'all, delete-orphan',
        backref = db.backref('review')
    )
    def __init__(self, email, password, username):
        self.email = email
        self.password = password
        self.username = username
    
    def insert(self):
        db.session.add(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'email': self.email,
            'password': self.password,
            'username': self.username,
        }
class Game(db.Model):
    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    background_image = Column(String(200), nullable=False)
    description = Column(String, nullable=False)
    rawg_id = Column(Integer, nullable=False)
    released = Column(String(25), nullable=False)
    title = Column(String(25), nullable=False)
    reviews = db.relationship(
        'Review',
        cascade = 'all, delete-orphan',
        backref = db.backref('review')
    )

    def __init__(self, background_image, description, rawg_id, released, title):
        self.background_image = background_image
        self.description = description
        self.rawg_id = rawg_id
        self.released = released
        self.title = title
    
    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    def format(self):
        return {
            'id': self.id,
            'background_image': self.background_image,
            'description': self.description,
            'rawg_id' : self.rawg_id,
            'released': self.released,
            'title': self.title
        }

class Review(db.Model):
    __tablename__ = 'review'
    id = Column(Integer, primary_key=True)
    game_id = Column(
        Integer,
        ForeignKey('game.id'),
        nullable=False
    )
    rating = Column(Integer, nullable=True)
    context = Column(String(200), nullable=True)
    user_id = Column(
        Integer,
        ForeignKey('user.id'),
        nullable = False
    )

    def __init__(self, rating, review,):
        self.rating = rating
        self.review = review
    
    def insert(self):
        db.session.add(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'rating': self.rating,
            'review': self.review,
        }

#----------Resolvers----------
@query.field('games')
def games(*_):
    return [game.format() for game in Game.query.all()]