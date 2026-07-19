import sqlite3
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit, join_room
from geopy.distance import geodesic

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Diccionario para rastrear la ubicación y estado de los lavadores conectados
lavadores_conectados = {}

def inicializar_base_de_datos():
    conexion = sqlite3.connect('base de datos.db')
    cursor = conexion.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id TEXT NOT NULL,
            lavador_id TEXT,
            latitud REAL NOT NULL,
            longitud REAL NOT NULL,
            estado TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conexion.commit()
    conexion.close()

@socketio.on('connect')
def handle_connect():
    print("Un usuario o lavador se ha conectado en tiempo real.")

# Conectar al lavador a su sala privada usando su ID
@socketio.on('registrar_lavador')
def handle_registrar_lavador(data):
    lavador_id = data['lavador_id']
    join_room(lavador_id)
    print(f"Lavador {lavador_id} registrado en su sala privada.")

# Actualizar la ubicación en tiempo real enviada desde la app del lavador
@socketio.on('actualizar_ubicacion_lavador')
def handle_ubicacion(data):
    lavador_id = data['lavador_id']
    lavadores_conectados[lavador_id] = {
        "lat": data['latitud'],
        "lon": data['longitud'],
        "status": data.get('status', 'disponible')
    }

# El cliente solicita un lavado estilo Uber
@socketio.on('solicitar_lavado')
def handle_solicitud(data):
    cliente_lat = data['latitud']
    cliente_lon = data['longitud']
    cliente_id = data['cliente_id']
    
    conexion = sqlite3.connect('base de datos.db')
    cursor = conexion.cursor()
    cursor.execute('''
        INSERT INTO citas (cliente_id, latitud, longitud, estado) 
        VALUES (?, ?, ?, ?)
    ''', (cliente_id, cliente_lat, cliente_lon, 'pendiente'))
    cita_id = cursor.lastrowid
    conexion.commit()
    conexion.close()
    
    lavador_mas_cercano = None
    distancia_minima = 5.0 

    for id_lavador, info in lavadores_conectados.items():
        if info['status'] == 'disponible':
            distancia = geodesic((cliente_lat, cliente_lon), (info['lat'], info['lon'])).km
            if distancia < distancia_minima:
                distancia_minima = distancia
                lavador_mas_cercano = id_lavador

    if lavador_mas_cercano:
        emit('nueva_cita_disponible', {
            'cita_id': cita_id,
            'cliente_id': cliente_id,
            'latitud_cliente': cliente_lat,
            'longitud_cliente': cliente_lon
        }, room=lavador_mas_cercano)
        emit('respuesta_solicitud', {'status': f'Buscando... Lavador encontrado para la cita #{cita_id}.'})
    else:
        emit('respuesta_solicitud', {'status': 'No hay lavadores disponibles cerca.'})

# NUEVO: El lavador presiona "Aceptar" desde su app de Flutter
@socketio.on('aceptar_lavado')
def handle_aceptar_lavado(data):
    cita_id = data['cita_id']
    lavador_id = data['lavador_id']
    
    # 1. Actualizar el estado de la cita en SQLite
    conexion = sqlite3.connect('base de datos.db')
    cursor = conexion.cursor()
    cursor.execute('''
        UPDATE citas 
        SET lavador_id = ?, estado = 'aceptado' 
        WHERE id = ?
    ''', (lavador_id, cita_id))
    conexion.commit()
    
    # Obtener el cliente_id para notificarle
    cursor.execute('SELECT cliente_id FROM citas WHERE id = ?', (cita_id,))
    resultado = cursor.fetchone()
    conexion.close()
    
    # 2. Cambiar el estado del lavador a ocupado
    if lavador_id in lavadores_conectados:
        lavadores_conectados[lavador_id]['status'] = 'ocupado'
        
    if resultado:
        cliente_id = resultado[0]
        # Avisar globalmente o directamente al cliente que su lavador va en camino
        emit('cita_aceptada', {
            'cita_id': cita_id,
            'lavador_id': lavador_id,
            'status': 'Tu lavador está en camino'
        }, broadcast=True) 
        print(f"Cita #{cita_id} aceptada por el lavador {lavador_id}")

if __name__ == '__main__':
    inicializar_base_de_datos()
    socketio.run(app, debug=True)
