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
    
    # --- GUARDAR EN LA BASE DE DATOS REAL ---
    conexion = sqlite3.connect('base de datos.db')
    cursor = conexion.cursor()
    cursor.execute('''
        INSERT INTO citas (cliente_id, latitud, longitud, estado) 
        VALUES (?, ?, ?, ?)
    ''', (cliente_id, cliente_lat, cliente_lon, 'pendiente'))
    
    cita_id = cursor.lastrowid # Este es el número de cita único creado
    conexion.commit()
    conexion.close()
    print(f"Cita #{cita_id} guardada con éxito en la base de datos.")
    # ----------------------------------------

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
        # Enviar alerta al lavador incluyendo el número de cita (cita_id)
        emit('nueva_cita_disponible', {
            'cita_id': cita_id,
            'cliente_id': cliente_id,
            'latitud_cliente': cliente_lat,
            'longitud_cliente': cliente_lon
        }, room=lavador_mas_cercano)
        emit('respuesta_solicitud', {'status': f'Buscando... Lavador encontrado para la cita #{cita_id}. Esperando aceptación.'})
    else:
        emit('respuesta_solicitud', {'status': 'No hay lavadores disponibles cerca en este momento.'})

    ''')
    conexion.commit()
    conexion.close()

# Ejecutar la creación al arrancar el servidor
inicializar_base_de_datos()
