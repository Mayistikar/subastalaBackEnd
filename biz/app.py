import boto3

from flask import Flask
from flask import request

from flask_sqlalchemy import SQLAlchemy
import os

dbdir = "sqlite:///" + os.path.abspath(os.getcwd()) + "/db/database.db"

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = dbdir
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(500))
    title = db.Column(db.String(500))
    description = db.Column(db.String(500))
    genre = db.Column(db.String(50))

s3 = boto3.resource('s3')
#data = open('test.jpg', 'rb')
#s3.Bucket('subastala').put_object(Key='test.jpg', Body=data)

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
    

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.headers['Content-Type'] == 'application/octet-stream':
        data = request.data
        s3.Bucket('subastala').put_object(Key=request.headers['file_name'], Body=data)
        return "Upload Succeed!"
    else:
        return "Upload not type"
    
    return "upload finished!"


if __name__ == "__main__":
    db.create_all()
    app.run()
