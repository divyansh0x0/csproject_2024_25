import time

import pygame


# Toast class for displaying temporary messages on screen
class Toast:
    def __init__(self, msg, font, duration_secs, text_color, bg_color):
        self.start_time_ns = None
        self.msg = msg
        self.font = font
        self.text_color = text_color
        self.bg_color = bg_color
        self.dur_secs = duration_secs
        self.isShowing = False

    # Show toast message
    def show(self, msg=None):
        if msg:
            self.set_message(msg)
        self.start_time_ns = time.time_ns()
        self.isShowing = True

    # Hide toast message
    def hide(self):
        self.isShowing = False

    # Set the message for the toast
    def set_message(self, msg):
        self.msg = msg

    # Draw toast message on the surface
    def draw(self, surface):
        if self.isShowing and (
                time.time_ns() - self.start_time_ns) * 1e-9 >= self.dur_secs:
            self.hide()

        if self.isShowing:
            pad = 10
            text = self.msg
            # Trim message to fit width
            if self.font.size(text)[0] > surface.get_width() - pad * 2:
                while self.font.size(text + "...")[0] > surface.get_width() - pad * 2:
                    text = text[:-1]
                text += "..."

            # get size of text so that the size of background can be determined
            text_size = self.font.size(text)

            # code to center align the text
            t_x = surface.get_width() / 2 - text_size[0] / 2
            t_y = surface.get_height() / 2 - text_size[1] / 2
            toast_bg_rect = (t_x - pad, t_y - pad,
                             text_size[0] + pad * 2, text_size[1] + pad * 2)

            # draw background of toast
            pygame.draw.rect(surface, self.bg_color, toast_bg_rect, border_radius=10)

            # draw text
            font_surface = self.font.render(text, True, self.text_color, self.bg_color)
            surface.blit(font_surface, (t_x, t_y))
