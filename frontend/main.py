from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
import requests
import base64

class FridgeApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        
        self.file_chooser = FileChooserIconView(filters=['*.jpg', '*.png'])
        self.layout.add_widget(self.file_chooser)
        
        self.upload_button = Button(text='Upload and Analyze')
        self.upload_button.bind(on_press=self.upload_image)
        self.layout.add_widget(self.upload_button)
        
        self.result_label = Label(text='Results will appear here')
        self.layout.add_widget(self.result_label)
        
        return self.layout
    
    def upload_image(self, instance):
        if self.file_chooser.selection:
            file_path = self.file_chooser.selection[0]
            with open(file_path, 'rb') as f:
                image_data = f.read()
            encoded = base64.b64encode(image_data).decode('utf-8')
            
            # Send to backend (placeholder URL)
            response = requests.post('http://localhost:5000/analyze', json={'image': encoded})
            if response.status_code == 200:
                result = response.json()['result']
                self.result_label.text = result
            else:
                self.result_label.text = 'Error processing image'

if __name__ == '__main__':
    FridgeApp().run()