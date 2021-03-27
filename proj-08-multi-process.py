# import kivy module 
import kivy 
kivy.require("1.9.1") 

from kivy.app import App 
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout

import multiprocessing
from multiprocessing import Manager
from multiprocessing.managers import BaseManager
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color

from kivy.clock import Clock

class AppState:
  def __init__(self):
    self.xPos = 0
    self.yPos = 0
    self.xScale = 1
    self.yScale = 1

def runOptionsApp(appState):
  app = OptionsApp(appState)
  app.run()

def runRenderApp(appState):
  canvasApp = CanvasApp(appState)
  canvasApp.run()

class OptionsApp(App):
  def __init__(self, appState):
    super(OptionsApp, self).__init__()
    self.appState = appState
  def build(self):
    layout = BoxLayout(orientation='vertical')

    row1 = BoxLayout(orientation='horizontal')
    self.slider = Slider(min=0, max=500, step=1, size=(800, 50))
    self.slider.bind(value=self.OnSliderValueChange)
    self.label = Label(text=str(self.appState['xPos']))
    row1.add_widget(self.slider)
    row1.add_widget(self.label)
    row2 = BoxLayout(orientation='horizontal')
    self.slider2 = Slider(min=0, max=500, step=1, size=(800, 50))
    self.slider2.bind(value=self.OnSliderValueChange2)
    self.label2 = Label(text=str(self.appState['yPos']))
    row2.add_widget(self.slider2)
    row2.add_widget(self.label2)
    layout.add_widget(row1)
    layout.add_widget(row2)
    return layout
  def OnSliderValueChange(self, instance, value):
    self.appState['xPos'] = value
    self.label.text = str(value)
  def OnSliderValueChange2(self, instance, value):
    self.appState['yPos'] = value
    self.label2.text = str(value)
    
  
# From graphics module we are importing
# Rectangle and Color as they are
# basic building of canvas.
  
# class in which we are creating the canvas
class CanvasWidget(Widget):

    def on_request_close(self, *args):
        self.textpopup(title='Exit', text='Are you sure?')
        return True

    def __init__(self, appState):
      self.appState = appState

      super(CanvasWidget, self).__init__()

      # Arranging Canvas
      with self.canvas:

          Color(1, 1, 1, 1)  # set the colour 

          # Seting the size and position of image
          # image must be in same folder 
          self.rect = Rectangle(source ='assets\\testeye.png',
                                pos = (self.appState['xPos'], self.appState['yPos']), size = self.size)

      Clock.schedule_interval(self.update, 1 / 60.)
  
    # update function which makes the canvas adjustable.
    def update(self, *args):
      self.rect.pos = (self.appState['xPos'], self.appState['yPos'])
      self.canvas.ask_update()
  


# Create the App Class
class CanvasApp(App):
  def __init__(self, appState):
    super(CanvasApp, self).__init__()
    self.widget = CanvasWidget(appState)
  def build(self):
    return self.widget
  
if __name__ == '__main__':
  manager = multiprocessing.Manager()
  appState = multiprocessing.Manager().dict()
  appState["xPos"] = 0
  appState["yPos"] = 0
  p1 = multiprocessing.Process(target=runOptionsApp, args=(appState,))
  p2 = multiprocessing.Process(target=runRenderApp, args=(appState,))
  p1.start()
  p2.start()
  p1.join()
  p2.join()


