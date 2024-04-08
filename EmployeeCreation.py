import tkinter
import sqlite3
import random
from tkinter import ttk
from tkinter import messagebox
from Encryption import encrypt, decrypt

employees={}
roles=["Waiter", "Runner", "Manager", "Floor Manager", "Bartender", "Barback", "Bar Manager"]

class EnterEmployees:
    def __init__(self, window):
        # Initialize the EnterEmployees class with a Tkinter window
        self.window = window
        self.window.title("Data Entry Form")

        # Create a frame to hold the widgets
        self.frame = tkinter.Frame(window)
        self.frame.pack()

        # Create a label frame for user information
        self.user_info_frame =tkinter.LabelFrame(self.frame, text="User Information")
        self.user_info_frame.grid(row=0, column=0, padx=20, pady=10)

        # Create labels and entry widgets for first name, last name and key
        self.first_name_label = tkinter.Label(self.user_info_frame, text="First Name")
        self.first_name_label.grid(row=0, column=0)
        self.first_name_entry = tkinter.Entry(self.user_info_frame)
        self.first_name_entry.grid(row=1, column=0)

        self.last_name_label = tkinter.Label(self.user_info_frame, text="Last Name")
        self.last_name_label.grid(row=0, column=1)
        self.last_name_entry = tkinter.Entry(self.user_info_frame)
        self.last_name_entry.grid(row=1, column=1)

        self.key = tkinter.Label(self.user_info_frame, text="User Key")
        self.key.grid(row=0, column=2)
        self.key_entry = tkinter.Entry(self.user_info_frame)
        self.key_entry.grid(row=1, column=2)

        # Create labels and combobox for gender, age, and role
        self.gender_label = tkinter.Label(self.user_info_frame, text="Gender")
        self.gender_combobox = ttk.Combobox(self.user_info_frame, values=["Male", "Female", "Other"])
        self.gender_label.grid(row=2, column=2)
        self.gender_combobox.grid(row=3, column=2)

        self.age_label = tkinter.Label(self.user_info_frame, text="Age")
        self.age_spinbox = tkinter.Spinbox(self.user_info_frame, from_=16, to=110)
        self.age_label.grid(row=2, column=0)
        self.age_spinbox.grid(row=3, column=0)

        self.role_label = tkinter.Label(self.user_info_frame, text="Role")
        self.role_combobox = ttk.Combobox(self.user_info_frame, values=roles)
        self.role_label.grid(row=2, column=1)
        self.role_combobox.grid(row=3, column=1)

        # Set padding for widgets in the label frame
        for widget in self.user_info_frame.winfo_children():
            widget.grid_configure(padx=10, pady=5)

        # Create a button to enter data, linked to the enter_data method
        self.button = tkinter.Button(self.frame, text="Enter data", command=self.enter_data)
        self.button.grid(row=3, column=0, sticky="news", padx=20, pady=10)

    def enter_data(self):
        # Creating Table in SQLite database if not exists
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        table_create_query = '''CREATE TABLE IF NOT EXISTS Employee_Data 
                (key TEXT, firstname TEXT, lastname TEXT, gender TEXT, age INT, role TEXT)
        '''
        conn.execute(table_create_query)

        # Getting the inputs from data boxes
        firstname = self.first_name_entry.get()
        lastname = self.last_name_entry.get()
        gender = self.gender_combobox.get()
        age = self.age_spinbox.get()
        role = self.role_combobox.get()
        key = '{:04d}'.format(int(self.key_entry.get()))
        
        # Checking there is an input for every box
        if firstname and lastname and gender and age and role and key:
            checkKey=[]
            cursor.execute("SELECT key FROM Employee_Data")
            keys = cursor.fetchall()
            for DBkeys in keys:
                checkKey.append(decrypt(DBkeys[0]))
            if key not in checkKey:
                # Inserting data into SQLite database
                data_insert_query = '''INSERT INTO Employee_Data (key, firstname, lastname, gender, 
                age, role) VALUES 
                (?, ?, ?, ?, ?, ?)'''
                data_insert_tuple = (encrypt(key), firstname, lastname, gender, age, role)
                cursor.execute(data_insert_query, data_insert_tuple)
                conn.commit()
                conn.close()
                print(checkKey)

                # Resetting the entry Boxes
                self.first_name_entry.delete(0, 'end')
                self.last_name_entry.delete(0, 'end')
                self.key_entry.delete(0, 'end')
                self.gender_combobox.set('')
                self.age_spinbox.delete(0, 'end')
                self.role_combobox.set('')
            else:
                messagebox.showerror('Python Error', 'Error: This key is already in use.')
        else:
            messagebox.showerror('Python Error', 'Error: You have to input all fields.')

# Initialize the tkinter window and create an instance of EnterEmployees
window = tkinter.Tk()
app = EnterEmployees(window)
window.mainloop()