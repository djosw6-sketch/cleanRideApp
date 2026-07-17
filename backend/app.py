from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configuración de la base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base_de_datos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializamos SQLAlchemy
db = SQLAlchemy(app)

# --- MODELOS DE LA BASE DE DATOS ---

# Tabla de Clientes y sus Vehículos
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False, unique=True)
    correo = db.Column(db.String(120), unique=True, nullable=True)
    
    marca_carro = db.Column(db.String(50), nullable=False)   
    modelo_carro = db.Column(db.String(50), nullable=False)  
    placa_carro = db.Column(db.String(20), nullable=False)   
    tipo_carro = db.Column(db.String(30), nullable=False)    

    # Esto conecta al usuario con sus citas agendadas
    citas = db.relationship('Cita', backref='cliente', lazy=True)

# Tabla para las Reservas de Citas
class Cita(db.Model):
    __tablename__ = 'citas'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha_hora = db.Column(db.DateTime, nullable=False)  
    tipo_servicio = db.Column(db.String(50), nullable=False)  
    estado = db.Column(db.String(30), default='Pendiente', nullable=False)
    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)


# --- RUTAS DE LA APP ---

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/agendar', methods=['POST'])
def agendar_cita():
    datos = request.get_json()
    
    # 1. Verificar si el usuario ya está registrado usando su teléfono
    usuario = Usuario.query.filter_by(telefono=datos['telefono']).first()
    
    if not usuario:
        # Si es cliente nuevo, lo registramos con su carro
        usuario = Usuario(
            nombre=datos['nombre'],
            telefono=datos['telefono'],
            marca_carro=datos['marca_carro'],
            modelo_carro=datos['modelo_carro'],
            placa_carro=datos['placa_carro'],
            tipo_carro=datos['tipo_carro']
        )
        db.session.add(usuario)
        db.session.commit() # Guardamos para obtener su ID único
    
    # 2. Convertir la fecha recibida de texto a formato fecha de Python
    # El formato esperado es: "Año-Mes-Día Hora:Minuto" (Ejemplo: "2026-07-20 15:30")
    try:
        fecha_cita = datetime.strptime(datos['fecha_hora'], '%Y-%m-%d %H:%M')
    except ValueError:
        return jsonify({"status": "error", "mensaje": "Formato de fecha inválido. Usa 'AAAA-MM-DD HH:MM'"}), 400
    
    # 3. Crear la cita para este usuario
    nueva_cita = Cita(
        fecha_hora=fecha_cita,
        tipo_servicio=datos['tipo_servicio'],
        usuario_id=usuario.id
    )
    
    db.session.add(nueva_cita)
    db.session.commit()
    
    return jsonify({
        "status": "success",
        "mensaje": "¡Cita agendada con éxito!",
        "cliente": usuario.nombre,
        "vehiculo": f"{usuario.marca_carro} {usuario.modelo_carro}",
        "fecha_hora": nueva_cita.fecha_hora.strftime('%Y-%m-%d %H:%M')
    }), 201

if __name__ == '__main__':
    # Creamos las tablas en la base de datos si no existen al iniciar
    with app.app_context():
        db.create_all()
    app.run(debug=True)
