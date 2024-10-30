# Toast class for displaying temporary messages on screen
import time
import pygame

class Toast:
    def __init__(self, msg, font, duration_secs, text_color=(255, 255, 255), bg_color=(0, 0, 0)):
        self.msg = msg
        self.font = font
        self.text_color = text_color
        self.bg_color = bg_color
        self.duration_secs = duration_secs
        self.isShowing = False

    # Show toast message
    def show(self, msg=None):
        if msg:
            self.setMessage(msg)
        self.time_displayed_at_ns = time.time_ns()
        self.isShowing = True

    # Hide toast message
    def hide(self):
        self.isShowing = False

    # Set the message for the toast
    def setMessage(self, msg):
        self.msg = msg

    # Draw toast message on the surface
    def draw(self, surface):
        if self.isShowing and (time.time_ns() - self.time_displayed_at_ns) * 1e-9 >= self.duration_secs:
            self.hide()
        if self.isShowing:
            pad = 10
            text = self.msg
            # Trim message to fit width
            if self.font.size(text)[0] > surface.get_width() - pad * 2:
                while self.font.size(text + "...")[0] > surface.get_width() - pad * 2:
                    text = text[:-1]
                text += "..."
            #get the rectangle (width,height) that can store the text    
            text_size = self.font.size(text)
            #code to center align the text
            t_x = surface.get_width() / 2 - text_size[0] / 2
            t_y =  surface.get_height() / 2- text_size[1] / 2
            toast_background_rect = (t_x - pad, t_y - pad , text_size[0] + pad * 2, text_size[1] + pad * 2)
            #draw background of toast
            pygame.draw.rect(surface, self.bg_color, toast_background_rect, border_radius=10)
            #draw text            
            surface.blit(self.font.render(text, True, self.text_color, self.bg_color), (t_x, t_y))

