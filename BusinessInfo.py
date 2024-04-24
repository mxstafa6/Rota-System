import tkinter
import sqlite3
from tkinter import ttk, messagebox

# Define the days of the week
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

class EnterWorkData:
    def __init__(self, window):
        # Initialize the main window
        self.window = window
        self.window.title("Business Information")
        self.create_widgets()

    def create_widgets(self):
        # Create the main frame
        self.frame = tkinter.Frame(self.window)
        self.frame.pack()

        # Create a label frame for user information
        self.user_info_frame = tkinter.LabelFrame(self.frame, text="Business Information")
        self.user_info_frame.grid(row=0, column=0, padx=20, pady=10)

        # Create input widgets
        self.create_input_widgets()

    def toggle_day(self, day, var, selected_days):
        # Toggle the selection of the days
        if var.get():
            selected_days.append(day)
        else:
            selected_days.remove(day)

    def create_input_widgets(self):
        # Create labels and entry widgets for user information
        labels = ["Days Open", "Weekly Budget", "Restaurant Name"]
        for i, label_text in enumerate(labels):
            label = tkinter.Label(self.user_info_frame, text=label_text)
            label.grid(row=0, column=i, sticky="n", padx=10, pady=5)

            # Determine type of entry widget based on label
            if label_text == "Restaurant Name":
                self.restaurantName_entry = tkinter.Entry(self.user_info_frame)
                self.restaurantName_entry.grid(row=1, column=i, padx=30, pady=5)
            elif label_text == "Weekly Budget":
                self.budget_entry = tkinter.Entry(self.user_info_frame)
                self.budget_entry.grid(row=1, column=i, padx=30, pady=5)
            elif label_text == "Days Open":
                self.selected_days = []

                # Create Checkbuttons for each day
                for j, day in enumerate(days):
                    var = tkinter.BooleanVar()
                    checkbox = ttk.Checkbutton(self.user_info_frame, text=day, variable=var)
                    checkbox.grid(sticky="w")
                    # Lambda function with default argument to capture the current value of 'day'
                    checkbox.config(command=lambda d=day, v=var: self.toggle_day(d, v, self.selected_days))

                # Button to validate and proceed
                ok_button = ttk.Button(self.user_info_frame, text="Ok", command=self.validate)
                ok_button.grid(row=len(days) + 1, column=0, pady=(5, 0), sticky="w") 
    
    def validate(self):
        # Validate user input
        restaurant_name = self.restaurantName_entry.get()  # Store the restaurant name as a string
        try:
            self.budget = float(self.budget_entry.get())  # Convert budget to float
            try:
                conn = sqlite3.connect('data.db')  # Connect to the SQLite database
                cursor = conn.cursor()

                # Check if the restaurant name already exists in the database
                cursor.execute("SELECT restaurantName FROM restaurant_data WHERE restaurantName=?", (restaurant_name,))
                existing_name = cursor.fetchone()
                conn.close()

                # If restaurant name doesn't exist, proceed to enter opening hours
                if existing_name is None:
                    self.show_hours_window()
                else:
                    messagebox.showerror('Error', 'Restaurant Name already exists.')
            except Exception as e:
                print(e)
                self.show_hours_window()  # Show hours window if any exception occurs
        except ValueError:
            messagebox.showerror("Error", "Weekly budget must be a valid number.")
    
    def enter_roles(self):
        self.roles = []
        roles_window = tkinter.Toplevel()
        roles_window.title("Business Information")

        role_entry = tkinter.Entry(roles_window)
        role_entry.grid(row=0, column=0, padx=30, pady=5)

        # Define a function to add the role to the roles list
        def add_role():
            role = role_entry.get()
            if role:
                self.roles.append(role)
                role_entry.delete(0, tkinter.END)  # Clear the entry after adding the role

        # Create a button to add the role
        add_button = ttk.Button(roles_window, text="Add Role", command=add_role)
        add_button.grid(row=1, column=0, padx=30, pady=5)

    def show_hours_window(self):
        # Show the window to enter opening and closing hours
        hours_window = tkinter.Toplevel()
        hours_window.title("Business Information")
        
        # Initialize dictionaries to store opening and closing hours
        self.opening_hours = {day: "OFF" for day in days}
        self.closing_hours = {day: "OFF" for day in days}

        # Create labels for opening and closing times
        opening_label = tkinter.Label(hours_window, text="Opening Time")
        opening_label.grid(row=0, column=1, padx=5)
        closing_label = tkinter.Label(hours_window, text="Closing Time")
        closing_label.grid(row=0, column=2, padx=5)

        row_counter = 1
        for day in self.selected_days:
            # Create labels and entry widgets for each selected day
            tkinter.Label(hours_window, text=day).grid(row=row_counter, column=0, sticky="e")
            
            # Entry widget for opening time
            opening_hours_entry = ttk.Frame(hours_window)
            opening_hours_entry.grid(row=row_counter, column=1, padx=5)
            opening_hours_spinbox = ttk.Spinbox(opening_hours_entry, from_=0, to=23, width=2, state="readonly")
            opening_hours_spinbox.grid(row=0, column=0)
            opening_hours_spinbox_minutes = ttk.Combobox(opening_hours_entry, values=["00", "15", "30", "45"], width=3)
            opening_hours_spinbox_minutes.grid(row=0, column=1)
            opening_hours_spinbox_minutes.current(0)

            # Entry widget for closing time
            closing_hours_entry = ttk.Frame(hours_window)
            closing_hours_entry.grid(row=row_counter, column=2, padx=5)
            closing_hours_spinbox = ttk.Spinbox(closing_hours_entry, from_=0, to=23, width=2, state="readonly")
            closing_hours_spinbox.grid(row=0, column=0)
            closing_hours_spinbox_minutes = ttk.Combobox(closing_hours_entry, values=["00", "15", "30", "45"], width=3)
            closing_hours_spinbox_minutes.grid(row=0, column=1)
            closing_hours_spinbox_minutes.current(0)

            row_counter += 1

            # Function to store opening and closing hours
            def store_hours(event=None, day=day, opening_spinbox=opening_hours_spinbox, opening_minutes=opening_hours_spinbox_minutes, closing_spinbox=closing_hours_spinbox, closing_minutes=closing_hours_spinbox_minutes):
                if event and str(event.type) == "VirtualEvent":
                    return
                
                # Format opening and closing hours
                opening_hour = f"{opening_spinbox.get()}:{opening_minutes.get()}"
                closing_hour = f"{closing_spinbox.get()}:{closing_minutes.get()}"
                    
                self.opening_hours[day] = opening_hour
                self.closing_hours[day] = closing_hour

                # Print the opening and closing hours for debugging
                print("Opening Hours:", self.opening_hours)
                print("Closing Hours:", self.closing_hours)

            # Bind the function to the Spinbox and Combobox entries
            opening_hours_spinbox.config(command=store_hours)
            opening_hours_spinbox_minutes.bind("<<ComboboxSelected>>", store_hours)
            closing_hours_spinbox.config(command=store_hours)
            closing_hours_spinbox_minutes.bind("<<ComboboxSelected>>", store_hours)

        # Button to proceed to enter restaurant data
        ok_button = ttk.Button(hours_window, text="Ok", command=self.enter_roles)
        ok_button.grid(row=row_counter, column=0, columnspan=3, pady=(5, 10), sticky="we")
    
    def enter_restaurantdata(self):
        # Connect to the SQLite database
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()

        # Create a table to store restaurant data if it doesn't exist already
        cursor.execute('''CREATE TABLE IF NOT EXISTS restaurant_data
                        (restaurantName TEXT, restaurantBudget FLOAT)''')

        # Insert restaurant name and budget into the restaurant_data table
        cursor.execute('''INSERT INTO restaurant_data (restaurantName, restaurantBudget) 
                        VALUES (?, ?)''', (self.restaurantName_entry.get(), self.budget))

        # Create a new table to store opening and closing times for each day
        cursor.execute('''CREATE TABLE IF NOT EXISTS days_data
                        (restaurantName TEXT, 
                        Monday TEXT, 
                        Tuesday TEXT, 
                        Wednesday TEXT, 
                        Thursday TEXT, 
                        Friday TEXT, 
                        Saturday TEXT, 
                        Sunday TEXT)''')

        # Insert opening and closing times for each day into the days_data table
        cursor.execute('''INSERT INTO days_data (restaurantName, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                        (self.restaurantName_entry.get(), 
                        f"{self.opening_hours.get('Monday', 'OFF')}-{self.closing_hours.get('Monday', 'OFF')}", 
                        f"{self.opening_hours.get('Tuesday', 'OFF')}-{self.closing_hours.get('Tuesday', 'OFF')}", 
                        f"{self.opening_hours.get('Wednesday', 'OFF')}-{self.closing_hours.get('Wednesday', 'OFF')}", 
                        f"{self.opening_hours.get('Thursday', 'OFF')}-{self.closing_hours.get('Thursday', 'OFF')}", 
                        f"{self.opening_hours.get('Friday', 'OFF')}-{self.closing_hours.get('Friday', 'OFF')}", 
                        f"{self.opening_hours.get('Saturday', 'OFF')}-{self.closing_hours.get('Saturday', 'OFF')}", 
                        f"{self.opening_hours.get('Sunday', 'OFF')}-{self.closing_hours.get('Sunday', 'OFF')}"))

        # Commit changes and close connection
        conn.commit()
        conn.close()

# Main code
if __name__ == "__main__":
    window = tkinter.Tk()
    app = EnterWorkData(window)
    window.mainloop()
