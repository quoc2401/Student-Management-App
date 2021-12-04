from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'osdoskdskods!@#dokko2o1ko1k2- 1-_!_!$(@$_!$!$)$!s'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:quoc2401@localhost/mystumana?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['MIN_AGE'] = 15
app.config['MAX_AGE'] = 20
app.config['MAX_SIZE'] = 4


db = SQLAlchemy(app=app)
