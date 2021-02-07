from gui_imagewindow import ImageWindow
from image_processor import ImageProcessor
from custom_widgets import ToggleButton
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog
import json
import math
import os.path


class MainWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.title("HEXI")

        self.image_windows = {}
        self.active_image_window = None

        self.auto_evaluate = False

        # Load available algorithms:
        self.available_classifiers = ImageProcessor.get_available_classifiers()
        self.available_detectors = ImageProcessor.get_available_detectors()

        # Timer job for triggering auto evaluation:
        self.parameter_changed_job = None

        # Create GUI:
        input_frame = tk.Frame(self)

        classifier_label = tk.Label(input_frame, text='Classifier:')
        self.classifier_entry = ttk.Combobox(
            input_frame,
            width=20,
            values=[classifier.get_name() for classifier in self.available_classifiers])
        self.classifier_entry.current(0)
        self.classifier_entry.bind("<<ComboboxSelected>>", self.on_algorithm_changed)

        detector_label = tk.Label(input_frame, text='Circle detector:')
        self.detector_entry = ttk.Combobox(input_frame, width=20, values=[
            detector.get_name() for detector in self.available_detectors])
        self.detector_entry.current(0)
        self.detector_entry.bind("<<ComboboxSelected>>", self.on_algorithm_changed)

        detector_label.grid(row=0, sticky=tk.W)
        self.detector_entry.grid(row=0, column=1, sticky=tk.W)

        classifier_label.grid(row=1, sticky=tk.W)
        self.classifier_entry.grid(row=1, column=1, sticky=tk.W)

        input_frame.grid(row=0, column=0, sticky=tk.W)

        self.parameters_frame = tk.Frame(self)
        self.parameters_frame.grid(row=3, sticky=tk.W)

        button_frame = tk.Frame(self)
        button_frame.grid(row=4, sticky=tk.W)

        open_button = tk.Button(button_frame, text="Open image", width=12, command=self.open_file)
        process_button = tk.Button(button_frame, text='Evaluate image', width=12, command=self.evaluate)
        auto_eval_button = ToggleButton(
            button_frame,
            text='Auto evaluation',
            width=12,
            default_state=False,
            command=self.toggle_auto_eval)
        save_button = tk.Button(button_frame, text="Save parameters", width=12, command=self.save_parameters)
        load_button = tk.Button(button_frame, text="Load parameters", width=12, command=self.load_parameters)

        open_button.grid(row=0, column=0, pady=2, padx=2, sticky=tk.W)
        process_button.grid(row=0, column=1, pady=2, padx=2, sticky=tk.W)
        auto_eval_button.grid(row=0, column=2, pady=2, padx=2, sticky=tk.W)
        save_button.grid(row=0, column=3, pady=2, padx=2, sticky=tk.W)
        load_button.grid(row=0, column=4, pady=2, padx=2, sticky=tk.W)

        self.parameter_widgets = {}
        self.update_parameters_gui()

    def on_image_window_focus(self, event):
        self.active_image_window = event.widget

    def open_file(self):
        file_path = tk.filedialog.askopenfilename()

        if file_path:
            image_window = self.create_image_window(file_path)
            self.image_windows[file_path] = image_window
            self.active_image_window = image_window

    def get_active_detector(self):
        return self.available_detectors[self.detector_entry.current()]

    def get_active_classifier(self):
        return self.available_classifiers[self.classifier_entry.current()]

    def parameter_value_changed(self, event):
        if self.auto_evaluate:
            if self.parameter_changed_job:
                self.after_cancel(self.parameter_changed_job)
            self.parameter_changed_job = self.after(500, self.trigger_auto_evaluate)

    def trigger_auto_evaluate(self):
        self.parameter_changed_job = None
        self.evaluate()

    def update_parameters_gui(self):
        # Get old parameter values:
        old_parameter_values = self.get_parameter_values()

        # Destroy old widgets:
        for widget in self.parameters_frame.winfo_children():
            widget.destroy()

        self.parameter_widgets.clear()

        # Get active parameter list:
        parameters = self.get_active_detector().get_parameter_list()
        parameters2 = self.get_active_classifier().get_parameter_list()

        for parameter in parameters2:
            if parameter not in parameters:
                parameters.append(parameter)

        # Create new widgets:
        for index, parameter in enumerate(parameters):
            parameter_id = parameter[0]
            range_start = parameter[1]
            range_end = parameter[2]
            range_size = range_end - range_start
            default_parameter_value = parameter[3]

            parameter_label = tk.Label(self.parameters_frame, text=parameter_id)

            parameter_scale = tk.Scale(self.parameters_frame,
                                       from_=range_start,
                                       to=range_end,
                                       tickinterval=float(range_size)/10.0,
                                       orient=tk.HORIZONTAL,
                                       length=math.log(range_size, 1.5) * 30,
                                       command=self.parameter_value_changed)

            # Set previous value if a parameter with the same id existed before, else set the default value:
            parameter_scale.set(
                default_parameter_value if parameter_id not in old_parameter_values else old_parameter_values[parameter_id])

            parameter_label.grid(row=index, sticky=tk.W)
            parameter_scale.grid(row=index, column=1, sticky=tk.W)
            self.parameter_widgets[parameter[0]] = parameter_scale

    def on_algorithm_changed(self, event):
        self.update_parameters_gui()

    def evaluate(self):
        if self.active_image_window:
            parameter_values = self.get_parameter_values()
            self.active_image_window.evaluate(self.get_active_detector(), self.get_active_classifier(), parameter_values)

    def get_parameter_values(self):
        parameter_values = {}
        for key, widget in self.parameter_widgets.items():
            parameter_values[key] = widget.get()
        return parameter_values

    def toggle_auto_eval(self, button, is_pressed):
        self.auto_evaluate = is_pressed
        if self.auto_evaluate:
            self.evaluate()

    def create_image_window(self, image_path):
        image_window = ImageWindow(image_path, image_path)
        image_window.geometry('+%d+%d' % (self.winfo_x() + self.winfo_width() + 10, self.winfo_y()))
        image_window.bind("<FocusIn>", self.on_image_window_focus)
        return image_window

    def get_parameter_file_name(self):
        if self.active_image_window:
            filename = self.active_image_window.title()
            filename = os.path.splitext(filename)[0]
            filename += '.par'
            return filename
        else:
            return ''

    def save_parameters(self):
        filename = self.get_parameter_file_name()
        if filename != '':
            with open(filename, 'w') as outfile:
                parameter_values = self.get_parameter_values()
                data = {
                    'detector': self.get_active_detector().get_name(),
                    'classifier': self.get_active_classifier().get_name(),
                    'parameters': parameter_values
                }
                json.dump(data, outfile, indent=4)

    def load_parameters(self):
        filename = self.get_parameter_file_name()
        if filename != '' and os.path.exists(filename):
            with open(filename, 'r') as infile:
                data = json.load(infile)

                if 'detector' in data:
                    detector_name = data['detector']
                    detector_entry_values = self.detector_entry["values"]
                    if detector_name in detector_entry_values:
                        detector_index = detector_entry_values.index(detector_name)
                        self.detector_entry.current(detector_index)

                if 'classifier' in data:
                    classifier_name = data['classifier']
                    classifier_entry_values = self.classifier_entry["values"]
                    if classifier_name in classifier_entry_values:
                        classifier_index = classifier_entry_values.index(classifier_name)
                        self.classifier_entry.current(classifier_index)

                self.update_parameters_gui()

                parameter_values = data['parameters']

                for key, widget in self.parameter_widgets.items():
                    if key in parameter_values:
                        widget.set(parameter_values[key])
