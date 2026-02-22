from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conductores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            vehiculo TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/registro', methods=['POST'])
def registro():
    data = request.json
    nombre = data['nombre']
    vehiculo = data['vehiculo']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conductores (nombre, vehiculo) VALUES (?, ?)",
        (nombre, vehiculo)
    )
    conn.commit()
    conn.close()

    return jsonify({"mensaje": "Registro exitoso"})

if __name__ == '__main__':
    app.run(debug=True)