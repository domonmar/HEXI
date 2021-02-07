import numpy as np
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox

from helpers import convert_image_pil_to_tk, set_entry_text
from custom_widgets import ToggleButton
from histogram import show_histogram
from image_processor import ImageProcessor


class ImageFrame(tk.Frame):
    def __init__(self, window, width, height):
        tk.Frame.__init__(self, window)

        self.display_scale = 1.0

        # Scale to fit display
        screenw = self.winfo_screenwidth() * 0.75
        screenh = self.winfo_screenheight() * 0.75
        screenwscale = screenw / width
        screenhscale = screenh / height
        screenscale = min(screenwscale, screenhscale)
        if screenscale < 1.0:
            self.display_scale = screenscale

        # Create image canvas:
        self.canvas = tk.Canvas(self, width=int(width * self.display_scale), height=int(height * self.display_scale))
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)
        self.canvas.pack_propagate(0)

        self.canvas.bind("<Button-1>", self.mouse_down)
        self.canvas.bind("<Motion>", self.mouse_move)
        self.canvas.bind("<Configure>", self.on_resize)

        self.input_top_left = (0, 0)
        self.input_bottom_right = (width, height)

        self.measurement_line = None
        self.measurement_label = None
        self.scale_factor = 1.0

        # Current input mode, value can be:
        # None - no input currently being processed
        # CropPoint1 - waiting for first coordinate of crop area (ROI)
        # CropPoint2 - waiting for second coordinate of crop area (ROI)
        # MeasurePoint1 - waiting for first coordinate of measurement line
        # MeasurePoint2 - waiting for second coordinate of measurement line
        self.input_mode = 'None'

        self.crop_area_changed_callback = None
        self.measurement_finished_callback = None

        # Create crop rectangle
        self.crop_rectangle = self.canvas.create_rectangle(0, 0, 0, 0, outline='blue', width=3)
        self.update_crop_rectangle()

        self.image = None
        self.image_object = None

    def on_resize(self, event):
        if self.image:
            wscale = event.width / self.image.width
            hscale = event.height / self.image.height

            display_scale = min(wscale, hscale)
            incremental_scale = display_scale / self.display_scale
            self.display_scale = display_scale

            # rescale all the objects
            self.canvas.scale("all", 0, 0, incremental_scale, incremental_scale)
            self.update_image_object()

    def get_active_crop_area(self):
        x0, y0, x1, y1 = self.canvas.coords(self.crop_rectangle)
        return (int(x0 / self.display_scale),
                int(y0 / self.display_scale),
                int(x1 / self.display_scale),
                int(y1 / self.display_scale))

    def set_active_crop_area(self, crop_area):
        self.set_active_crop_area_display_coords((
                           crop_area[0] * self.display_scale,
                           crop_area[1] * self.display_scale,
                           crop_area[2] * self.display_scale,
                           crop_area[3] * self.display_scale))

    # Sets the active crop area in display coordinates (for internal use)
    def set_active_crop_area_display_coords(self, crop_area):
        self.canvas.coords(self.crop_rectangle,
                           crop_area[0],
                           crop_area[1],
                           crop_area[2],
                           crop_area[3])
        self.canvas.tag_raise(self.crop_rectangle)

    # image expected as PIL image
    def set_image(self, image):
        self.image = image
        self.update_image_object()

    def update_image_object(self):
        if self.image_object:
            self.canvas.delete(self.image_object)

        if self.image:
            scaled_image = self.image.resize((int(self.image.width * self.display_scale),
                                              int(self.image.height * self.display_scale)))
            self.converted_image = convert_image_pil_to_tk(scaled_image)
            self.image_object = self.canvas.create_image(0, 0, image=self.converted_image, anchor=tk.NW)

            self.canvas.tag_raise(self.crop_rectangle)

            if self.measurement_line:
                self.canvas.tag_raise(self.measurement_line)
                self.canvas.tag_raise(self.measurement_label)

    def update_crop_rectangle(self):
        self.set_active_crop_area_display_coords(self.input_top_left + self.input_bottom_right)

        if self.crop_area_changed_callback:
            self.crop_area_changed_callback()

    def update_measurement_line(self):
        top_left = np.array(self.input_top_left)
        bottom_right = np.array(self.input_bottom_right)
        input_vector = bottom_right - top_left
        mid_position = (bottom_right + top_left) / 2.0
        offset_vector = np.array([-input_vector[1], input_vector[0]])
        offset_vector_length = np.linalg.norm(offset_vector)
        offset_vector = 30 * offset_vector / (offset_vector_length if offset_vector_length > 0.0 else 1.0)
        label_position = mid_position + offset_vector

        if not self.measurement_line:
            self.measurement_line = self.canvas.create_line(self.input_top_left[0],
                                                            self.input_top_left[1],
                                                            self.input_bottom_right[0],
                                                            self.input_bottom_right[1],
                                                            fill='yellow',
                                                            width=3)
            self.measurement_label = self.canvas.create_text(label_position[0],
                                                             label_position[1],
                                                             fill='yellow')

        self.canvas.coords(self.measurement_line,
                           self.input_top_left[0],
                           self.input_top_left[1],
                           self.input_bottom_right[0],
                           self.input_bottom_right[1])

        self.canvas.itemconfigure(self.measurement_label, text=str(
            int(self.scale_factor * np.linalg.norm(input_vector))) + ' nm')
        self.canvas.coords(self.measurement_label,
                           label_position[0],
                           label_position[1])

        self.canvas.tag_raise(self.measurement_line)

    def mouse_down(self, event):
        if 'Point1' in self.input_mode:
            self.input_top_left = (event.x, event.y)
            self.input_bottom_right = (event.x, event.y)

        if self.input_mode == 'CropPoint1':
            self.update_crop_rectangle()
            self.input_mode = 'CropPoint2'
        elif self.input_mode == 'CropPoint2':
            self.input_mode = 'None'

        if self.input_mode == 'MeasurePoint1':
            self.update_measurement_line()
            self.input_mode = 'MeasurePoint2'
        elif self.input_mode == 'MeasurePoint2':
            if self.measurement_finished_callback:
                input_vector = np.array(self.input_bottom_right) - np.array(self.input_top_left)
                self.measurement_finished_callback(np.linalg.norm(input_vector) / self.display_scale)
                self.measurement_finished_callback = None
            self.input_mode = 'None'

    def mouse_move(self, event):
        if 'Point2' in self.input_mode:
            x, y = event.x, event.y

            # Limit input area to image size:
            if self.image:
                x = min(x, self.image.size[0])
                y = min(y, self.image.size[1])

            self.input_bottom_right = (x, y)

        if self.input_mode == 'MeasurePoint2':
            self.update_measurement_line()

        if self.input_mode == 'CropPoint2':
            self.update_crop_rectangle()

    def measure(self, measurement_finished_callback):
        self.input_mode = 'MeasurePoint1'
        self.measurement_finished_callback = measurement_finished_callback

    # Initiates setting the ROI (Region of Interest)
    def set_roi(self):
        self.input_mode = 'CropPoint1'


