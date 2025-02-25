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
from models import db, User, People, Planet

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

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

#[GET] /people Listar todos los registros de people en la base de datos.
@app.route('/people', methods=['GET'])
def people_get():
    response_body = {}
    character = db.session.execute(db.select(People)).scalars()
    response_body = {'characters': character.serialize()}
    return response_body, 200

#[GET] /people/<int:people_id> Muestra la información de un solo personaje según su id.
@app.route('/people/<int:character_id>', methods=['GET'])
def people_get_id(character_id):
    response_body = {}
    character = db.session.execute(db.select(People).filter(People.id == character_id)).scalar()
    response_body['character'] = character.serialize()
    return response_body, 201

#[GET] /planets Listar todos los registros de planets en la base de datos.
@app.route('/planets', methods=['GET'])
def planet_get():
    response_body = {}
    planet = db.session.execute(db.select(Planet)).scalars()
    response_body = {'planets': planet.serialize()}
    return response_body, 202

#[GET] /planets/<int:planet_id> Muestra la información de un solo planeta según su id.
@app.route('/planets/<int:planet_id>', methods=['GET'])
def planet_get_id(planet_id):
    response_body = {}
    planet = db.session.execute(db.select(Planet).filter(Planet.id == planet_id)).scalar()
    response_body['planet'] = planet.serialize()
    return response_body, 203

#[GET] /users Listar todos los usuarios del blog.
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200