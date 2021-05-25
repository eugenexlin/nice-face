from kivy.app import App
from kivy.core.window import Window
from kivy.core.image import Image

from nicefacelib.src.utils.editor.GridEditor import GridEditorWidget



class MyApp(App):
    def build(self):
        Window.size = (1280, 720)
        gewidget = GridEditorWidget()
        gewidget.setGrid(3,3)
        img = Image("assets\\head01.png")
        gewidget.setImage(img)
        return gewidget


if __name__ == '__main__':
    MyApp().run() 