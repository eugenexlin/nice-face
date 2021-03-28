from kivy.app import App
from kivy.core.window import Window

from nicefacelib.src.utils.editor.GridEditor import GridEditorWidget



class MyApp(App):
	def build(self):
		Window.size = (1280, 720)
		return GridEditorWidget()


if __name__ == '__main__':
    MyApp().run()