from ariadne import QueryType, MutationType
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    Text
    )
from re import search
import os

db = SQLAlchemy()
mutation = MutationType()
query = QueryType()
#database_path="postgresql://postgres:seoisoe5i73@localhost:5432/gamereviewsdb"
database_path=(os.environ.get('DATABASE_URI'))
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db, compare_type=True)
    db.create_all()

#----------Models----------
class User(db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(40), nullable=False)
    password = Column(String(40), nullable=False)
    username = Column(String(25), nullable=False)
    games = db.relationship(
        'Review',
        cascade = 'all, delete-orphan',
        backref = db.backref('user')
    )
    def __init__(self, email, password, username):
        self.email = email
        self.password = password
        self.username = username
    
    def insert(self):
        db.session.add(self)
        db.session.commit()

#return the games relationship so graphql has access to it along with other values
    def format(self):
        return {
            'id': self.id,
            'email': self.email,
            'password': self.password,
            'username': self.username,
            'games' : self.games
        }
class Game(db.Model):
    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    background_image = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    rawg_id = Column(Integer, nullable=False)
    released = Column(String(25), nullable=False)
    title = Column(String(50), nullable=False)
    players = db.relationship(
        'Review',
        cascade = 'all, delete-orphan',
        backref = db.backref('game')
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

    #return the players relationship so graphql has access to it
    def format(self):
        return {
            'id': self.id,
            'background_image': self.background_image,
            'description': self.description,
            'players' : self.players,
            'rawg_id' : self.rawg_id,
            'released': self.released,
            'title': self.title
        }

class Review(db.Model):
    __tablename__ = 'review'
    id = Column(Integer, primary_key=True)
    context = Column(String(200), nullable=True)
    game_id = Column(
        Integer,
        ForeignKey('game.id'),
        nullable=False
    )
    rating = Column(Integer, nullable=True)
    user_id = Column(
        Integer,
        ForeignKey('user.id'),
        nullable = False
    )

    def __init__(self, context, game_id, rating, user_id):
        self.rating = rating
        self.context = context
        self.game_id = game_id
        self.user_id = user_id
    
    def insert(self):
        db.session.add(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'rating': self.rating,
            'context': self.context,
            'user_id': self.user_id,
            'game_id': self.game_id,
        }

#----------Resolvers----------

@query.field('gamesByString')
def gamesByString(*_, str=None):
    matches = []
    games = Game.query.all()
    for game in games:
        loweredTitle = game.title.lower()
        if loweredTitle.find(str.lower()) != -1:
            matches.append(game)
    return matches
    
@query.field('gameById')
def gameById(*_, id):
    game = Game.query.filter(Game.id == id).one_or_none()
    return game

@query.field('games')
def games(*_):
    return [game.format() for game in Game.query.limit(5).all()]

@query.field('user')
def user(*_, id=None):
    user = User.query.filter(User.id == id).one_or_none()
    print(user.games)
    return user

@query.field('userLogin')
def userLogin(*_, string, password):
    user = User.query.filter((User.email.ilike(string)) | (User.username.ilike(string))).first()
    if user.password == password:
        return user
    return 'Fail'
    
@query.field('users')
def users(*_):
    return [ user.format() for user in User.query.all()]

@query.field('reviews')
def reviews(*_):
    return [ review.format() for review in Review.query.all()]

#-------Mutations-----------
@mutation.field('addUser')
def add_user(_, info, email, password, username):
    exists = User.query.filter(User.email == email).one_or_none()
    if exists == None:
        newUser = User(email, password, username)
        newUser.insert()
        return newUser

@mutation.field('addGame')
def add_game(_, info, background_image, description, rawg_id, released, title):
    exists = Game.query.filter(Game.rawg_id == rawg_id).one_or_none()
    if exists == None:
        newGame = Game(background_image, description, rawg_id, released, title)
        newGame.insert()
        return newGame

@mutation.field('addReview')
def add_review(_, info, context, game_id, rating, user_id):
    exists = Review.query.filter(Review.game_id == game_id, Review.user_id == user_id).one_or_none()
    if exists == None:
        newReview = Review(context, game_id, rating, user_id)
        newReview.insert()
        return newReview