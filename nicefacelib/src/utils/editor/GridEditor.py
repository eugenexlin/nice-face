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
from kivy.graphics import Line, Color, Rectangle, Mesh
from kivy.lang import Builder
from kivy.config import Config
import time
import math
import nicefacelib.src.utils.GLUtils as GLUtils

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
        # Color:
        #     rgba: 1, 1, 1, 1
        # Rectangle:
        #     pos: (self.pos[0]-3, self.pos[1]-3)
        #     size: (6, 6)
        # Color:
        #     rgba: 0, 0, 0, 1
        # Line:
        #     width: 1
        #     cap: 'square'
        #     joint: 'miter'
        #     rectangle: (self.pos[0]-3, self.pos[1]-3, 6, 6)

<ImagePlaceholderFrame>:
    size_hint: None, None
    canvas:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: (self.width, self.height)

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
            multiline: False
            on_text: root.onZoomChange(self.text)
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

class ImagePlaceholderFrame(Widget):
    pass

class Vertex(Widget):
    # corresponds to the actual pixel offset relative to center.
    pixelPos = (0,0)

    isHighlighted = False

    # corresponds to which vertex in the mesh grid this is, 
    # this should not change after init.
    coordinate = ()

    def setCoordinate(self, x, y):
        self.coordinate = (x, y)

    def __init__(self, **kwargs):
        super(Vertex, self).__init__(**kwargs)
        self.pos = (0,0)
        with self.canvas:
            self.rectC = Color(rgba=(1,1,1,1))
            self.rect = Rectangle(pos=(0,0), size=(6,6))
            self.rectLineC = Color(rgba=(0,0,0,1))
            self.rectLine = Line(rectangle=(0,0, 6, 6))

    def movePixelPos(self, dX, dY):
        self.pixelPos = (self.pixelPos[0] - dX, self.pixelPos[1] - dY)
    def setPixelPos(self, pixelPos):
        self.pixelPos = pixelPos
        
    def updatePos(self, pos):
        self.pos = pos
        self.rect.pos = (pos[0]-3, pos[1]-3)
        self.rectLine.rectangle = (pos[0]-3, pos[1]-3, 6, 6)

    def updateHighlight(self, isHighlighted):
        if (self.isHighlighted != isHighlighted):
            self.isHighlighted = isHighlighted
            self.rectLine.width = 1.4 if isHighlighted else 1
            self.rectC = Color(rgba=(.9,.9,1,1)) if isHighlighted else Color(rgba=(1,1,1,0.5))

    def getDistanceFrom(self, pos, maxDist):
        dist = math.dist((self.pixelPos[0], self.pixelPos[1]), pos)
        if dist < maxDist:
            return dist
        return -1



class GridEditorSidePanel(BoxLayout):
    zoomInput = StringProperty(str(1.0))
    def __init__(self, **kwargs):
        super(GridEditorSidePanel, self).__init__(**kwargs)
        # Window.bind(mouse_pos=self.mouse_pos)

    def onZoomChange(self, text):
        try:
            val = float(text)
            if val > 0:
                self.parent.parent.zoom = val
                self.parent.parent.updateAllRenderPosition()
        except ValueError:
            pass

class GridEditorCanvas(RelativeLayout):
    imagePlaceholderFrame = ObjectProperty(None)
    countX = 0
    countY = 0
    
    def __init__(self, **kwargs):
        super(GridEditorCanvas, self).__init__(**kwargs)
        self.imagePlaceholderFrame = ImagePlaceholderFrame()
        self.add_widget(self.imagePlaceholderFrame)
        with self.canvas:
            self.imageMesh = Mesh(vertices=[], indices=[], mode='triangle_strip')

    def updateMeshImage(self, image):
        self.imageMesh.texture = image.texture
    def updateMeshVertices(self, vertices):
        self.imageMesh.vertices = vertices
    def updateSingleVertex(self, vertex: Vertex):
        #remember we need to map vertex from inverted coordinate to the mesh's coordinates
        index = (vertex.coordinate[1] + (vertex.coordinate[0]*self.countX))*4 
        vertices = self.imageMesh.vertices.copy()
        vertices[index] = vertex.pos[0]
        vertices[index+1] = vertex.pos[1]
        self.imageMesh.vertices = vertices
    def updateIndices(self, countX, countY):
        if (self.countX != countX or self.countY != countY):
            self.imageMesh.indices = GLUtils.getIndicesForSquareMeshDegenerateTriangles(countX, countY)
            self.countX = countX
            self.countY = countY

    def setIndices():
        pass

