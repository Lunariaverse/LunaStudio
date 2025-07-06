# Simple Layer Draw


class Layer:

    def __init__(self, name):
        self.name = name
        self.objects = []

    def add(self, obj):
        print("Add Obj: ", obj)
        self.objects.append(obj)

    def remove(self, obj):
        if obj in self.objects:
            self.objects.remove(obj)

    def draw(self, surface):
        for obj in self.objects:
            surface.blit(obj[0], obj[1])


class LayerManager:

    def __init__(self):
        self.layer = []

    def addLayer(self, layer, index=None):
        print("Add Layer: ", layer)
        print("Add Layer Index: ", index)
        if index is None:
            self.layer.append(layer)
        else:
            self.layer.insert(index, layer)

    def removeLayer(self, layerName):
        self.layer = [layer for layer in self.layer if layer.name != layerName]
        print("Add Layer Removed: ", layerName)

    def draw(self, surface):
        print("drawing surface here")
        for layer in self.layer:
            layer.draw(surface)
