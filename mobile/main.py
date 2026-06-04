import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label

class CleanRideApp(App):
    def build(self):
        # Contenedor principal con márgenes limpios
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Campos de entrada de texto
        self.nombre = TextInput(hint_text='Nombre del usuario', multiline=False)
        self.vehiculo = TextInput(hint_text='Modelo o Placa del Vehículo', multiline=False)

        # Botón para registrar los datos
        boton = Button(
            text='Registrar Vehículo', 
            background_color=(0, 0.5, 0.8, 1), # Color Azul
            font_size='18sp'
        )
        boton.bind(on_press=self.registrar)

        # Etiqueta de estado para el usuario
        self.resultado = Label(
            text='CleanRide - Ingrese datos para comenzar', 
            color=(0.8, 0.8, 0.8, 1)
        )

        # Añadimos los elementos al diseño
        layout.add_widget(self.nombre)
        layout.add_widget(self.vehiculo)
        layout.add_widget(boton)
        layout.add_widget(self.resultado)

        return layout

    def registrar(self, instance):
        nombre_usuario = self.nombre.text.strip()
        vehiculo_usuario = self.vehiculo.text.strip()

        # Validación básica de campos vacíos
        if not nombre_usuario or not vehiculo_usuario:
            self.resultado.text = "Error: Ambos campos son obligatorios."
            self.resultado.color = (1, 0, 0, 1)
            return

        datos = {
            "nombre": nombre_usuario,
            "vehiculo": vehiculo_usuario
        }

        self.resultado.text = "Guardando en la nube..."
        self.resultado.color = (1, 1, 1, 1)

        try:
            # Tu URL real de Firebase con '/usuarios.json' al final
            url_api = "https://cleanrideapp-37a57-default-rtdb.firebaseio.com/usuarios.json"
            
            # Enviamos los datos reales a la base de datos con un método POST
            response = requests.post(url_api, json=datos, timeout=6)

            if response.status_code == 200:
                self.resultado.text = f"¡{nombre_usuario} registrado con éxito!"
                self.resultado.color = (0, 1, 0, 1) # Verde éxito
                
                # Limpiamos las cajas de texto
                self.nombre.text = ""
                self.vehiculo.text = ""
            else:
                self.resultado.text = f"Error del servidor: {response.status_code}"
                self.resultado.color = (1, 0, 0, 1)
                
        except requests.exceptions.RequestException:
            self.resultado.text = "Error: Sin conexión o URL inválida."
            self.resultado.color = (1, 0, 0, 1)

if __name__ == '__main__':
    CleanRideApp().run()