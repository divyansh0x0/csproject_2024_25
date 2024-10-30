import pygame
# Slider class for interactive sliders
class Slider:
    
    def __init__(self, bg, slider_color, text_color, font, min_val, max_val, value=0, text="", size=(200, 40), pos=(0, 0)):
        self.slider_color = slider_color
        self.bg_color = bg
        self.text_color = text_color
        self.font = font
        self.size = size
        self.pos = pos
        self.value = value
        self.text = text
        self.setMinMaxValues(min_val, max_val)

    # Set slider min and max values
    def setMinMaxValues(self, min_val, max_val):
        
        if max_val < min_val:
            raise ValueError("max_val cannot be less than min_val")
        if max_val < 0 or min_val < 0:
            raise ValueError("max_val and min_val cannot be less than 0")
        self.min_val = min_val
        self.max_val = max_val
        self.value_range = self.max_val - self.min_val

    # Set slider size
    def setSize(self, width, height):
        self.size = (width, height)

    # Set slider position
    def setPos(self, x, y):
        self.pos = (x, y)

    # Set slider text
    def setText(self, text):
        self.text = text
        
    # Get the slider's value ratio between min and max
    def getRatio(self):
        return (self.value - self.min_val) / (self.max_val - self.min_val)

    # Draw slider on the surface
    def draw(self, surface):
        ratio = self.getRatio()
        #draw background color
        pygame.draw.rect(surface, self.bg_color, rect=(self.pos[0], self.pos[1], self.size[0], self.size[1]), border_radius=10)
        #draw slider
        pygame.draw.rect(surface, self.slider_color, rect=(self.pos[0], self.pos[1], ratio * self.size[0], self.size[1]), border_radius=10)
        
        #get the size of rectangle that can store the text
        txt_size_rect = self.font.size(self.text)
        #draw text
        surface.blit(self.font.render(self.text, True, self.text_color), (self.pos[0] + self.size[0] / 2 - txt_size_rect[0] / 2, self.pos[1] + self.size[1] / 2 - txt_size_rect[1] / 2))

    # Set slider value within min-max range
    def setValue(self, value):
        self.value = max(min(value, self.max_val), self.min_val)
        self.value = round(self.value, 2)

    # Check if a point is within the slider bounds
    def containsPoint(self, x, y):
        return self.pos[0] <= x <= self.pos[0] + self.size[0] and self.pos[1] <= y <= self.pos[1] + self.size[1]

    # Set slider value based on a ratio
    def setValueRatio(self, ratio):
        self.setValue(self.min_val + self.value_range * max(0, min(1, ratio)))
