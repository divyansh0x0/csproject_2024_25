import pygame


# Slider class for interactive sliders
class Slider:

    def __init__(self, bg, slider_color, text_color, font, min_val, max_val, value, text, size, pos):
        self.bg_color = bg
        self.slider_color = slider_color
        self.text_color = text_color
        self.font = font
        self.size = size
        self.pos = pos
        self.value = value
        self.text = text

        if max_val < min_val:
            raise ValueError("max_val cannot be less than min_val")
        if max_val < 0 or min_val < 0:
            raise ValueError("max_val and min_val cannot be less than 0")
        self.min_val = min_val
        self.max_val = max_val
        self.value_range = self.max_val - self.min_val

    # Set slider size
    def set_size(self, width, height):
        self.size = (width, height)

    # Set slider position
    def set_pos(self, x, y):
        self.pos = (x, y)

    # Set slider text
    def set_text(self, text):
        self.text = text

    # Get the slider's value ratio between min and max
    def get_ratio(self):
        return (self.value - self.min_val) / (self.max_val - self.min_val)

    # Draw slider on the surface
    def draw(self, surface):
        ratio = self.get_ratio()
        # draw background color
        bounds = (self.pos[0], self.pos[1], self.size[0], self.size[1])
        pygame.draw.rect(surface, self.bg_color, rect=bounds, border_radius=10)
        # draw slider
        pad = 5
        bounds = (self.pos[0] + pad, self.pos[1] + pad, ratio * (self.size[0] - 2 * pad), self.size[1] - 2 * pad)
        pygame.draw.rect(surface, self.slider_color, rect=bounds, border_radius=10)

        # get the size of rectangle that can store the text
        txt_size_rect = self.font.size(self.text)
        # draw text
        x = self.pos[0] + (self.size[0] - txt_size_rect[0]) / 2
        y = self.pos[1] + (self.size[1] - txt_size_rect[1]) / 2
        text_surface = self.font.render(self.text, True, self.text_color)
        surface.blit(text_surface, (x, y))

    # Set slider value within min-max range
    def set_value(self, value):
        self.value = max(min(value, self.max_val), self.min_val)
        self.value = round(self.value, 2)

    # Check if a point is within the slider bounds
    def contains_point(self, x, y):
        return self.pos[0] <= x <= self.pos[0] + self.size[0] and self.pos[1] <= y <= self.pos[1] + self.size[1]

    # Set slider value based on a ratio
    def set_value_ratio(self, ratio):
        self.set_value(self.min_val + self.value_range * max(0, min(1, ratio)))