class MeasurementWindow(tk.Toplevel):
    def __init__(self):
        tk.Toplevel.__init__(self)

        self.title('Measurement')

        frame = tk.Frame(self)
        frame.grid()  # fill=BOTH, expand=True

        length_label = tk.Label(frame, text='Length (px):')
        length_label.grid(column=1, row=1)

        self.length_entry_px = tk.Entry(frame, state=tk.DISABLED)
        self.length_entry_px.grid(column=2, row=1)

        length_label2 = tk.Label(frame, text='Length (nm):')
        length_label2.grid(column=1, row=2)

        length_nm_string_value = tk.StringVar()
        length_nm_string_value.trace(
            "w",
            lambda name,
            index, mode,
            sv=length_nm_string_value: self.on_length_nm_changed(sv.get()))

        self.length_entry_nm = tk.Entry(frame, textvariable=length_nm_string_value)
        self.length_entry_nm.grid(column=2, row=2)

        self.length_nm_changed_callback = None

    def set_length_px(self, value):
        self.length_entry_px.configure(state=tk.NORMAL)
        set_entry_text(self.length_entry_px, str(int(value)))
        self.length_entry_px.configure(state=tk.DISABLED)

    def set_length_nm(self, value):
        set_entry_text(self.length_entry_nm, str(int(value)))

    def set_lenght_nm_changed_callback(self, callback):
        self.length_nm_changed_callback = callback

    def on_length_nm_changed(self, string_value):
        try:
            length_nm = int(string_value)
            if self.length_nm_changed_callback:
                self.length_nm_changed_callback(length_nm)
        except ValueError:
            return


