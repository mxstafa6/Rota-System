import tkinter
import sqlite3
from tkinter import ttk, messagebox

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

class EnterWorkData:
    daysHours={}
    def __init__(self, window):
        # Initialize the EnterWorkData class with a Tkinter window
        self.window = window
        self.window.title("Business Information")

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

    #Handle the toggling of the days
    def toggle_day(self, day, var, selected_days):
        if var.get():
            selected_days.append(day)
        else:
            selected_days.remove(day)

    def create_input_widgets(self):
        # Labels and entry widgets for user information
        labels = ["Days Open", "Weekly Budget"]

        # Loop through labels and create corresponding entry widgets
        for i, label_text in enumerate(labels):
            label = tkinter.Label(self.user_info_frame, text=label_text)
            label.grid(row=0, column=i, sticky="n", padx=10, pady=5)

            # Determine type of entry widget based on label
            if label_text == "Weekly Budget":
                budget_entry = tkinter.Entry(self.user_info_frame)
                budget_entry.grid(row=i, column=i, padx=30, pady=5)
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
                try:
                    budget=float(budget_entry.get())
                    ok_button = ttk.Button(self.user_info_frame, text="Ok", command=lambda: self.show_hours_window(selected_days))
                    ok_button.grid(row=len(days) + 1, column=0, pady=(5, 0), sticky="w") 
                except ValueError:
                    messagebox.showerror("Error", "Weekly budget must be a valid number")

    def show_hours_window(self, selected_days):
        # Create a new window for entering hours
        hours_window = tkinter.Toplevel()
        hours_window.title("Business Information")
        
        # Dictionary to store day and its opening hour
        opening_hours = {}

        # Create labels and entry boxes for each selected day
        row_counter = 0
        for day in days:
            if day in selected_days:
                tkinter.Label(hours_window, text=day).grid(row=row_counter, column=0, sticky="e")
                hoursEntry = ttk.Spinbox(hours_window, from_=0, to=23, width=2, state="readonly")
                hoursEntry.grid(row=row_counter, column=1)
                minutesEntry = ttk.Combobox(hours_window, values=["00", "15", "30", "45"], width=3)
                minutesEntry.grid(row=row_counter, column=2)
                minutesEntry.current(0)
                row_counter += 1

                # Define a function to store the opening hour when entry is made
                def store_opening_hour(event=None, day=day, hoursEntry=hoursEntry, minutesEntry=minutesEntry):
                    if event and str(event.type) == "VirtualEvent":
                        return  # Ignore VirtualEvent
                    opening_hour = f"{hoursEntry.get()}:{minutesEntry.get()}"
                    opening_hours[day] = opening_hour

                # Bind the function to the Spinbox entries
                hoursEntry.config(command=store_opening_hour)
                minutesEntry.bind("<<ComboboxSelected>>", store_opening_hour)

        # Function to print the dictionary
        def print_opening_hours():
            print(opening_hours)

        # Button to print the dictionary
        ok_button = ttk.Button(hours_window, text="Ok", command=print_opening_hours)
        ok_button.grid(row=row_counter, column=0, columnspan=3, pady=(5, 10), sticky="we")

window = tkinter.Tk()
app = EnterWorkData(window)
window.mainloop()