import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite

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

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    if not data or not all(key in data for key in ['email', 'password']):
        return jsonify({"error": "Email y contraseña son obligatorios"}), 400
    
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"error": "El usuario ya existe"}), 400
    
    new_user = User(email=data['email'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify(new_user.serialize()), 201

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = request.args.get('user_id')
    user = User.query.get_or_404(user_id)
    favorites = Favorite.query.filter_by(user_id=user.id).all()
    return jsonify({
        "planets": [fav.planet.serialize() for fav in favorites if fav.planet_id],
        "people": [fav.people.serialize() for fav in favorites if fav.people_id]
    }), 200

@app.route('/people', methods=['GET'])
def people_get():
    people = People.query.all()
    return jsonify([person.serialize() for person in people]), 200

@app.route('/people/<int:character_id>', methods=['GET'])
def people_get_id(character_id):
    person = People.query.get_or_404(character_id)
    return jsonify(person.serialize()), 200

@app.route('/people', methods=['POST'])
def create_people():
    data = request.get_json()
    
    if not data or 'planet_id' not in data:
        return jsonify({"error": "planet_id es obligatorio"}), 400
    
    planet = Planet.query.get(data['planet_id'])
    if not planet:
        return jsonify({"error": "El planet_id proporcionado no existe"}), 404

    new_person = People(
        name=data.get("name"),
        species=data.get("species"),
        birth_year=data.get("birth_year"),
        gender=data.get("gender"),
        planet_id=data["planet_id"]
    )
    db.session.add(new_person)
    db.session.commit()

    return jsonify(new_person.serialize()), 201

@app.route('/planets', methods=['GET'])
def planet_get():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def planet_get_id(planet_id):
    planet = Planet.query.get_or_404(planet_id)
    return jsonify(planet.serialize()), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"error": "user_id es obligatorio"}), 400
    
    user = User.query.get_or_404(user_id)
    planet = Planet.query.get_or_404(planet_id)
    
    if Favorite.query.filter_by(user_id=user.id, planet_id=planet.id).first():
        return jsonify({"error": "Este planeta ya está en favoritos"}), 400
    
    new_favorite = Favorite(user_id=user.id, planet_id=planet.id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({"message": "Planeta añadido a favoritos"}), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"error": "user_id es obligatorio"}), 400
    
    user = User.query.get_or_404(user_id)
    person = People.query.get_or_404(people_id)
    
    if Favorite.query.filter_by(user_id=user.id, people_id=person.id).first():
        return jsonify({"error": "Este personaje ya está en favoritos"}), 400
    
    new_favorite = Favorite(user_id=user.id, people_id=person.id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({"message": "Personaje añadido a favoritos"}), 201

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
