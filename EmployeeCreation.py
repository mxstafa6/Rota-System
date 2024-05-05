import tkinter
import sqlite3
from tkinter import ttk, messagebox
from Encryption import encrypt  # Importing encryption function from a custom module

class EnterEmployees:
    def __init__(self, window):
        self.window = window
        self.window.title("Employee Creation")
        self.create_widgets()

    def create_widgets(self):
        # Create a frame to contain all widgets
        self.frame = tkinter.Frame(self.window)
        self.frame.pack()

        # Create a labeled frame for user information
        self.user_info_frame = tkinter.LabelFrame(self.frame, text="User Information")
        self.user_info_frame.grid(row=0, column=0, padx=20, pady=10)

        # Call methods to create input widgets and button
        self.create_input_widgets()
        self.create_button()

    def create_input_widgets(self):
        # Method to create input widgets for employee information
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT restaurantName FROM restaurant_data")
        restaurants = [x[0] for x in cursor.fetchall()]  # Fetch restaurant names from database
        conn.close()

        labels = ["First Name", "Last Name", "User Key", "Gender", "Age", "Hourly Pay", "Restaurant", "Role"]
        self.entries = {}

        for i, label_text in enumerate(labels):
            label = tkinter.Label(self.user_info_frame, text=label_text)
            label.grid(row=i, column=0, sticky="w", padx=10, pady=5)

            # Depending on the label, create different types of input widgets
            if label_text == "Restaurant":
                entry = ttk.Combobox(self.user_info_frame, values=restaurants, state="readonly")
            elif label_text == "Gender":
                entry = ttk.Combobox(self.user_info_frame, values=["Male", "Female", "Other"], state="readonly")
            elif label_text == "Age":
                entry = tkinter.Spinbox(self.user_info_frame, from_=16, to=110, state="readonly")
            elif label_text == "Role":
                entry = ttk.Combobox(self.user_info_frame, state="readonly")
                entry['values'] = ['Manager', 'Waiter', 'Runner', 'Bartender', 'Barback']
            else:
                entry = tkinter.Entry(self.user_info_frame)

            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries[label_text] = entry  # Store input widgets in a dictionary

    def check(self):
        # Method to validate input data before entering it into the database
        self.data = {key: entry.get() for key, entry in self.entries.items()}

        if all(self.data.values()):  # Check if all fields are filled
            if self.data["User Key"].isdigit() and len(self.data["User Key"]) == 4:  # Check if user key is a 4-digit number
                self.key = '{:04d}'.format(int(self.data["User Key"]))  # Format key as 4 digits
                self.hourly_pay = self.data["Hourly Pay"]

                try:
                    self.hourly_pay = float(self.hourly_pay)  # Convert hourly pay to float
                except ValueError:
                    messagebox.showerror('Error', 'Hourly Pay must be a valid number.')  # Show error if hourly pay is not a number
                    return

                if not self.check_key_availability(self.key):  # Check if key is available
                    self.enter_data()  # Enter employee data into the database
                else:
                    messagebox.showerror('Error', 'This key is already in use.')  # Show error if key is already in use
            else:
                messagebox.showerror('Error', 'User Key must be a 4-digit number.')  # Show error if user key is not 4 digits
        else:
            messagebox.showerror('Error', 'You have to input all fields.')  # Show error if any field is empty

    def create_button(self):
        # Method to create a button for entering data
        self.button = tkinter.Button(self.frame, text="Enter Data", command=self.check)
        self.button.grid(row=1, column=0, sticky="news", padx=20, pady=10)

    def enter_data(self):
        # Method to enter employee data into the database
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO employee_data (key, firstname, lastname, gender, age, role, pay, restaurantName)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (encrypt(self.key), self.data["First Name"], self.data["Last Name"],
                                                             self.data["Gender"], self.data["Age"], self.data["Role"], round(self.hourly_pay, 2), self.data['Restaurant']))
        conn.commit()
        conn.close()

        self.window.destroy()  # Close the window after entering data
        self.window.quit()

    def check_key_availability(self, key):
        # Method to check if a key is already in use
        try:
            conn = sqlite3.connect('data.db')
            cursor = conn.cursor()
            cursor.execute("SELECT key FROM employee_data WHERE key=?", (encrypt(key),))
            existing_key = cursor.fetchone()
            conn.close()

            return existing_key is not None
        except:
            return None

def employee_main():
    # Main function to create and run the GUI for entering employee data
    window = tkinter.Tk()
    app = EnterEmployees(window)
    window.mainloop()
