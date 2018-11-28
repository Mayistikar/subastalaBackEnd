from flask import Flask
from flask import request
from flask import Response
from flask import jsonify
from flask import json
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

#Import os to get pwd
import os

#Import aws s3 library
import boto3

# -------- SET VARIABLES -------- #
dbdir = "sqlite:///" + os.path.abspath(os.getcwd()) + "/db/database.db"

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config["SQLALCHEMY_DATABASE_URI"] = dbdir
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

s3 = boto3.resource('s3')

s3_client = boto3.client('s3')

BUCKET_NAME = "subastala"


# -------- SET MODELS -------- #
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(500))
    title = db.Column(db.String(500))
    description = db.Column(db.String(500))
    genre = db.Column(db.String(50))
    images = db.relationship('Image', backref='movie', lazy=True)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000), nullable=False)
    url = db.Column(db.String(1000))
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)


# -------- ROUTES -------- #
@app.route('/')
def index():
    return "Workink!"

@app.route('/create', methods=['POST'])
def create_movie():
    new_movie = Movie(
        code = request.json['code'],
        title = request.json['title'],
        description = request.json['description'],
        genre = request.json['genre']
    )
    db.session.add(new_movie)
    db.session.commit()

    return "Creating movie succeed!"
    

@app.route('/set_image', methods=['POST'])
def set_image():

    url_image = upload_file( request )    

    new_image = Image(
        name = request.headers['file_name'],
        url = url_image,
        movie_id = request.headers['movie_id']
    )
    db.session.add( new_image )
    db.session.commit() 
    return "Image added!"

@app.route('/get_movies')
def get_movies():
    list_movies = []
    list_images = []

    movies = Movie.query.order_by(Movie.id).all()
    for movie in movies:

        images = Image.query.filter_by(movie_id=movie.id).all()
        for image in images:
            img = {
                'id':image.id,
                'name':image.name,
                'url':image.url
            }            
            list_images.append(img)

        data = {
            'id' : movie.id,
            'code' : movie.code,
            'title' : movie.title,
            'description' : movie.description,
            'genre' : movie.genre,
            'images' : list_images
        }        
        list_movies.append(data)

    resp = jsonify(list_movies)
    resp.status_code = 200
    
    return resp

# -------- UTILS -------- #
def upload_file( request ):

    bucket = s3.Bucket('subastala')

    bucket.put_object(Key=request.headers['file_name'], Body=request.data)
    
    url = s3_client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': 'subastala',
            'Key': request.headers['file_name']
        },
        ExpiresIn=3600000
    )    

    return url





if __name__ == "__main__":
    db.create_all()
    #app.run(host="0.0.0.0", port=80)
    app.run()