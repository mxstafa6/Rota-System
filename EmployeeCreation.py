import tkinter
import sqlite3
from tkinter import ttk
from tkinter import messagebox
from Encryption import encrypt

roles=["Waiter", "Runner", "Manager", "Floor Manager", "Bartender", "Barback", "Bar Manager"]

class EnterEmployees:
    def __init__(self, window):
        # Initialize the EnterEmployees class with a Tkinter window
        self.window = window
        self.window.title("Employee Creation")
        # Create GUI widgets
        self.create_widgets()

    def create_widgets(self):
        # Create a frame to hold the widgets
        self.frame = tkinter.Frame(self.window)
        self.frame.pack()

        # Create a label frame for user information
        self.user_info_frame = tkinter.LabelFrame(self.frame, text="User Information")
        self.user_info_frame.grid(row=0, column=0, padx=20, pady=10)

        # Create input widgets
        self.create_input_widgets()

        # Create the enter data button
        self.create_button()

    def create_input_widgets(self):
        # Get list of restaurants
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT restaurantName FROM restaurant_data")
        restaurants = [x[0] for x in cursor.fetchall()] # Extract the first element of each tuple
        conn.close()

        # Labels and entry widgets for user information
        labels = ["First Name", "Last Name", "User Key", "Gender", "Age", "Role", "Hourly Pay", "Ability Level", "Restaurant"]
        self.entries = {}  # Dictionary to hold the entry widgets
        
        # Loop through labels and create corresponding entry widgets
        for i, label_text in enumerate(labels):
            label = tkinter.Label(self.user_info_frame, text=label_text)
            label.grid(row=i, column=0, sticky="w", padx=10, pady=5)

            # Determine type of entry widget based on label
            if label_text == "Restaurant":
                entry = ttk.Combobox(self.user_info_frame, values=restaurants, state="readonly")
            elif label_text == "Gender":
                entry = ttk.Combobox(self.user_info_frame, values=["Male", "Female", "Other"],state="readonly")
            elif label_text == "Age":
                entry = tkinter.Spinbox(self.user_info_frame, from_=16, to=110,state="readonly")
            elif label_text == "Role":
                entry = ttk.Combobox(self.user_info_frame, values=roles,state="readonly")
            elif label_text == "Ability Level":
                entry = tkinter.Spinbox(self.user_info_frame, from_=1, to=3,state="readonly")
            else:
                entry = tkinter.Entry(self.user_info_frame)

            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries[label_text] = entry  # Store entry widget in the dictionary

    def create_button(self):
        # Create button to enter data
        self.button = tkinter.Button(self.frame, text="Enter data", command=self.enter_data)
        self.button.grid(row=1, column=0, sticky="news", padx=20, pady=10)

    def enter_data(self):
        # Get data from entry widgets
        data = {key: entry.get() for key, entry in self.entries.items()}
        
        # Check if all fields are filled
        if all(data.values()):
            # Check if User Key is a 4-digit number
            if data["User Key"].isdigit() and len(data["User Key"]) == 4:
                key = '{:04d}'.format(int(data["User Key"]))

                # Check if Hourly Pay can be converted to a float
                try:
                    hourly_pay = float(data['Hourly Pay'])
                except ValueError:
                    messagebox.showerror('Error', 'Hourly Pay must be a valid number.')
                    return

                # Check if the key is available
                if not self.check_key_availability(key):
                    # Insert data into SQLite database
                    conn = sqlite3.connect('data.db')
                    cursor = conn.cursor()
                    cursor.execute('''CREATE TABLE IF NOT EXISTS Employee_Data 
                                    (key TEXT, firstname TEXT, lastname TEXT, gender TEXT, age INT, role TEXT, pay FLOAT, ability INT, restaurantName TEXT)''')

                    cursor.execute('''INSERT INTO Employee_Data (key, firstname, lastname, gender, age, role, pay, ability, restaurantName) 
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (encrypt(key), data["First Name"], data["Last Name"],
                                                                data["Gender"], data["Age"], data["Role"], round(hourly_pay, 2), data['Ability Level'], data['Restaurant']))
                    conn.commit()
                    conn.close()

                    # Clear entry fields after successful entry
                    self.clear_entry_fields()
                else:
                    # Show error message if key is already in use
                    messagebox.showerror('Error', 'This key is already in use.')
            else:
                # Show error message if User key is not a 4-digit number.
                messagebox.showerror('Error', 'User Key must be a 4-digit number.')
        else:
            # Show error message if not all fields are filled
            messagebox.showerror('Error', 'You have to input all fields.')

    def check_key_availability(self, key):
        # Check if the key is already in use
        try:
            conn = sqlite3.connect('data.db')
            cursor = conn.cursor()
            cursor.execute("SELECT key FROM Employee_Data WHERE key=?", (encrypt(key),))
            existing_key = cursor.fetchone()
            conn.close()

            return existing_key is not None
        except:
            return None


    def clear_entry_fields(self):
        # Clear all entry fields
        for entry in self.entries.values():
            entry.delete(0, 'end')

def main():
    # Create main window and run the application
    window = tkinter.Tk()
    app = EnterEmployees(window)
    window.mainloop()

if __name__ == "__main__":
    main()