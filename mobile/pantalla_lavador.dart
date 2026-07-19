import 'package:flutter/material.dart';
import 'package:socket_io_client/socket_io_client.dart' as IO;

class PantallaLavador extends StatefulWidget {
  @override
  _PantallaLavadorState createState() => _PantallaLavadorState();
}

class _PantallaLavadorState extends State<PantallaLavador> {
  late IO.Socket socket;
  Map<String, dynamic>? citaDisponible; // Guarda la cita si hay una cerca
  String miIdLavador = "lavador_juan";  // Tu ID de lavador ficticio

  @override
  void initState() {
    super.initState();
    conectarAlServidor();
  }

  void conectarAlServidor() {
    // Configura la IP de tu servidor Flask (10.0.2.2 se usa para el emulador de Android)
    socket = IO.io('http://10.0.2.2:5000', IO.OptionBuilder()
      .setTransports(['websocket'])
      .disableAutoConnect()
      .build());

    socket.connect();

    socket.onConnect((_) {
      print("Lavador conectado al servidor");
      // Al conectarse, se registra en su sala privada para recibir alertas directas
      socket.emit('registrar_lavador', {'lavador_id': miIdLavador});
      
      // Simular que el lavador manda su ubicación actual al conectarse
      socket.emit('actualizar_ubicacion_lavador', {
        'lavador_id': miIdLavador,
        'latitud': 19.4350,
        'longitud': -99.1350,
        'status': 'disponible'
      });
    });

    // Escuchar si el servidor backend te manda una nueva cita cercana
    socket.on('nueva_cita_disponible', (data) {
      setState(() {
        citaDisponible = data; // Guarda los datos para mostrarlos en pantalla
      });
    });
  }

  void aceptarServicio() {
    if (citaDisponible != null) {
      // Enviar la señal de aceptación al evento 'aceptar_lavado' de Flask
      socket.emit('aceptar_lavado', {
        'cita_id': citaDisponible!['cita_id'],
        'lavador_id': miIdLavador
      });

      setState(() {
        citaDisponible = null; // Limpiar la alerta tras aceptar
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("¡Cita aceptada! Dirígete a la ubicación.")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("CleanRide - Panel Lavador")),
      body: Center(
        child: citaDisponible == null
            ? Text("Esperando solicitudes de lavado...", style: TextStyle(fontSize: 16, color: Colors.grey))
            : Container(
                margin: EdgeInsets.all(20),
                padding: EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.blue[50],
                  borderRadius: BorderRadius.circular(15),
                  border: Border.all(color: Colors.blue, width: 2),
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text("¡TRABAJO DISPONIBLE!", style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.blue[900])),
                    SizedBox(height: 10),
                    Text("Cita #: ${citaDisponible!['cita_id']}"),
                    Text("Cliente ID: ${citaDisponible!['cliente_id']}"),
                    Text("Lat: ${citaDisponible!['latitud_cliente']} | Lon: ${citaDisponible!['longitud_cliente']}"),
                    SizedBox(height: 20),
                    ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green,
                        padding: EdgeInsets.symmetric(horizontal: 40, vertical: 15),
                      ),
                      onPressed: aceptarServicio,
                      child: Text("ACEPTAR LAVADO", style: TextStyle(color: Colors.white, fontSize: 16)),
                    )
                  ],
                ),
              ),
      ),
    );
  }
}
