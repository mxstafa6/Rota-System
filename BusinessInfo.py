import tkinter
import sqlite3
from tkinter import ttk
from tkinter import messagebox

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

class EnterWorkData:
    def __init__(self, window):
        # Initialize the EnterWorkData class with a Tkinter window
        self.window = window
        self.window.title("Data Entry Form")
        # Create GUI widgets
        self.create_widgets()

    def create_widgets(self):
        # Create a frame to hold the widgets
        self.frame = tkinter.Frame(self.window)
        self.frame.pack()

        # Create a label frame for user information
        self.user_info_frame = tkinter.LabelFrame(self.frame, text="Business Information")
        self.user_info_frame.grid(row=0, column=0, padx=20, pady=10)

        # Create input widgets
        self.create_input_widgets()

        # Create the enter data button
        #self.create_button()

    #Handle the toggling of the days
    def toggle_day(self, day, var, selected_days):
        if var.get():
            selected_days.append(day)
        else:
            selected_days.remove(day)

    def create_input_widgets(self):
        # Labels and entry widgets for user information
        labels = ["Days Open"]

        # Loop through labels and create corresponding entry widgets
        for label_text in labels:
            label = tkinter.Label(self.user_info_frame, text=label_text)
            label.grid(row=0, column=0, sticky="n", padx=10, pady=5)

            # Determine type of entry widget based on label
            if label_text == "Days Open":
                selected_days = []

                # Create Checkbuttons for each day
                for day in days:
                    var = tkinter.BooleanVar()
                    checkbox = ttk.Checkbutton(self.user_info_frame, text=day, variable=var)
                    checkbox.grid(sticky="w")
                    
                    # Lambda function with default argument to capture the current value of 'day'
                    checkbox.config(command=lambda d=day, v=var: self.toggle_day(d, v, selected_days))

                # Button to print selected days and destroy the label
                ok_button = ttk.Button(self.user_info_frame, text="Ok", command=lambda: self.show_hours_window(selected_days))
                ok_button.grid(row=len(days) + 1, column=0, pady=(5, 0), sticky="w")

        entry = tkinter.Entry(self.user_info_frame)

    def show_hours_window(self, selected_days):
        # Create a new window for entering hours
        hours_window = tkinter.Toplevel()
        hours_window.title("Enter Hours")
        
        # Create labels and entry boxes for each selected day
        for i, day in enumerate(days):
            if day in selected_days:
                tkinter.Label(hours_window, text=day).grid(row=i, column=0, sticky="e")
                entry = tkinter.Entry(hours_window)
                entry.grid(row=i, column=1)







    # Store entry widget in the dictionary

    #def create_button(self):
        # Create button to enter data
        #self.button = tkinter.Button(self.frame, text="Enter data", command=self.enter_data)
        #self.button.grid(row=1, column=0, sticky="news", padx=20, pady=10)

window = tkinter.Tk()
app = EnterWorkData(window)
window.mainloop()