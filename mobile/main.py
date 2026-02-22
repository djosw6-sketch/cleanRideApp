import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

class CleanRideApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')

        self.nombre = TextInput(hint_text='Nombre')
        self.vehiculo = TextInput(hint_text='Vehículo')

        boton = Button(text='Registrar')
        boton.bind(on_press=self.registrar)

        layout.add_widget(self.nombre)
        layout.add_widget(self.vehiculo)
        layout.add_widget(boton)

        return layout

    def registrar(self, instance):
        data = {
            "nombre": self.nombre.text,
            "vehiculo": self.vehiculo.text
        }

        response = requests.post("http://127.0.0.1:5000/registro", json=data)
        print(response.json())

if __name__ == '__main__':
    CleanRideApp().run()