import io, os, math, time

from PIL import Image
import pygame

from components.button import Button
from components.slider import Slider
from components.toast import Toast


def is_valid_img_path(im_path):
    """
    Validate img path and file type
    """
    return (os.path.exists(im_path)
            and os.path.isfile(im_path)
            and os.path.splitext(im_path)[1].lower() in [".jpeg", ".jpg"])


def format_byte_count(size_bytes):
    """
    Format byte size to human-readable format
    """
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    s = round(size_bytes / 1024 ** i, 2)
    return f"{s} {size_name[i]}"


# Main application class
class App:
    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((640, 480), flags=pygame.RESIZABLE)
        self.pad = 20

        try:
            pygame.display.set_caption("Image Quality Modifier", "Image Quality Modifier")
        except Exception as e:
            print(e)

        # RGB colors
        self.img_info_text_bg = pygame.Color("#191c20")
        self.img_info_text_color = pygame.Color("#e2e2e9")
        self.__bg_color = pygame.Color("#111318")
        
        slider_bg = pygame.Color("#284777")
        slider_fg = pygame.Color("#aac7ff")
        slider_text_color = pygame.Color("#000000")
        
        save_btn_bg = pygame.Color("#bec6dc")
        save_btn_hover_color = pygame.Color("#d5ddf5")
        save_btn_text_color = pygame.Color("#283141")
        
        toast_bg =  pygame.Color("#33353a")
        toast_fg = pygame.Color("#e2e2e9")
        
        # booleans
        self.is_dragging_on_res_slider = False
        self.is_dragging_on_quality_slider = False
        self.was_save_btn_pressed = False
        self.is_right_mouse_btn_pressed_on_window = False

        # text
        self.info_text_height = 0
        self.font = pygame.font.SysFont(None, 24)

        # image variables
        self.img_quality = 0
        self.predicted_img_size = None
        self.imgRenderPos = (100, 100)
        self.img_render_size = (0, 0)
        self.img_org_res = (0, 0)
        self.new_img_res = (0, 0)
        self.img_extension = None
        self.original_img_path = None
        self.modified_img_path = None
        self.img_info_dict = {"Original Image Resolution": "",
                              "New Image Resolution": "",
                              "Save path": "",
                              "Quality": "",
                              "Size": ""
                              }

        # stores the amount mouse was dragged in x-axis and y-axis
        self.drag_delta = (0, 0)
        self.zoom = 1.0
        self.MIN_ZOOM = 0.3
        self.MAX_ZOOM = 5.0

        # image surface
        self.original_img_surface = None  # used to maintain a copy of original image in memory to allow fast resizing
        self.modified_img_surface = None  # stores the image with new quality and resolution
        self.active_img_surface = None  # this image surface is what is visible as image preview
        # save button
        self.save_btn = Button(save_btn_bg, save_btn_hover_color, save_btn_text_color, self.font, "Save",
                               (80, 40), (0, 0))
        # A toast component used to display popup messages
        self.toast = Toast("Drag an image here", self.font, 5, toast_fg, toast_bg)

        # two sliders used for changing resolution of image or quality of image

        self.resolution_slider = Slider(slider_bg, slider_fg, slider_text_color, self.font, 1, 100, 100,
                                        "Resolution: 0 x 0",
                                        (200, 40), (0, 0))
        self.quality_slider = Slider(slider_bg, slider_fg, slider_text_color, self.font, 1, 100, 100, "Quality: 100%",
                                     (200, 40),
                                     (0, 0))
        # show "Drag an image here" message on app launch
        self.toast.show()

    def update_image_quality_and_resolution(self, new_quality, new_resolution):
        """
        This function will use PIL to modify the self.active_img_surface to the quality and resolution set by the user using
        the sliders
        """
        # save original unmodified pygame surface to BytesIO buffer
        curr_img_buffer = io.BytesIO()
        pygame.image.save(self.original_img_surface, curr_img_buffer, self.img_extension)
        # load buffer as PIL image and convert it into RGB format.
        # Then it is resized to new_resolution  and saved with new_quality
        pil_img = Image.open(curr_img_buffer, mode="r")
        pil_img = pil_img.convert("RGB").resize(new_resolution, Image.Resampling.LANCZOS)

        # update information regarding image
        new_img_buffer = io.BytesIO()
        pil_img.save(new_img_buffer, format="JPEG", optimized=True, quality=new_quality)
        new_img_size = new_img_buffer.tell()

        self.img_info_dict["Quality"] = f"{new_quality}%"
        self.img_info_dict["New Image Resolution"] = f"{new_resolution[0]} x {new_resolution[1]}"
        self.img_info_dict["Size"] = format_byte_count(new_img_size)

        # load image back as pygame surface
        new_img_buffer.seek(0)
        self.modified_img_surface = pygame.image.load(new_img_buffer, "JPEG")
        # scales the image to new resolution
        self.active_img_surface = pygame.transform.scale(self.modified_img_surface, self.img_render_size)
        # close the buffers
        pil_img.close()
        curr_img_buffer.close()
        new_img_buffer.close()

    def save_img(self):
        """
        Saves image to self.modified_img_path
        """
        try:
            if self.original_img_surface is not None and self.modified_img_path is not None:
                print("Saving img to", self.modified_img_path)
                new_quality = self.quality_slider.value
                pil_image = Image.open(self.original_img_path)
                pil_image = pil_image.convert("RGB").resize(self.new_img_res, Image.Resampling.LANCZOS)
                pil_image.save(self.modified_img_path, format="JPEG", optimized=True, quality=new_quality)
                pil_image.close()
                self.toast.show("Image saved")
        except Exception as ex:
            self.toast.show(f"Error occurred: {str(ex)}")

    def load_img(self, path):
        """
        Used for loading img for first time
        """

        try:
            if not is_valid_img_path(path):
                self.toast.show(f"Invalid image: {os.path.basename(path)}. Only JPEGs are supported")
                return

            self.original_img_path = path
            # adds modified_ as suffix for the name the img will be saved as
            self.modified_img_path = os.path.join(os.path.dirname(self.original_img_path),
                                                  f'modified_{os.path.basename(self.original_img_path)}')
            # retrieves extension of image
            self.img_extension = os.path.splitext(self.modified_img_path)[1].lower()
            self.active_img_surface = pygame.image.load(self.original_img_path)
            self.modified_img_surface = pygame.image.load(self.original_img_path)
            self.original_img_surface = pygame.image.load(self.original_img_path)

            self.img_org_res = (self.active_img_surface.get_width(), self.active_img_surface.get_height())
            self.img_render_size = self.img_org_res
            self.new_img_res = (self.active_img_surface.get_width(), self.active_img_surface.get_height())

            self.resolution_slider.set_value(self.resolution_slider.max_val)
            self.img_info_dict["Save path"] = self.modified_img_path
            self.img_info_dict["Original Image Resolution"] = f"{self.img_org_res[0]} x {self.img_org_res[1]}"
            self.img_info_dict["New Image Resolution"] = f"{self.new_img_res[0]} x {self.new_img_res[1]}"
            self.img_info_dict["Quality"] = "100%"
            self.img_info_dict["Size"] = format_byte_count(os.path.getsize(path))

            self.quality_slider.set_value_ratio(1)
            self.resolution_slider.set_value_ratio(1)
            print(f"Loaded {self.original_img_path} {self.modified_img_path}")

        except Exception as e:
            self.toast.show("Error occurred:" + e.args[0])

    def draw_img_info_text(self):
        """
        Renders the text in self.img_info_dict
        """
        render_area = (self.screen.get_width() - self.pad * 2, self.screen.get_height())
        total_lines = len(self.img_info_dict)
        bg_height = (self.font.get_height() + 5.5) * total_lines
        bg_width = self.screen.get_width() - 20
        bg_bounds = (10, 10, bg_width, bg_height)
        pygame.draw.rect(self.screen, self.img_info_text_bg, bg_bounds, border_radius=10)

        ty = self.pad  # store y position of line
        for key, value in self.img_info_dict.items():
            text = str(key) + " : " + str(value)
            # Clip the text if it is too long
            if self.font.size(text)[0] > render_area[0]:
                while self.font.size(text + "...")[0] > render_area[0]:
                    text = text[:-1]
                text += "..."
            # render the text
            text = self.font.render(text, True, self.img_info_text_color)
            self.screen.blit(text, (self.pad, ty))
            ty += text.get_height()
        self.info_text_height = ty

    def handle_event(self, event_data):
        """
        All application events are handled here
        """
        # checks if user dropped a file
        if event_data.type == pygame.DROPFILE:
            self.load_img(event_data.dict["file"])

        elif event_data.type == pygame.MOUSEBUTTONDOWN:
            # check if left mouse button was pressed
            if event_data.dict["button"] == 1:
                mouse_pos = event_data.dict["pos"]
                # checks if save button was pressed
                if self.save_btn.contains_point(mouse_pos[0], mouse_pos[1]):
                    self.was_save_btn_pressed = True
                #check if resolution slider was pressed                        
                if self.resolution_slider.contains_point(mouse_pos[0], mouse_pos[1]):
                    self.is_dragging_on_res_slider = True
                    slider_ratio = (mouse_pos[0] - self.resolution_slider.pos[0]) / self.resolution_slider.size[0]
                    self.resolution_slider.set_value_ratio(slider_ratio)
                #check if quality slider was pressed                        
                        
                if self.quality_slider.contains_point(mouse_pos[0], mouse_pos[1]):
                    self.is_dragging_on_quality_slider = True
                    slider_ratio = (mouse_pos[0] - self.quality_slider.pos[0]) / self.quality_slider.size[0]
                    self.quality_slider.set_value_ratio(slider_ratio)
            # check if right mouse button is pressed
            elif event_data.dict["button"] == 3:
                # checks if user is dragging the mouse around
                pygame.mouse.get_rel()
                self.is_right_mouse_btn_pressed_on_window = True

        elif event_data.type == pygame.MOUSEBUTTONUP:
            mouse_pos = event_data.dict["pos"]
            # Checks if save button was released
            if self.was_save_btn_pressed and self.save_btn.contains_point(mouse_pos[0], mouse_pos[1]):
                self.save_img()
                self.was_save_btn_pressed = False
            if self.resolution_slider.contains_point(mouse_pos[0], mouse_pos[1]):
                self.is_dragging_on_res_slider = False    
            if self.quality_slider.contains_point(mouse_pos[0], mouse_pos[1]):
                self.is_dragging_on_quality_slider
            self.is_right_mouse_btn_pressed_on_window = False

        # checks if user is zooming
        elif event_data.type == pygame.MOUSEWHEEL:
            delta = event_data.dict["precise_y"]
            self.zoom += 0.5 * delta
            if self.zoom < self.MIN_ZOOM:
                self.zoom = self.MIN_ZOOM
            if self.zoom > self.MAX_ZOOM:
                self.zoom = self.MAX_ZOOM

    def update(self):
        """
        Responsible for updating the logic of the application. It updates the position, size and logic of all components
        based on how user interacts with app
        """
        pad = self.pad

        # code for resolution slider logic
        mouse_pos = pygame.mouse.get_pos()
        screen_size = self.screen.get_size()
        slider_size = (screen_size[0] - self.save_btn.size[0] - pad * 2, self.resolution_slider.size[1])
        slider_x_pos = (screen_size[0] - slider_size[0] - self.save_btn.size[0]) / 2
        slider_y_pos = screen_size[1] - slider_size[1] - pad

        self.resolution_slider.set_pos(slider_x_pos, slider_y_pos)
        self.resolution_slider.set_size(slider_size[0], slider_size[1])

        # check if mouse is on resolution slider or user has been dragging on slider
        # if yes then update the value of the slider

        if self.is_dragging_on_res_slider:
            if pygame.mouse.get_pressed()[0]:
                # if mouse is on slider and left mouse button is pressed then set is_dragging_on_slider to True
                # and set the value of the slider based on position of mouse on slider
                slider_ratio = (mouse_pos[0] - self.resolution_slider.pos[0]) / self.resolution_slider.size[0]
                self.resolution_slider.set_value_ratio(slider_ratio)
                self.is_dragging_on_res_slider = True
            else:
                # if user was dragging on slider and has released the left mouse button then
                # update the image size based on value of slider
                if self.is_dragging_on_res_slider and self.active_img_surface is not None:
                    ratio = self.resolution_slider.value / self.resolution_slider.max_val
                    self.new_img_res = (
                        int(self.img_org_res[0] * ratio), int(self.img_org_res[1] * ratio))

                    self.update_image_quality_and_resolution(self.quality_slider.value, self.new_img_res)

                # set dragging to false because left mouse button has been released
                self.is_dragging_on_res_slider = False

        # code for quality slider logic
        mouse_pos = pygame.mouse.get_pos()
        screen_size = self.screen.get_size()
        slider_size = (screen_size[0] - self.save_btn.size[0] - pad * 2, self.quality_slider.size[1])
        slider_x_pos = (screen_size[0] - slider_size[0] - self.save_btn.size[0]) / 2
        slider_y_pos = screen_size[1] - slider_size[1] - self.resolution_slider.size[1] - 2 * pad
        self.quality_slider.set_pos(slider_x_pos, slider_y_pos)
        self.quality_slider.set_size(slider_size[0], slider_size[1])

        # check if mouse is on resolution slider or user has been dragging on slider
        # if yes then update the value of the slider

        if self.is_dragging_on_quality_slider:
            if pygame.mouse.get_pressed()[0]:
                # if mouse is on slider and left mouse button is pressed then set is_dragging_on_slider to True
                # and set the value of the slider based on position of mouse on slider
                slider_ratio = (mouse_pos[0] - self.quality_slider.pos[0]) / self.quality_slider.size[0]
                new_slider_val = int(self.quality_slider.max_val * slider_ratio)
                self.quality_slider.set_value(new_slider_val)
                self.is_dragging_on_quality_slider = True
            else:
                # if user was dragging on slider and has released the left mouse button then
                # update the image size based on value of slider
                if self.is_dragging_on_quality_slider and self.active_img_surface is not None:
                    ratio = self.resolution_slider.value / self.resolution_slider.max_val
                    self.new_img_res = (int(self.img_org_res[0] * ratio), int(self.img_org_res[1] * ratio))

                    self.update_image_quality_and_resolution(self.quality_slider.value, self.new_img_res)

                # set dragging to false because left mouse button has been released
                self.is_dragging_on_quality_slider = False

        # update text of both sliders
        self.resolution_slider.set_text(f"Resolution: {self.new_img_res[0]} x {self.new_img_res[1]}")
        self.quality_slider.set_text("Quality : " + str(self.quality_slider.value) + "%")

        # the following code is for rendering image preview with appropriate size and position
        # without it the alignment of image preview will be wrong
        if self.active_img_surface is not None:
            ratio = self.img_org_res[0] / self.img_org_res[1]

            # calculate image preview size in the center
            min_size = (self.quality_slider.pos[1] - self.info_text_height) - 2 * pad
            max_size = self.screen.get_width() - 2 * pad
            new_width = min(max_size, min_size * ratio)
            new_height = min(min_size, max_size / ratio)
            self.img_render_size = (abs(round(new_width * self.zoom)), abs(round(new_height * self.zoom)))
            # align image preview to center
            x = (self.screen.get_width() - self.img_render_size[0]) / 2
            y = (self.screen.get_height() - self.quality_slider.pos[1] + self.info_text_height) / 2 + pad

            # apply mouse drag if any
            x += self.drag_delta[0]
            y += self.drag_delta[1]
            self.imgRenderPos = (x, y)

        # update save button position
        self.save_btn.set_pos(self.screen.get_width() - self.save_btn.size[0] - pad / 2,
                              self.resolution_slider.pos[1])

        # update drag parameter if user was dragging mouse around
        if self.is_right_mouse_btn_pressed_on_window:
            new_drag_delta = pygame.mouse.get_rel()
            self.drag_delta = (self.drag_delta[0] + new_drag_delta[0], self.drag_delta[1] + new_drag_delta[1])
        # else:
        # self.drag_delta = (0, 0)

    def render(self):
        """
        Handles rendering of every component visible on screen
        """
        self.screen.fill(self.__bg_color)

        border_width = 10
        # draw the image if it has been loaded
        if self.active_img_surface is not None:
            # if the expected image size does not match the size of image surface then resize the surface
            if (self.img_render_size[0] != self.active_img_surface.get_width()
                    or self.img_render_size[1] != self.active_img_surface.get_height()):
                self.active_img_surface = pygame.transform.scale(self.modified_img_surface, self.img_render_size)

                self.update_image_quality_and_resolution(self.quality_slider.value, self.new_img_res)
            # draw a border around image
            img_border = (self.imgRenderPos[0] - border_width, self.imgRenderPos[1] - border_width,
                          self.img_render_size[0] + 2 * border_width,
                          self.img_render_size[1] + 2 * border_width)
            pygame.draw.rect(self.screen, (0, 0, 0), img_border, border_radius=10)
            # draw the image
            self.screen.blit(self.active_img_surface, self.imgRenderPos)
        # draw resolution slider
        self.resolution_slider.draw(self.screen)
        # draw quality slider
        self.quality_slider.draw(self.screen)
        # draw save button
        self.save_btn.draw(self.screen)
        # draw toast
        self.toast.draw(self.screen)
        # draw overlaying text that contains information regarding the image
        self.draw_img_info_text()

    def loop(self):
        """
        Application loop which renders components and updates logic at 60 frames per second
        """

        max_fps = 60
        min_frame_time = 1e9 / max_fps

        t1 = time.time_ns()
        stop = False

        # the application loop, used for updating and rendering at a maximum of 60 fps
        while not stop:
            # process events
            for event in pygame.event.get():
                # check if user wants to quit and exit if true
                if event.type == pygame.QUIT:
                    stop = True
                else:
                    self.handle_event(event)
            # code to make sure the application runs at 60 frames per second
            t2 = time.time_ns()
            dt = t2 - t1
            if dt < min_frame_time:
                continue
            # update and then render in every frame
            self.update()
            self.render()
            pygame.display.update()
            t1 = t2

# Start app
if __name__ == "__main__":
    app = App()
    app.loop()
