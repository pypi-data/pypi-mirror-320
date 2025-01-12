from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout


class Scanner(GridLayout):    
    def test(self,instance,text):
        print(text)
        
    def submit(self,instance,text):
        print(text)

class ScannerApp(App):
    def build(self):
        return Scanner(cols=3)


if __name__ == '__main__':
    ScannerApp().run()