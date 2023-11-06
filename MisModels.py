from flask_sqlalchemy import SQLAlchemy
import psycopg2
from sqlalchemy.orm import DeclarativeBase

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Json(db.Model):
    __tablename__ = 'jsonFiles'
    id=db.Column(db.Integer,primary_key=True)
    data = db.Column(db.JSON)

class control(db.Model):
    __tablename__ = 'control'
    id = db.Column(db.Integer, primary_key = True)
    creado_por = db.Column(db.String(64))
    fecha_creacion_ = db.Column(db.Date)
    modificado_por = db.Column(db.String(64))
    fecha_modificacion = db.Column(db.Date)
    vigente = db.Column(db.String(64))
