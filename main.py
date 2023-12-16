from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
# from dotenv import load_dotenv
import os
# load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_KEY')
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQL_URI')
db = SQLAlchemy()
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


with app.app_context():
    db.create_all()
    # cafe = db.session.execute(db.select(Cafe).where(Cafe.location == 'Puducherry')).scalar()
    # db.session.delete(cafe)
    # db.session.commit()


@app.route("/")
def home():
    return render_template("index.html")

# HTTP GET - Read Record
@app.route('/random')
def random_cafe():
    cafes_list = db.session.execute(db.select(Cafe)).scalars().all()
    random_cafe = random.choice(cafes_list)
   
    return jsonify(cafe=random_cafe.to_dict()
        )
        
@app.route('/all')
def all_cafes():
    cafes_list = db.session.execute(db.select(Cafe)).scalars().all()
    cafe_dict=[cafe.to_dict() for cafe in cafes_list]
    return jsonify(cafes=cafe_dict)

@app.route('/search')
def search_cafe():
    loc = request.args.get('loc')
    cafes_list = db.session.execute(db.select(Cafe).where(Cafe.location == loc)).scalars().all()
    cafe_dict=[cafe.to_dict() for cafe in cafes_list]
    if cafe_dict == []:
        return jsonify(error={
            'not found': "Sorry, we don't have the cafe at this location"
        }), 404
    else:
        return jsonify(cafes=cafe_dict)

    
def to_bool(value):
    if value in ['True', 'true', 'T', 't', 'Yes', 'yes', 'y', '1']:
        return True
    else:
        return False
    

# HTTP POST - Create Record
@app.route('/add', methods=['POST'])
def add_cafe():
    # print(request.args.get('name'))
    new_cafe = Cafe(
        name= request.args.get('name'),
        map_url = request.args.get('map_url'),
        img_url = request.args.get('img_url'),
        location = request.args.get('loc'),
        seats = request.args.get('seats'),
        has_toilet = to_bool(request.args.get('toilet')),
        has_wifi = to_bool(request.args.get('wifi')),
        has_sockets = to_bool(request.args.get('sockets')),
        can_take_calls = to_bool(request.args.get('calls')),
        coffee_price = request.args.get('price')
    )
    db.session.add(new_cafe)
    db.session.commit()

    return jsonify(response={"success": "Successfully added the new cafe."})



# HTTP PUT/PATCH - Update Record
@app.route('/update-price/<int:id>', methods=['PATCH'])
def update_price(id):
    cafe_to_update = db.get_or_404(Cafe, id)
    if cafe_to_update:
        price = request.args.get('price')
        cafe_to_update.coffee_price = price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


# HTTP DELETE - Delete Record
@app.route('/report-closed/<int:id>', methods=['DELETE'])
def delete_cafe(id):
    if request.args.get('api-key') == os.environ.get('API_KEY'):
        cafe_to_delete = db.get_or_404(Cafe, id)
        if cafe_to_delete:
                db.session.delete(cafe_to_delete)
                db.session.commit()
                return jsonify(response={"success": "The cafe has been deleted"}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
            
    else:
        return jsonify(error={"Sorry": "That's not allowed. Make sure you have the correct api-key ."}), 403
    

if __name__ == '__main__':
    app.run(debug=False)
