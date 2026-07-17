from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS # Importamos CORS

app = Flask(__name__)
CORS(app) # Esto permite que tu página web se conecte al backend sin bloqueos

app.config['SQLALCHEMY_DATABASE_DATABASE_URI'] = 'sqlite:///base_de_datos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Cita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    marca_carro = db.Column(db.String(50), nullable=False)
    modelo_carro = db.Column(db.String(50), nullable=False)
    placa_carro = db.Column(db.String(20), nullable=False)
    tipo_carro = db.Column(db.String(50), nullable=False)
    fecha_hora = db.Column(db.String(50), nullable=False)
    tipo_servicio = db.Column(db.String(50), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/agendar', methods=['POST'])
def agendar_cita():
    data = request.get_json()
    try:
        nueva_cita = Cita(
            nombre=data['nombre'],
            telefono=data['telefono'],
            marca_carro=data['marca_carro'],
            modelo_carro=data['modelo_carro'],
            placa_carro=data['placa_carro'],
            tipo_carro=data['tipo_carro'],
            fecha_hora=data['fecha_hora'],
            tipo_servicio=data['tipo_servicio']
        )
        db.session.add(nueva_cita)
        db.session.commit()
        return jsonify({"status": "success", "mensaje": "¡Cita agendada con éxito!"}), 201
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) # El host '0.0.0.0' permite conexiones externas
   