class ImageWindow(tk.Toplevel):
    def __init__(self, image_path, title):
        tk.Toplevel.__init__(self)

        self.title(title)

        # Create button bar:
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(fill=tk.BOTH, expand=True)

        self.perimeter_button = ToggleButton(
            self.button_frame,
            text="Perimeter",
            width=12,
            default_state=True,
            command=self.button_toggled)
        self.perimeter_button.pack(side=tk.LEFT)

        self.info_button = ToggleButton(
            self.button_frame,
            text="Info",
            width=12,
            default_state=True,
            command=self.button_toggled)
        self.info_button.pack(side=tk.LEFT)

        self.histogram_button = tk.Button(
            self.button_frame,
            text="Histogram",
            width=12,
            command=lambda: self.button_toggled(self.histogram_button, True))
        self.histogram_button.pack(side=tk.LEFT)

        self.roi_button = tk.Button(self.button_frame, text="ROI", width=12, command=self.set_roi)
        self.roi_button.pack(side=tk.LEFT)

        self.measure_button = tk.Button(self.button_frame, text="Measure", width=12, command=self.start_measurement)
        self.measure_button.pack(side=tk.LEFT)

        self.save_button = tk.Button(self.button_frame, text="Save", width=12, command=self.save_image)
        self.save_button.pack(side=tk.LEFT)

        self.on_button_toggle_callback = None

        self.scale_factor = 1.0  # nm/px ratio

        # Create image processor:
        self.image_processor = ImageProcessor(image_path)

        # Create image frame:
        width, height = self.image_processor.get_image_size()
        self.frame = ImageFrame(self, width, height)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.frame.crop_area_changed_callback = self.on_crop_area_changed
        self.image_processor.autodetect_crop_area()
        self.frame.set_active_crop_area(self.image_processor.active_crop_area)

        self.update_result_image()

    def evaluate(self, detector, classifier, parameters):
        self.image_processor.evaluate(detector, classifier, parameters)
        self.update_result_image()

    def update_result_image(self):
        self.image_processor.update_result_image()
        self.frame.set_image(self.image_processor.result_image)

    def button_toggled(self, button, button_is_pressed):
        button_id = button.config('text')[-1]

        if button_id == "Perimeter":
            self.image_processor.draw_perimeters = button_is_pressed
            self.update_result_image()

        if button_id == "Info":
            self.image_processor.draw_info_text = button_is_pressed
            self.update_result_image()

        if button_id == "Histogram":
            if len(self.image_processor.circles) > 0:
                # Display histogram:
                diameters_in_nm = list(
                    2 * int(circle[2] * self.scale_factor)
                    for circle
                    in self.image_processor.circles)
                show_histogram(diameters_in_nm)

    def save_image(self):
        if self.frame.image:
            file_types = [("JPEG", "*.jpg"), ("PNG", "*.png"), ("All Files", "*")]
            file_path = tkinter.filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=file_types)
            self.frame.image.save(file_path)

    def change_scale_lenght(self, scale_factor):
        self.scale_factor = scale_factor
        self.frame.scale_factor = scale_factor

    def on_measurement_finished(self, measured_length):
        measurement_window = MeasurementWindow()
        measurement_window.set_length_px(measured_length)
        measurement_window.set_length_nm(measured_length * self.scale_factor)
        measurement_window.set_lenght_nm_changed_callback(
            lambda x: self.change_scale_lenght(float(x) / float(measured_length)))

    def start_measurement(self):
        self.frame.measure(self.on_measurement_finished)

    def set_roi(self):
        self.frame.set_roi()

    def on_crop_area_changed(self):
        self.image_processor.set_active_crop_area(self.frame.get_active_crop_area())
