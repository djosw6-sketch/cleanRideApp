import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label

class CleanRideApp(App):
    def build(self):
        # Contenedor principal con margen (padding) y espacio entre elementos (spacing)
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        # Campos de entrada de texto
        self.nombre = TextInput(hint_text='Nombre', multiline=False)
        self.vehiculo = TextInput(hint_text='Vehículo', multiline=False)

        # Botón para registrar los datos
        boton = Button(
            text='Registrar', 
            background_color=(0, 0.6, 0.8, 1), # Color azul/celeste
            font_size='18sp'
        )
        boton.bind(on_press=self.registrar)

        # Etiqueta de texto para mostrar mensajes de estado al usuario
        self.resultado = Label(
            text='Introduce los datos y presiona Registrar', 
            color=(0.7, 0.7, 0.7, 1)
        )

        # Añadimos los elementos (widgets) al contenedor visual
        layout.add_widget(self.nombre)
        layout.add_widget(self.vehiculo)
        layout.add_widget(boton)
        layout.add_widget(self.resultado)

        return layout

    def registrar(self, instance):
        # Capturamos la información escrita por el usuario
        nombre_usuario = self.nombre.text.strip()
        vehiculo_usuario = self.vehiculo.text.strip()

        # Validación: Evitar campos vacíos
        if not nombre_usuario or not vehiculo_usuario:
            self.resultado.text = "Error: Por favor, llena todos los campos."
            self.resultado.color = (1, 0, 0, 1) # Texto en rojo
            return

        # Estructura de datos que se enviará en la petición HTTP
        datos = {
            "nombre": nombre_usuario,
            "vehiculo": vehiculo_usuario
        }

        # Actualizamos la etiqueta para avisar que se está procesando
        self.resultado.text = "Enviando datos..."
        self.resultado.color = (1, 1, 1, 1)

        try:
            # URL de prueba (Reemplázala por la URL real de tu backend o API)
            url_api = "https://httpbin.org/post"
            
            # Realizamos la petición POST de forma síncrona
            response = requests.post(url_api, json=datos, timeout=5)

            # Si el servidor responde correctamente (Código 200 o 201)
            if response.status_code in [200, 201]:
                self.resultado.text = f"¡Registro exitoso para {nombre_usuario}!"
                self.resultado.color = (0, 1, 0, 1) # Texto en verde
                
                # Limpiamos los campos de texto para un nuevo registro
                self.nombre.text = ""
                self.vehiculo.text = ""
            else:
                self.resultado.text = f"Error en el servidor: Código {response.status_code}"
                self.resultado.color = (1, 0, 0, 1)
                
        except requests.exceptions.Timeout:
            self.resultado.text = "Error: Tiempo de espera agotado (Timeout)."
            self.resultado.color = (1, 0, 0, 1)
        except requests.exceptions.RequestException:
            self.resultado.text = "Error: No se pudo conectar con el servidor."
            self.resultado.color = (1, 0, 0, 1)

# Punto de entrada para ejecutar la aplicación
if __name__ == '__main__':
    CleanRideApp().run()