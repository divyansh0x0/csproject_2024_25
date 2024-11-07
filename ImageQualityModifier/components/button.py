import pygame


# Button class for creating interactive buttons
class Button:
    def __init__(self, bg, hover_color, text_color, font, text, size, pos):
        self.bg_color = bg
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font
        self.text = text
        self.size = size
        self.pos = pos

    # Set button position
    def set_pos(self, x, y):
        self.pos = (x, y)

    # Draw button on surface
    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        bg_color = self.hover_color if self.contains_point(mouse_pos[0], mouse_pos[1]) else self.bg_color
        pygame.draw.rect(surface, bg_color, rect=(self.pos[0], self.pos[1], self.size[0], self.size[1]),
                         border_radius=10)
        txt_size = self.font.size(self.text)
        surface.blit(self.font.render(self.text, True, self.text_color),
                     (self.pos[0] + self.size[0] / 2 - txt_size[0] / 2, self.pos[1] + self.size[1] / 2 - txt_size[1] / 2))

    # Set button text
    def set_text(self, text):
        self.text = text

    # Check if a point is inside the button bounds
    def contains_point(self, x, y):
        return self.pos[0] <= x <= self.pos[0] + self.size[0] and self.pos[1] <= y <= self.pos[1] + self.size[1]