class GridEditorWidget(BoxLayout): 
    HOVER_DISTANCE = 20 #PX

    editorCanvas = ObjectProperty(None)
    sidePanel = ObjectProperty(None)
    vertices = None
    image = None
    countX = 3
    countY = 3
    zoom = 1.0

    #keyboard hotkeys
    previousTouchPos = (0,0)
    previousDragPos = (0,0)
    isSpaceHeld = False
    isDraggingView = False
    isDraggingVertex = False
    dragVertex = None

    # we are calculating view as the offset from default center.
    # this should be pixel value before zoom.
    viewX = 0.0
    viewY = 0.0

    # these width and height refer to the default image dimensions untransformed and at 100%
    imageWidth = 100
    imageHeight = 100

    def __init__(self, **kwargs):
        super(GridEditorWidget, self).__init__(**kwargs)
        Window.bind(on_minimize=self.on_minimize)
        Window.bind(on_maximize=self.on_maximize)
        Window.bind(on_restore=self.on_restore)
        Window.bind(on_resize=self.on_resize)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self.handleKeyDown, on_key_up=self.handleKeyUp)

        Window.bind(mouse_pos=self.on_mouse_pos)
        Clock.schedule_interval(self.throttledMouseHover, 0.1)

    def _keyboard_closed(self):
        # self._keyboard.unbind(on_key_down=self.handleKeyDown, on_key_up=self.handleKeyUp)
        # self._keyboard = None
        pass
        
    def handleKeyDown(self, keyboard, keycode, *args):
        if keycode[1] == 'spacebar':
            self.isSpaceHeld = True
        return True

    def handleKeyUp(self, keyboard, keycode, *args):
        if keycode[1] == 'spacebar': 
            self.isSpaceHeld = False
        return True

    def on_minimize(self, *largs):
        self.updateAllRenderPosition()

    def on_maximize(self, *largs):
        self.updateAllRenderPosition()

    def on_restore(self, *largs):
        self.updateAllRenderPosition()

    def on_resize(self, *largs):
        self.updateAllRenderPosition()

    def resetStartingView(self, sizeImage):
        self.imageWidth = sizeImage[0]
        self.imageHeight = sizeImage[1]
        zoomX = 1.0
        zoomY = 1.0
        maxLoop = 0
        while self.imageWidth * zoomX > Window.size[0]:
            maxLoop = maxLoop + 1
            zoomX = zoomX * 0.8
            if maxLoop > 9:
                break
        maxLoop = 0
        while self.imageHeight * zoomY > Window.size[1]:
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
        self.ids.editorCanvas.updateMeshImage(image)
        self.setInitialVertexPixel()
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
        self.ids.editorCanvas.updateIndices(xVertexCount, yVertexCount)
        
        Clock.schedule_once(self.updateAllRenderPosition, 0.1)
        
    # use the self.canvasSize
    def setInitialVertexPixel(self):

        incX = float(self.imageWidth) / float(self.countX - 1)
        incY = float(self.imageHeight) / (self.countY - 1)
        startX = - self.imageWidth / 2
        startY = - self.imageHeight / 2
        for i in range(self.countX):
            for j in range(self.countY):
                vertex: Vertex = self.vertices[i][j] 
                vertex.setPixelPos((startX + (i*incX), startY + (j*incY)))

    def updateAllRenderPosition(self, *largs): 
        # offset is always the same and it is so we base all pixels centered around 0,0 
        # so we offset everything by half the width and height of the canvas
        offsetX = self.ids.editorCanvas.size[0] / 2
        offsetY = self.ids.editorCanvas.size[1] / 2

        meshVertices = []
        for i in range(self.countX):
            for j in range(self.countY):
                u = float(i)/float(self.countX-1)
                v = float(j)/float(self.countY-1)
                vertex: Vertex = self.vertices[i][j] 
                self.updateVertexPositionFromPixel(vertex)
                meshVertices.extend([vertex.pos[0], vertex.pos[1], u,v])
        self.ids.editorCanvas.imagePlaceholderFrame.pos = (
            (self.viewX + -self.imageWidth/2) * self.zoom + offsetX,
            (self.viewY + -self.imageHeight/2) * self.zoom + offsetY)

        self.ids.editorCanvas.imagePlaceholderFrame.width = self.imageWidth * self.zoom
        self.ids.editorCanvas.imagePlaceholderFrame.height = self.imageHeight * self.zoom
        self.ids.editorCanvas.updateMeshVertices(meshVertices)

    def updateVertexPositionFromPixel(self, vertex):
        offsetX = self.ids.editorCanvas.size[0] / 2
        offsetY = self.ids.editorCanvas.size[1] / 2
        x = (self.viewX + vertex.pixelPos[0]) * self.zoom + offsetX
        y = (self.viewY + vertex.pixelPos[1]) * self.zoom + offsetY 
        vertex.updatePos((round(x)+0.4,round(y)+0.4)) #round and add a .4 to offset the 1 pixel opengl line so it is not blury lol
        
    def on_touch_down(self, touch):
        super(GridEditorWidget, self).on_touch_down(touch)
        pos = (touch.pos[0], touch.pos[1])

        try:
            if self.isSpaceHeld:
                # only drag, stop handling event
                self.isDraggingView = True
                return True
            #here we check if we are in range to grab any vertex.
            offsetX = self.ids.editorCanvas.size[0] / 2
            offsetY = self.ids.editorCanvas.size[1] / 2
            pixelPos = (
                (pos[0] - self.ids.editorCanvas.pos[0] - offsetX) / self.zoom - self.viewX,
                (pos[1] - self.ids.editorCanvas.pos[1] - offsetY) / self.zoom - self.viewY
            )
            maxDist = self.HOVER_DISTANCE / self.zoom 
            nearestVertex = None
            for i in range(self.countX):
                for j in range(self.countY):
                    vertex: Vertex = self.vertices[i][j] 
                    vertex.updateHighlight(False)
                    dist = vertex.getDistanceFrom(pos=pixelPos, maxDist=maxDist)
                    if dist >= 0:
                        if nearestVertex is None or nearestDist > dist:
                            nearestDist = dist
                            nearestVertex = vertex
            if nearestVertex is not None:
                self.dragVertex = nearestVertex
                self.isDraggingVertex = True
        finally:
            self.previousTouchPos = pos
            self.previousDragPos = pos

    def on_touch_up(self, touch):
        self.isDraggingView = False
        self.isDraggingVertex = False

    def on_touch_move(self, touch):
        pos = (touch.pos[0], touch.pos[1])
        try:    
            dX = (touch.pos[0] - self.previousDragPos[0]) / self.zoom
            dY = (touch.pos[1] - self.previousDragPos[1]) / self.zoom
            if self.isDraggingView:
                self.viewX = self.viewX + dX
                self.viewY = self.viewY + dY
                self.updateAllRenderPosition()
            if self.isDraggingVertex:
                self.dragVertex.movePixelPos(-dX, -dY)
                self.updateVertexPositionFromPixel(self.dragVertex)
                self.ids.editorCanvas.updateSingleVertex(self.dragVertex)
                print(self.dragVertex.coordinate)
        finally:
            self.previousDragPos = pos

    # we going to use this to check hover events. and thus lets just debounce it 
    # so it doesnt spamm it and we dont keep iterating over all vertices or something

    previousMouseEventTime = 0
    previousMouseEventPos = (0,0)
    def on_mouse_pos(self, window, pos):
        self.previousMouseEventPos = pos
        self.previousMouseEventTime = time.time()

    previousMouseEventUpdateTime = 0.1
    def throttledMouseHover(self, *largs):
        t = time.time()
        if self.previousMouseEventTime > self.previousMouseEventUpdateTime:
            self.previousMouseEventUpdateTime = t
            self.handleMouseHover(self.previousMouseEventPos)

    def handleMouseHover(self, pos):
        offsetX = self.ids.editorCanvas.size[0] / 2
        offsetY = self.ids.editorCanvas.size[1] / 2
        pixelPos = ((pos[0] - self.ids.editorCanvas.pos[0] - offsetX) / self.zoom - self.viewX,
            (pos[1] - self.ids.editorCanvas.pos[1] - offsetY) / self.zoom - self.viewY
        )
        maxDist = self.HOVER_DISTANCE / self.zoom

        nearestVertex = None
        nearestDist = 0.0
        for i in range(self.countX):
            for j in range(self.countY):
                vertex: Vertex = self.vertices[i][j] 
                vertex.updateHighlight(False)
                dist = vertex.getDistanceFrom(pos=pixelPos, maxDist=maxDist)
                if dist >= 0:
                    if nearestVertex is None or nearestDist > dist:
                        nearestDist = dist
                        nearestVertex = vertex
        if nearestVertex is not None:
            nearestVertex.updateHighlight(True)


print()