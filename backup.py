from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
#configurar la base de datos SQlite
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:1234@localhost/flask"
#inicializar la extension con la app
db = SQLAlchemy(app)

class Backup(db.Model):
    __tablename__ = 'backup'
    id=db.Column(db.Integer,primary_key=True)
    data = db.Column(db.JSON)
    status = db.Column(db.String(64))
    Fecha_registro = db.Column(db.Date)

with app.app_context():
    db.create_all()