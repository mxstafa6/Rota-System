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

    def create_input_widgets(self):
        # Labels and entry widgets for user information
        labels = ["Days Open", "Hours On Open Days"]
        self.entries = {}  # Dictionary to hold the entry widgets
        
        # Loop through labels and create corresponding entry widgets
        for i, label_text in enumerate(labels):
            label = tkinter.Label(self.user_info_frame, text=label_text)
            label.grid(row=i, column=0, sticky="w", padx=10, pady=5)

            # Determine type of entry widget based on label
            if label_text == "Days Open":
                selected_days=[]
                for x in range(len(days)):
                    l = ttk.Checkbutton(window, text=days[x], variable=days[x],command=lambda x=days[x]:selected_days.append(x))
                    l.pack(anchor = 'w')
                ttk.Button(window,text="Ok",command=lambda: [print(selected_days),window.destroy()]).pack()
            entry = tkinter.Entry(self.user_info_frame)

            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries[label_text] = entry  # Store entry widget in the dictionary

    #def create_button(self):
        # Create button to enter data
        #self.button = tkinter.Button(self.frame, text="Enter data", command=self.enter_data)
        #self.button.grid(row=1, column=0, sticky="news", padx=20, pady=10)

window = tkinter.Tk()
app = EnterWorkData(window)
window.mainloop()