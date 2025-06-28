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
    
    pass