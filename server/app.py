#!/usr/bin/env python3

from flask import request, session, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api, bcrypt
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
    def get(self):
        # Check if user_id is in session
        user_id = session.get('user_id')
        if not user_id:
            return {"error": "User not logged in"}, 401
        
         # Query user by ID
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return {"error": "User not found"}, 401

        # Return user data
        return {
            "id": user.id,
            "username": user.username,
            "image_url": user.image_url,
            "bio": user.bio
        }, 200

class Login(Resource):
    def post(self):
        # Handle login by implementing POST /login route
        try:
            data = request.get_json()
            if not data:
                return {"error": "No input data provided"}, 422

            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return {"error": "Username and password are required"}, 422

            user = User.query.filter_by(username=username).first()
            if user and user.authenticate(password):
                # If authenticated, save user ID in session and return user data
                session['user_id'] = user.id
                return {
                    "id": user.id,
                    "username": user.username,
                    "image_url": user.image_url,
                    "bio": user.bio
                }, 200
            else:
                # If not authenticated, return error with 401 status
                return {"error": "Invalid username or password"}, 401

        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}, 500

class Logout(Resource):
    def delete(self):
        # Handle logout by implementing DELETE /logout route
        user_id = session.get('user_id')
        if user_id is not None:  # Check for a valid user_id
            session.pop('user_id', None)
            return '', 204
        else:
            # If not logged in, return 401 with error
            return {"error": "User not logged in"}, 401


class RecipeIndex(Resource):
    def get(self):
        # Handle recipe viewing by implementing GET /recipes route
        user_id = session.get('user_id')
        if not user_id:
            return {"error": "User not logged in"}, 401

        recipes = Recipe.query.all()
        recipe_data = [
            {
                "id": recipe.id,
                "title": recipe.title,
                "instructions": recipe.instructions,
                "minutes_to_complete": recipe.minutes_to_complete,
                "user": {
                    "id": recipe.user.id,
                    "username": recipe.user.username,
                    "image_url": recipe.user.image_url,
                    "bio": recipe.user.bio
                }
            } for recipe in recipes
        ]
        return recipe_data, 200

    def post(self):
        # Handle recipe creation by implementing POST /recipes route
        user_id = session.get('user_id')
        if not user_id:
            return {"error": "User not logged in"}, 401

        data = request.get_json()
        if not data:
            return {"error": "No input data provided"}, 422

        title = data.get('title')
        instructions = data.get('instructions')
        minutes_to_complete = data.get('minutes_to_complete')

        errors = []
        if not title:
            errors.append("Title must be provided")
        if not instructions:
            errors.append("Instructions must be provided")
        elif len(instructions) < 50:
            errors.append("Instructions must be at least 50 characters long")
        if minutes_to_complete is not None and not isinstance(minutes_to_complete, int):
            errors.append("Minutes to complete must be an integer")

        if errors:
            return {"errors": errors}, 422

        user = db.session.get(User, user_id)
        if not user:
            return {"error": "User not found"}, 401

        recipe = Recipe(
            title=title,
            instructions=instructions,
            minutes_to_complete=minutes_to_complete,
            user_id=user_id
        )
        db.session.add(recipe)
        db.session.commit()

        return {
            "id": recipe.id,
            "title": recipe.title,
            "instructions": recipe.instructions,
            "minutes_to_complete": recipe.minutes_to_complete,
            "user": {
                "id": user.id,
                "username": user.username,
                "image_url": user.image_url,
                "bio": user.bio
            }
        }, 201

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)