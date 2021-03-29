import numpy as np
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.image import Image
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stencilview import StencilView
from kivy.uix.splitter import Splitter
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, StringProperty
from kivy.graphics import Line, Color, Rectangle
from kivy.lang import Builder
from kivy.config import Config

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

# debug for seeing widget boundaries
# <BoxLayout>:
#     canvas.after:
#         Line:
#             rectangle: self.x+1,self.y+1,self.width-1,self.height-1
#             dash_offset: 5
#             dash_length: 3
    # 
    # GridEditorCanvas:
    #     id: editcanvas

ZOOMS = [0.5, 1.0, 2.0, 3.0, 4.0]

Builder.load_string(
'''
<Vertex>:
    canvas:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: (self.pos[0]-3, self.pos[1]-3)
            size: (6, 6)
        Color:
            rgba: 0, 0, 0, 1
        Line:
            width: 1
            cap: 'square'
            joint: 'miter'
            rectangle: (self.pos[0]-3, self.pos[1]-3, 6, 6)

<GridEditorWidget>:
    id: editorWidget
    Splitter:
        sizable_from: 'right'
        size_hint_max_x: 480
        min_size: 12
        GridEditorSidePanel:
            id: sidePanel
    GridEditorCanvas:
        id: editorCanvas


<GridEditorSidePanel>:
    orientation: 'vertical'
    BoxLayout:
        orientation: 'horizontal'
        Label:
            text: "Sync Left and Right"
        Switch:
            active: True
    BoxLayout:
        orientation: 'horizontal'
        Label:
            text: "Zoom"
        TextInput:
            text: root.zoomInput
    Label:
        text: "KeyFrames"

<GridEditorKeyframes>:

<GridEditorCanvas>:

    # use stencil to make canvas unable to draw outside the layout
    canvas.before:
        StencilPush
        Rectangle:
            pos: (0, 0)
            size: self.size
        StencilUse
        Color:
            rgba: .8, .8, .8, 1
        Rectangle:
            pos: (0,0)
            size: self.size
    canvas.after:
        StencilUnUse
        Rectangle:
            pos: (0, 0)
            size: self.size
        StencilPop

   
    
        
'''
)

class Vertex(Widget):
    # corresponds to the actual pixel offset relative to center.
    pixelX = 0
    pixelY = 0

    # corresponds to which vertex in the mesh grid this is, 
    coordinateX = 0
    coordinateY = 0

    def setCoordinate(self, x, y):
        self.coordinateX = x
        self.coordinateY = y

    def __init__(self, **kwargs):
        super(Vertex, self).__init__(**kwargs)
        self.pos = (0,0)
        # with self.canvas:
        #     Color(rgba=(1,1,1,1))
        #     self.shape = Rectangle(center= self.center, size=(8,8))

class GridEditorSidePanel(BoxLayout):
    zoomInput = StringProperty(str(1.0))
    def __init__(self, **kwargs):
        super(GridEditorSidePanel, self).__init__(**kwargs)
        # Window.bind(mouse_pos=self.mouse_pos)

    # def mouse_pos(self, window, pos):
    #     pass


class GridEditorCanvas(RelativeLayout):
    vertices = []
    
    def __init__(self, **kwargs):
        super(GridEditorCanvas, self).__init__(**kwargs)

    # def on_touch_down(self, touch):
    #     print(touch.pos)
    #     pass


class GridEditorWidget(BoxLayout):
    editorCanvas = ObjectProperty(None)
    sidePanel = ObjectProperty(None)
    vertices = None
    image = None
    countX = 3
    countY = 3
    zoom = 1.0
    zoomInput = StringProperty(str(zoom))
    viewX = 0
    viewY = 0

    def __init__(self, **kwargs):
        super(GridEditorWidget, self).__init__(**kwargs)
        Window.bind(on_minimize=self.on_minimize)
        Window.bind(on_maximize=self.on_maximize)
        Window.bind(on_restore=self.on_restore)
        Window.bind(on_resize=self.on_resize)

    def on_minimize(self, *largs):
        self.updateAllRenderPosition()

    def on_maximize(self, *largs):
        self.updateAllRenderPosition()

    def on_restore(self, *largs):
        self.updateAllRenderPosition()

    def on_resize(self, *largs):
        self.updateAllRenderPosition()


    def initialize(self):
        self.setGrid()
        pass

    def resetStartingView(self, sizeImage):
        zoomX = 1.0
        zoomY = 1.0
        maxLoop = 0
        print(sizeImage[0])
        print(Window.size[0])
        print(sizeImage[1])
        print(Window.size[1])
        while sizeImage[0] * zoomX > Window.size[0]:
            maxLoop = maxLoop + 1
            zoomX = zoomX * 0.8
            if maxLoop > 9:
                break
        maxLoop = 0
        while sizeImage[1] * zoomY > Window.size[1]:
            maxLoop = maxLoop + 1
            zoomY = zoomY * 0.8
            if maxLoop > 9:
                break
        zoom = min(zoomX, zoomY)
        self.zoom = zoom
        self.viewX = 0.0
        self.viewY = 0.0
        self.ids.sidePanel.zoomInput = str(zoom)


    # call set grid first i guess
    def setImage(self, image: Image):
        # calculate the default zoom here 
        self.resetStartingView(image.size)

        self.image = image 
        self.setInitialVertexPixel(image.size)
        self.updateAllRenderPosition()

    # after calling this the widets are nullified so you better not do anything until you call setGrid
    def removeAllWidgets(self):
        if self.vertices is None:
            return
        for i in range(self.countX):
            for j in range(self.countY):
                vertex = self.vertices[i][j]
                if vertex is not None:
                    continue
                vertex.parent.remove_widget(vertex)
                self.vertices[i][j] = None

    def setGrid(self, xVertexCount=3, yVertexCount=3):
        xVertexCount = max(xVertexCount, 2)
        yVertexCount = max(yVertexCount, 2)
        self.removeAllWidgets()
        self.vertices =  [[None for _ in range(xVertexCount)] for _ in range(yVertexCount)]
        self.countX = xVertexCount
        self.countY = yVertexCount
        for i in range(self.countX):
            for j in range(self.countY):
                vertex = Vertex()
                vertex.setCoordinate(i, j)
                self.vertices[i][j] = vertex
                self.ids.editorCanvas.add_widget(vertex)
        Clock.schedule_once(self.updateAllRenderPosition, 0.1)
        
    def setInitialVertexPixel(self, size=(100,100)):

        incX = float(size[0]) / float(self.countX - 1)
        incY = float(size[1]) / (self.countY - 1)
        startX = - size[0] / 2
        startY = - size[1] / 2
        for i in range(self.countX):
            for j in range(self.countY):
                vertex: Vertex = self.vertices[i][j] 
                vertex.pixelX = startX + (i*incX)
                vertex.pixelY = startY + (j*incY)


    def updateAllRenderPosition(self, *largs):
        offsetX = self.ids.editorCanvas.size[0] / 2
        offsetY = self.ids.editorCanvas.size[1] / 2
        for i in range(self.countX):
            for j in range(self.countY):
                vertex: Vertex = self.vertices[i][j] 
                x = (self.viewX + vertex.pixelX) * self.zoom + offsetX
                y = (self.viewY + vertex.pixelY) * self.zoom + offsetY 
                vertex.pos = (x,y)



    def on_touch_down(self, touch):
        super(GridEditorWidget, self).on_touch_down(touch)






# self.vertices[0][0].pos = touch.pos