from flask import Flask, render_template, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
import threading
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import func, create_engine
from datetime import datetime
from crontab import CronTab
from apscheduler.schedulers.background import BackgroundScheduler
from flask_apscheduler import APScheduler
import schedule
import time
import json


#from MisModels import db, control, Json

app = Flask(__name__)

#configurar la base de datos SQlite
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:1234@localhost/flask"
engine = create_engine("postgresql://postgres:1234@localhost/flask")
#inicializar la extension con la app
db = SQLAlchemy(app)

#!Modelos para las tablas
class Json(db.Model):
    __tablename__ = 'jsonFiles'
    id=db.Column(db.Integer,primary_key=True)
    data = db.Column(db.JSON)
    #autor = db.relationship('Autor', backref="json")

class Autor(db.Model):
    __tablename__ = 'control'
    id = db.Column(db.Integer, primary_key = True)
    creado_por = db.Column(db.String(64))
    fecha_creacion_ = db.Column(db.Date)
    modificado_por = db.Column(db.String(64))
    fecha_modificacion = db.Column(db.Date)
    vigente = db.Column(db.String(64))
    json = db.relationship('Json', backref="json")
    json_id = db.Column(db.Integer, db.ForeignKey("jsonFiles.id"), nullable=False )

class Backup(db.Model):
    __tablename__ = 'backup'
    id=db.Column(db.Integer,primary_key=True)
    data = db.Column(db.JSON)
    status = db.Column(db.String(64))
    Fecha_registro = db.Column(db.Date)
    
    #en el mismo form a;adir que se creo por usuario o agregar un nombre
    #en este caso guardar la fecha
    #mostrar un dato de vigente

with app.app_context():
    db.create_all()

def __init__(self,data):
    self.data=data
    

#se creo un objectos dentro de otros objectos que contienen peliculas    
cns_videos = [
    {
        "id": 1,
        "title": "1. pelis del monton"
    },
    {
        "id": 2,
        "title": "1. pelis del monton secuela 2"
    },
    {
        "id": 3,
        "title": "persona 3 rebirth"
    },   
]
lsc_videos = [
    {
        "id": 1,
        "title": "1. pelis no del monton"
    },
    {
        "id": 2,
        "title": "1. pelis mejor que el monton"
    },
    {
        "id": 3,
        "title": "persona 4 true game"
    },  
]


#se retorna los objectos creados en modo de json
@app.route("/api/v1/videos/")
def get_all_videos():
    return jsonify({"videos":{"cns": cns_videos,"lsc": lsc_videos}})

#!Muestra todos los datos de las tablas / JOIN
@app.route("/")
#@crontab.job(minute='*/1')
def index():

    #! threading mandar url
    url = "/"
    thread = threading.Thread(target=registrar_hora, args=(url,))
    thread.start()
    
    #! paginacion (muestra la cantidad de paginas que hay)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', default= 3, type=int) #se toma el valor del url

    data_con_registro = db.session.query(Json, Autor).join(Json, Autor.json_id == Json.id).paginate(page = page, per_page=per_page)
    return render_template('db.html', data_con_registro = data_con_registro, per_page = per_page)

#!funcion para crear json y almacenarlos en la base de datos
@app.route("/create_json",methods=['GET', 'POST'])
def create_json():
    
    #! threading para mandar la ruta del create json
    url = "create_json"
    thread = threading.Thread(target=registrar_hora, args=(url,))
    thread.start()

    if request.method == 'POST':
        idJson = request.form.get("id")
        nameJson = request.form.get("nombre_video")
        new_video = {
                "id": idJson,
                "title":nameJson
            }
        

        #--para almancenar en la segunda tabla-------------
        creador = request.form.get("creado_por")
        fecha_creacion = datetime.now()
        vigencia = request.form.get("vigenteInput")


        with app.app_context():
            datoAlmacenar = Json(data = new_video)
            db.session.add(datoAlmacenar)
            AutorAlmacenar = Autor(creado_por = creador, fecha_creacion_ = fecha_creacion , vigente = vigencia, json = datoAlmacenar)
            db.session.add(AutorAlmacenar)
            db.session.commit()
            return redirect('/')
    return render_template('add_json.html')

