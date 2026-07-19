from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from geopy.distance import geodesic

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Base de datos simulada en memoria (puedes migrar esto a tu base de datos.db luego)
lavadores_conectados = {
    # "id_lavador": {"lat": 19.4326, "lon": -99.1332, "status": "disponible"}
}

@socketio.on('connect')
def handle_connect():
    print("Un usuario o lavador se ha conectado en tiempo real.")

# 1. El lavador actualiza su ubicación constantemente desde su app
@socketio.on('actualizar_ubicacion_lavador')
def handle_ubicacion(data):
    lavador_id = data['lavador_id']
    lavadores_conectados[lavador_id] = {
        "lat": data['latitud'],
        "lon": data['longitud'],
        "status": data.get('status', 'disponible')
    }

# 2. El cliente solicita un lavado "estilo Uber"
@socketio.on('solicitar_lavado')
def handle_solicitud(data):
    cliente_lat = data['latitud']
    cliente_lon = data['longitud']
    cliente_id = data['cliente_id']
    
    lavador_mas_cercano = None
    distancia_minima = 5.0 # Radio máximo de cobertura en kilómetros (ej. 5km)

    # Buscar al lavador disponible más cercano
    for id_lavador, info in lavadores_conectados.items():
        if info['status'] == 'disponible':
            distancia = geodesic((cliente_lat, cliente_lon), (info['lat'], info['lon'])).km
            if distancia < distancia_minima:
                distancia_minima = distancia
                lavador_mas_cercano = id_lavador

    if lavador_mas_cercano:
        # Enviar alerta en tiempo real ÚNICAMENTE al lavador más cercano
        emit('nueva_cita_disponible', {
            'cliente_id': cliente_id,
            'latitud_cliente': cliente_lat,
            'longitud_cliente': cliente_lon
        }, room=lavador_mas_cercano) # Necesitarás manejar 'rooms' para cada usuario en producción
        emit('respuesta_solicitud', {'status': 'Buscando... lavador encontrado, esperando aceptación.'})
    else:
        emit('respuesta_solicitud', {'status': 'No hay lavadores disponibles cerca en este momento.'})

if __name__ == '__main__':
    socketio.run(app, debug=True)
   import sqlite3

def inicializar_base_de_datos():
    conexion = sqlite3.connect('base de datos.db')
    cursor = conexion.cursor()
    
    # Crear la tabla de citas si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id TEXT NOT NULL,
            lavador_id TEXT,
            latitud REAL NOT NULL,
            longitud REAL NOT NULL,
            estado TEXT NOT NULL, -- 'pendiente', 'aceptado', 'en_camino', 'completado'
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conexion.commit()
    conexion.close()

# Ejecutar la creación al arrancar el servidor
inicializar_base_de_datos()
