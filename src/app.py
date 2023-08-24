"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Favorite, Character, Planet
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

#creating instance of data

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/people', methods=['GET'])
def get_characters():
    try:
        characters = Character.query.all()
        response_body = list(map(lambda x:x.serialize(),characters))
        return jsonify(response_body), 200
    except:
        return "Error trying to retrive people", 400

@app.route('/people/<int:char_id>', methods=['GET'])
def get_char(char_id):
    try:
        char = Character.query.filter_by(id = char_id).first()
        char = Character.serialize(char)
        return jsonify(char), 200
    except:
        return "Invalid id", 400

@app.route('/planets', methods=['GET'])
def get__all_planets():
    try:
        planets = Planet.query.all()
        print(planets)
        response_body = list(map(lambda x:x.serialize(),planets))
        return jsonify(response_body), 200
    except:
        return "Error trying to retrive planets", 400

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    try:
        planet = Planet.query.filter_by(id = planet_id).first()
        planet = Planet.serialize(planet)
        return jsonify(planet), 200
    except:
        return "Invalid id", 400

@app.route('/users', methods=['GET'])
def get_users():
   users = User.query.all()
   response_body = list(map(lambda x:x.serialize(),users))
   return jsonify(response_body), 200

@app.route('/<int:user_id>/favorites', methods=['GET'])
def get_favorites(user_id):
    favorites = Favorite.query.filter_by(user = user_id).first()
    if favorites == None:
        return "No favorites for user_id: "+str(user_id), 404
    favorites = Favorite.serialize(favorites)
    return jsonify(favorites), 200

@app.route('/<int:user_id>/favorites/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(user_id, planet_id):
    favorite = Favorite()
    favorite.name = request.json.get("name")
    favorite.type = 'planet'
    favorite.planet_id = planet_id
    favorite.user = user_id
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"msg":"Favorite planet added successfully!"})


@app.route('/<int:user_id>/favorites/people/<int:people_id>', methods=['POST'])
def add_favorite_people(user_id, character_id):
    favorite = Favorite()
    favorite.name = request.json.get("name")
    favorite.type = 'character'
    favorite.character_id = character_id
    favorite.user = user_id
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"msg":"Favorite character added successfully!"})

@app.route('/<int:user_id>/favorites/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(user_id, planet_id):
    favorites = Favorite.query.filter_by(user = user_id).first()
    if favorites == None:
        return "No favorites for user_id: "+str(user_id), 404
    response_body = list(map(lambda x:x.serialize(),favorites))
    for favorite in response_body:
        if "planet_id" in favorite:
            if favorite.planet_id == planet_id:
                db.session.delete(favorite)
                return "Deleted planet from favorites successfully", 200
        return "No planet in favorites", 404
    return "No favorites", 404

@app.route('/<int:user_id>/favorites/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_character(user_id, character_id):
    favorites = Favorite.query.filter_by(user = user_id).first()
    if favorites == None:
        return "No favorites for user_id: "+str(user_id), 404
    response_body = list(map(lambda x:x.serialize(),favorites))
    for favorite in response_body:
        if "character_id" in favorite:
            if favorite.character_id == character_id:
                db.session.delete(favorite)
                return "Deleted character from favorites successfully", 200
        return "No character in favorites", 404
    return "No favorites", 404

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
