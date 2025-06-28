from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    _password_hash = db.Column(db.String(128), nullable=False)
    image_url = db.Column(db.String)
    bio = db.Column(db.String(255))

    #relationships
    recipes = db.relationship('Recipe', back_populates="user", cascade="all, delete-orphan")

    @property
    def password_hash(self):
        raise AttributeError('password_hash is not readable')

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise ValueError('Username must be provided')
        return username
    
    @validates('image_url')
    def validate_image_url(self, key, image_url):
        if image_url and not image_url.startswith(('http://', 'https://')):
            raise ValueError('Image URL must start with http:// or https://')
        return image_url
    
class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    minutes_to_complete = db.Column(db.Integer)

    # Foreign key to associate recipe with user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # relationships
    user = db.relationship('User', back_populates='recipes')

    @validates('title')
    def validate_title(self, key, title):
        if not title:
            raise ValueError('Title must be provided')
        return title

    @validates('instructions')
    def validate_instructions(self, key, instructions):
        if not instructions:
            raise ValueError('Instructions must be provided')
        if len(instructions) < 50:
            raise ValueError('Instructions must be at least 50 characters long')
        return instructions