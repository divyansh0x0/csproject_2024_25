import pygame
# Button class for creating interactive buttons
class Button:
    def __init__(self, bg, hover_color, text_color, font, text, size=(200, 40), pos=(0, 0)):
        self.bg_color = bg
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font
        self.text = text
        self.size = size
        self.pos = pos

    # Set button position
    def setPos(self, x, y):
        self.pos = (x, y)

    # Draw button on surface
    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        bg_color = self.hover_color if self.containsPoint(mouse_pos[0], mouse_pos[1]) else self.bg_color
        pygame.draw.rect(surface, bg_color, rect=(self.pos[0], self.pos[1], self.size[0], self.size[1]), border_radius=10)
        txtSize = self.font.size(self.text)
        surface.blit(self.font.render(self.text, True, self.text_color), (self.pos[0] + self.size[0] / 2 - txtSize[0] / 2, self.pos[1] + self.size[1] / 2 - txtSize[1] / 2))

    # Set button text
    def setText(self, text):
        self.text = text

    # Check if a point is inside the button bounds
    def containsPoint(self, x, y):
        return self.pos[0] <= x <= self.pos[0] + self.size[0] and self.pos[1] <= y <= self.pos[1] + self.size[1]