#!Editar un dato de la tabla
@app.route('/data/<int:id>', methods=['GET','POST'])
def update_json(id):

    #! threading mandar la ruta del editar_json
    url = "editar_json"
    thread = threading.Thread(target=registrar_hora, args=(url,))
    thread.start()

    #se consiguen los id de ambas tablas
    json = Json.query.filter(id == id).first()
    autor = Autor.query.filter(id == id).first()

    #autor = Json.query.get(id)
    #autor = Autor.query.get(id)
    if request.method == 'POST':
        if json:
            #--para almancenar en la primera tabla-------------
            idJson = request.form.get("id")
            nameJson = request.form.get("nombre_video")
            new_video = [
                {
                    "id":idJson,
                    "name":nameJson
                }
            ]

            #--para almancenar en la segunda tabla-------------
            Fecha_modificacion = datetime.now()
            vigencia = request.form.get("vigenteInput")
            Modificado_por = request.form.get("modificado_por")

            #se modifican los datos
            autor.modificado_por = Modificado_por
            autor.fecha_modificacion = Fecha_modificacion
            autor.vigente = vigencia
            json.data = new_video
            db.session.commit()
            return redirect(f'/data/{id}')
        return f"el titulo con el id = {id} no existe en la base de datos"
    return render_template('update_json.html' )

#!Borrar un dato de la tabla
@app.route('/data/<int:id>/delete', methods=['GET','POST'])
def delete_json(id):
        jsonId = Json.query.get(id)
        autorId = Autor.query.get(id)
        if request.method == 'POST':
            db.session.delete(jsonId)
            db.session.delete(autorId)
            db.session.commit()

            #! threading mandar url
            url = "se ha eliminado un dato"
            thread = threading.Thread(target=registrar_hora, args=(url,))
            thread.start()

            return redirect('/')
            return f"el titulo con el id = {id} no existe en la base de datos"
        return redirect('/')

#! thread
def registrar_hora(url):
    hora_actual = datetime.now()
    hora_cadena = hora_actual.strftime('%Y-%m-%d %H:%M:%S')
    if (url != "eliminar"):
        print('se accedio a la ruta' , url , ' a las: ', hora_cadena)
    else:
        print(url, ' a las ', hora_cadena)

#!Schedule------------------------------------------------------------



#def addBackup():
#        with app.app_context():
#            rows = db.session.query(Json).join(Autor).with_entities(Json.id).all()
#            for row in rows:
#                ids = int(row.id)
#                data = db.session.query(Json).join(Autor).filter(Json.id == ids).with_entities(Json.data).first() # el dato que nos devuelve es de tipo <class 'sqlalchemy.engine.row.Row'> hay que transformalo a json
                
#                data_list = list(data)
#                data_json = json.dumps(data_list)
#                data_json_fixed = json.loads(data_json)

#                backup_guardar = Backup(data = data_json_fixed, status = "se a creado la copia",Fecha_registro = datetime.now())
#                db.session.add(backup_guardar)
#                db.session.commit()
#            print("la copia a sido generada")

#def updateBackup():
#    with app.app_context():
#        rows = db.session.query(Backup).all()
#        for row in rows:
            
#            row.status = "Copia actualizada"
#            db.session.commit()
#        print("las copias fueron actualizados")

#def deleteBackup():
#    with app.app_context():
#        rows = db.session.query(Backup).all()
#        for row in rows:
#            if row.status == 'Copia actualizada':
#                db.session.delete(row)
#                db.session.commit()
#        print("las copias han sido borradas")


#schedule.every(5).seconds.do(addBackup)
#schedule.every(10).seconds.do(updateBackup)
#schedule.every(15).seconds.do(deleteBackup)   

#while True:
#    schedule.run_pending()
#    time.sleep(1)

#utilizar ASPscheduler ----------------------------------------------------
sched = BackgroundScheduler()
session_maker = sessionmaker(autocommit = False, autoflush=False, bind= engine)
Session = scoped_session(session_maker)

def mi_tarea():
    print("esta es una tarea" )

def addbackupASP():
    se = Session()
    rows = se.query(Json).all()
    for row in rows:
        ids = int(row.id)
        data = se.query(Json).join(Autor).filter(Json.id == ids).with_entities(Json.data).first()
        data_list = list(data)
        data_json = json.dumps(data_list)
        data_json_fixed = json.loads(data_json)

        backup_guardar = Backup(data = data_json_fixed, status = "se a creado la copia",Fecha_registro = datetime.now())
        Session.add(backup_guardar)
        Session.commit()
    print("la copia a sido generada")


def updateBackup():
    se = Session()
    rows = se.query(Backup).all()
    for row in rows:
        row.status = "Copia actualizada"
        Session.commit()
    print("las copias fueron actualizadas")

def deleteBackup():
    se = Session()
    rows = se.query(Backup).all()
    for row in rows:
        if row.status == "Copia actualizada":
            Session.delete(row)
            Session.commit()
    print("las copias han sido borradas")
    
sched.add_job(addbackupASP , 'interval', seconds = 2)
sched.add_job(updateBackup , 'interval', seconds = 2)
sched.add_job(deleteBackup , 'interval', seconds = 2)

sched.start()


if __name__ == "__main__":
    app.run()



