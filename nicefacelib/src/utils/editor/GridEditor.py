
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.splitter import Splitter
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

Builder.load_string(
'''
<GridEditorWidget>:
	Splitter:
		sizable_from: 'right'
		size_hint_max_x: 480
		GridEditorSidePanel:
	GridEditorCanvas:

<GridEditorSidePanel>:
	orientation: 'vertical'
	BoxLayout:
		orientation: 'horizontal'
		Label:
			text: "Sync Left and Right"
		Switch:
			active: True
	Label:
		text: "KeyFrames"

<GridEditorKeyframes>:

<GridEditorCanvas>:
    canvas:
        Color:
            rgba: 0, 0, 1, 1    # Blue
  
        # size and position of Canvas
        Rectangle:
            pos: self.pos
            size: self.size

		
'''
)

class GridEditorRoot(Widget):
	pass

class GridEditorSidePanel(BoxLayout):
	pass

class GridEditorCanvas(Widget):
	pass

class GridEditorWidget(BoxLayout):
	def __init__(self, **kwargs):
		super(GridEditorWidget, self).__init__(**kwargs)
	



  
