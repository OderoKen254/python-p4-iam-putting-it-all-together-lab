#!/usr/bin/env python3

from flask import request, session, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api, bcrypt
from flask_cors import CORS
from models import User, Recipe

class Signup(Resource):
    def post(self):
        try:
            # Get JSON data from request
            data = request.get_json()
            if not data:
                return {"errors": ["No input data provided"]}, 422
            
            # Extracting fields
            username = data.get('username')
            password = data.get('password')
            image_url = data.get('image_url')
            bio = data.get('bio')

            # Validating required fields
            errors = []
            if not username:
                errors.append("Username must be provided")
            if not password:
                errors.append("Password must be provided")

            if errors:
                return {"errors": errors}, 422
            
            # Creating new user
            user = User(
                username=username,
                image_url=image_url,
                bio=bio
            )
            user.password_hash = password  # Encrypt password using setter

            # Saving to database
            db.session.add(user)
            db.session.commit()

            # Store user_id in session
            session['user_id'] = user.id

            # Returning user data
            return {
                "id": user.id,
                "username": user.username,
                "image_url": user.image_url,
                "bio": user.bio
            }, 201

        except ValueError as ve:
            # Handle validation errors from model (e.g., invalid image_url)
            db.session.rollback()
            return {"errors": [str(ve)]}, 422
        except IntegrityError:
            # Handle duplicate username
            db.session.rollback()
            return {"errors": ["Username already exists"]}, 422
        except Exception as e:
            # Handle unexpected errors
            db.session.rollback()
            return {"errors": [f"An error occurred: {str(e)}"]}, 422

class CheckSession(Resource):
    pass

class Login(Resource):
    pass

class Logout(Resource):
    pass

class RecipeIndex(Resource):
    pass

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)