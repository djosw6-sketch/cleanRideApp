import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy_garden.mapview import MapView, MapMarker
from kivy.clock import Clock

class CleanRideApp(App):
    def build(self):
        # Contenedor principal vertical
        self.layout = BoxLayout(orientation='vertical')
        
        # 1. Creamos el mapa centrado en una coordenada inicial (ej. Ciudad de México)
        self.mapa = MapView(zoom=15, lat=19.4326, lon=-99.1332)
        
        # 2. Marcador para el carro del cliente
        self.marcador_cliente = MapMarker(lat=19.4326, lon=-99.1332)
        self.mapa.add_marker(self.marcador_cliente)
        
        # Marcador para el lavador (inicia en la misma posición)
        self.marcador_lavador = MapMarker(lat=19.4326, lon=-99.1332)
        
        # 3. Barra inferior de estado y botones
        self.barra_inferior = BoxLayout(orientation='horizontal', size_hint_y=0.2)
        self.lbl_estado = Label(text="Listo para solicitar", color=(1,1,1,1))
        
        boton_solicitar = Button(text='Solicitar Lavado', size_hint_x=0.4)
        boton_solicitar.bind(on_press=self.pedir_lavado)
        
        self.barra_inferior.add_widget(self.lbl_estado)
        self.barra_inferior.add_widget(boton_solicitar)
        
        # Unir todo al diseño principal
        self.layout.add_widget(self.mapa)
        self.layout.add_widget(self.barra_inferior)
        
        return self.layout

    def pedir_lavado(self, instance):
        self.lbl_estado.text = "Buscando lavador..."
        
        datos = {
            "cliente_id": "usuario_kivy_1",
            "latitud": self.mapa.lat,
            "longitud": self.mapa.lon
        }
        
        try:
            # Enviamos la solicitud al backend mediante HTTP POST
            response = requests.post("http://127.0.0.1:5000/registro", json=datos, timeout=5)
            self.lbl_estado.text = "Solicitud enviada al servidor."
            
            # Programar una función que simule la ruta del lavador cada 3 segundos
            Clock.schedule_interval(self.actualizar_ruta_lavador, 3.0)
        except Exception as e:
            self.lbl_estado.text = "Error de conexión"

    def actualizar_ruta_lavador(self, dt):
        self.mapa.remove_marker(self.marcador_lavador)
        
        # Movemos ligeramente la latitud del lavador simulando que se acerca
        nueva_lat = self.marcador_lavador.lat + 0.0002
        self.marcador_lavador.lat = nueva_lat
        
        self.mapa.add_marker(self.marcador_lavador)

if __name__ == '__main__':
    CleanRideApp().run()
