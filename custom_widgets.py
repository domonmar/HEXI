import tkinter as tk


class ToggleButton(tk.Button):
    def __init__(self, parent, text, width, default_state, command):
        tk.Button.__init__(self,
                           parent,
                           text=text,
                           width=width,
                           relief="sunken" if default_state else "raised",
                           command=self.on_toggle)
        self.command = command

    def on_toggle(self):
        button_is_pressed = self.config('relief')[-1] == 'sunken'
        if button_is_pressed:
            self.config(relief="raised")
        else:
            self.config(relief="sunken")

        if self.command:
            self.command(self, not button_is_pressed)
