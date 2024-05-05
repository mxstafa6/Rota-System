import tkinter
import sqlite3
from tkinter import ttk, messagebox

# Define the days of the week
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

class EnterWorkData:
    def __init__(self, window):
        self.window = window
        self.window.title("Business Information")
        self.create_widgets()

    def create_widgets(self):
        # Create a frame to contain all widgets
        self.frame = tkinter.Frame(self.window)
        self.frame.pack()

        # Create a labeled frame for user information
        self.user_info_frame = tkinter.LabelFrame(self.frame, text="Business Information")
        self.user_info_frame.grid(row=0, column=0, padx=20, pady=10)

        # Call method to create input widgets
        self.create_input_widgets()

    def toggle_day(self, day, var, selected_days):
        # Method to toggle selected days
        if var.get():
            selected_days.append(day)
        else:
            selected_days.remove(day)

    def create_input_widgets(self):
        # Method to create input widgets for restaurant information
        labels = ["Days Open", "Weekly Budget", "Restaurant Name"]
        for i, label_text in enumerate(labels):
            label = tkinter.Label(self.user_info_frame, text=label_text)
            label.grid(row=0, column=i, sticky="n", padx=10, pady=5)

            if label_text == "Restaurant Name":
                self.restaurantName_entry = tkinter.Entry(self.user_info_frame)
                self.restaurantName_entry.grid(row=1, column=i, padx=30, pady=5)
            elif label_text == "Weekly Budget":
                self.budget_entry = tkinter.Entry(self.user_info_frame)
                self.budget_entry.grid(row=1, column=i, padx=30, pady=5)
            elif label_text == "Days Open":
                # Create checkboxes for each day of the week
                self.selected_days = []

                for j, day in enumerate(DAYS):
                    var = tkinter.BooleanVar(value=False)
                    checkbox = ttk.Checkbutton(self.user_info_frame, text=day, variable=var)
                    checkbox.grid(sticky="w")
                    # Attach toggle_day method to each checkbox
                    checkbox.config(command=lambda d=day, v=var: self.toggle_day(d, v, self.selected_days))

                # Create OK button to proceed
                ok_button = ttk.Button(self.user_info_frame, text="Ok", command=self.validate)
                ok_button.grid(row=len(DAYS) + 1, column=0, columnspan=len(labels), pady=(5, 0), sticky="we")

    def validate(self):
        # Method to validate user input
        restaurant_name = self.restaurantName_entry.get().strip()
        if not restaurant_name:
            messagebox.showerror("Error", "Restaurant name cannot be empty.")
            return

        try:
            self.budget = float(self.budget_entry.get())
            try:
                # Connect to database and check if restaurant name already exists
                conn = sqlite3.connect('data.db')
                cursor = conn.cursor()

                cursor.execute("SELECT restaurantName FROM restaurant_data WHERE restaurantName=?", (restaurant_name,))
                existing_name = cursor.fetchone()
                conn.close()

                if existing_name is None:
                    self.show_hours_window()  # Proceed to enter opening/closing hours
                else:
                    messagebox.showerror('Error', 'Restaurant Name already exists.')
            except Exception as e:
                print(e)
                self.show_hours_window()  # Proceed to enter opening/closing hours if database operation fails
        except ValueError:
            messagebox.showerror("Error", "Weekly budget must be a valid number.")

    def show_hours_window(self):
        # Method to show window for entering opening/closing hours
        hours_window = tkinter.Toplevel()
        hours_window.title("Business Information")

        self.opening_hours = {day: "OFF" for day in DAYS}
        self.closing_hours = {day: "OFF" for day in DAYS}

        # Create labels and input fields for opening/closing hours for each selected day
        opening_label = tkinter.Label(hours_window, text="Opening Time")
        opening_label.grid(row=0, column=1, padx=5)
        closing_label = tkinter.Label(hours_window, text="Closing Time")
        closing_label.grid(row=0, column=2, padx=5)

        row_counter = 1
        for day in self.selected_days:
            tkinter.Label(hours_window, text=day).grid(row=row_counter, column=0, sticky="e")

            opening_hours_entry = ttk.Frame(hours_window)
            opening_hours_entry.grid(row=row_counter, column=1, padx=5)
            opening_hours_spinbox = ttk.Spinbox(opening_hours_entry, from_=0, to=23, width=2, state="readonly")
            opening_hours_spinbox.grid(row=0, column=0)
            opening_hours_spinbox_minutes = ttk.Combobox(opening_hours_entry, values=["00", "15", "30", "45"], width=3)
            opening_hours_spinbox_minutes.grid(row=0, column=1)
            opening_hours_spinbox_minutes.current(0)

            closing_hours_entry = ttk.Frame(hours_window)
            closing_hours_entry.grid(row=row_counter, column=2, padx=5)
            closing_hours_spinbox = ttk.Spinbox(closing_hours_entry, from_=0, to=23, width=2, state="readonly")
            closing_hours_spinbox.grid(row=0, column=0)
            closing_hours_spinbox_minutes = ttk.Combobox(closing_hours_entry, values=["00", "15", "30", "45"], width=3)
            closing_hours_spinbox_minutes.grid(row=0, column=1)
            closing_hours_spinbox_minutes.current(0)

            row_counter += 1

            def store_hours(event=None, day=day, opening_spinbox=opening_hours_spinbox,
                            opening_minutes=opening_hours_spinbox_minutes, closing_spinbox=closing_hours_spinbox,
                            closing_minutes=closing_hours_spinbox_minutes):
                # Method to store selected opening/closing hours
                if event and str(event.type) == "VirtualEvent":
                    return

                opening_hour = f"{opening_spinbox.get()}:{opening_minutes.get()}"
                closing_hour = f"{closing_spinbox.get()}:{closing_minutes.get()}"

                self.opening_hours[day] = opening_hour
                self.closing_hours[day] = closing_hour

            opening_hours_spinbox.config(command=store_hours)
            opening_hours_spinbox_minutes.bind("<<ComboboxSelected>>", store_hours)
            closing_hours_spinbox.config(command=store_hours)
            closing_hours_spinbox_minutes.bind("<<ComboboxSelected>>", store_hours)

        def check_times():
            # Method to check if opening time is before closing time for each selected day
            errors = []
            for day in self.selected_days:
                opening_hour = self.opening_hours[day]
                closing_hour = self.closing_hours[day]

                if opening_hour == "OFF" or closing_hour == "OFF":
                    errors.append(f"Please enter opening and closing times for {day}.")
                else:
                    opening_hour_parts = opening_hour.split(":")
                    opening_hour_int = int(opening_hour_parts[0])
                    opening_minutes_int = int(opening_hour_parts[1])

                    closing_hour_parts = closing_hour.split(":")
                    closing_hour_int = int(closing_hour_parts[0])
                    closing_minutes_int = int(closing_hour_parts[1])

                    if closing_hour_int < opening_hour_int or (closing_hour_int == opening_hour_int and closing_minutes_int <= opening_minutes_int):
                        errors.append(f"Opening time must be before closing time for {day}.")

            if errors:
                messagebox.showerror("Error", "\n".join(errors))
            else:
                self.enter_restaurantdata()  # Proceed to enter restaurant data if validation passes

        # Create OK button to validate opening/closing hours
        ok_button = ttk.Button(hours_window, text="Ok", command=check_times)
        ok_button.grid(row=row_counter, column=0, columnspan=3, pady=(5, 10), sticky="we")

    def enter_restaurantdata(self):
        # Method to store entered restaurant data in the database
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()

        cursor.execute(''' CREATE TABLE IF NOT EXISTS current_data
                           (restaurantName TEXT, currentRota BLOB, currentWages TEXT)''')
        cursor.execute('''INSERT INTO current_data (restaurantName) 
                        VALUES (?)''', (self.restaurantName_entry.get(),))
        cursor.execute('''CREATE TABLE IF NOT EXISTS restaurant_data
                        (restaurantName TEXT, restaurantBudget FLOAT)''')

        cursor.execute('''INSERT INTO restaurant_data (restaurantName, restaurantBudget) 
                        VALUES (?, ?)''', (self.restaurantName_entry.get(), self.budget))

        cursor.execute('''CREATE TABLE IF NOT EXISTS days_data
                        (restaurantName TEXT, 
                        Monday TEXT, 
                        Tuesday TEXT, 
                        Wednesday TEXT, 
                        Thursday TEXT, 
                        Friday TEXT, 
                        Saturday TEXT, 
                        Sunday TEXT)''')

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

        conn.commit()
        conn.close()

        self.window.destroy()
        self.window.quit()
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
        cursor.execute('''CREATE TABLE IF NOT EXISTS Employee_Data
                        (key TEXT, firstname TEXT, lastname TEXT, gender TEXT, age INT, role TEXT, pay FLOAT, restaurantName TEXT)''')

        cursor.execute('''INSERT INTO Employee_Data (key, firstname, lastname, gender, age, role, pay, restaurantName)
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
            cursor.execute("SELECT key FROM Employee_Data WHERE key=?", (encrypt(key),))
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
# Encryption parameters
multiplier = 7
adder = 13
modulus = 10

def encrypt(code):
    code = str(code)

    # Encrypt each digit using the parameters
    encrypted_code = ''
    for digit in code:
        encrypted_digit = (int(digit) * multiplier + adder) % modulus
        encrypted_code += str(encrypted_digit)
    
    return (encrypted_code)
def decrypt(code):
    code = str(code)

    # Decrypt each digit using the parameters
    decrypted_code = ''
    for digit in code:
        decrypted_digit = (int(digit) - adder) * pow(multiplier, -1, modulus) % modulus
        decrypted_code += str(decrypted_digit)
    
    return (decrypted_code)
import sqlite3
from tkinter import messagebox
import tkinter as tk
from datetime import datetime, timedelta
from TableDrawer import RotaApp
# RestaurantInformationRetriever retrieves and calculates shift information for a restaurant.
class RestaurantInformationRetriever:
    # Initialize with the restaurant's name and prepare the shifts dictionary.
    def __init__(self, restaurant_name):
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        self.restaurant_name = restaurant_name
        self.shifts = {day: None for day in self.days}
        self.check_off_days()
        self.get_shift()

    # Check the database for days the restaurant is closed and remove them from the days list.
    def check_off_days(self):
        with sqlite3.connect('data.db') as conn:
            cursor = conn.cursor()
            # Query to find off days for the restaurant.
            cursor.execute("SELECT * FROM days_data WHERE restaurantName = ? AND "
                           "(Monday = 'OFF-OFF' OR Tuesday = 'OFF-OFF' OR Wednesday = 'OFF-OFF' OR "
                           "Thursday = 'OFF-OFF' OR Friday = 'OFF-OFF' OR Saturday = 'OFF-OFF' OR Sunday = 'OFF-OFF')",
                           (self.restaurant_name,))
            # Remove off days from the days list.
            columns = [description[0] for description in cursor.description if description[0] != 'restaurantName']
            for column in columns:
                cursor.execute(f"SELECT {column} FROM days_data WHERE restaurantName = ? AND {column} = 'OFF-OFF'",
                               (self.restaurant_name,))
                if cursor.fetchone():
                    self.days.remove(column)

    # Retrieve shift times from the database and calculate the number and duration of shifts for each day.
    def get_shift(self):
        with sqlite3.connect('data.db') as conn:
            cursor = conn.cursor()
            for day in self.days:
                # Query to get shift times for the day.
                cursor.execute(f"SELECT {day} FROM days_data WHERE restaurantName = ?", (self.restaurant_name,))
                shift = cursor.fetchone()[0]
                # Calculate shift times and store them in the shifts dictionary.
                open_time, _, close_time = shift.partition('-')
                open_datetime = datetime.strptime(open_time.strip(), "%H:%M")
                close_datetime = datetime.strptime(close_time.strip(), "%H:%M")
                if close_datetime < open_datetime:
                    close_datetime += timedelta(days=1)
                time_difference_minutes = (close_datetime - open_datetime).total_seconds() // 60
                num_shifts = (time_difference_minutes + 359) // 360
                shift_duration = time_difference_minutes / num_shifts
                self.shifts[day] = [f"{(open_datetime + timedelta(minutes=shift_duration * i)):%H:%M}-"
                                    f"{(open_datetime + timedelta(minutes=shift_duration * (i + 1))):%H:%M}"
                                    for i in range(int(num_shifts))]

# Main function to create the application window and run the program.
def main(permissions, restaurant_name):
    if permissions < 1:
        messagebox.showerror("Permission Denied", "You need higher permissions to create a rota.")
        return
    app = RestaurantInformationRetriever(restaurant_name)
    root = tk.Tk()
    RotaApp(root, restaurant_name, app.shifts, app.days)
    root.mainloop()
import tkinter
import io
from PIL import Image, ImageTk
from tkinter import messagebox, ttk
import sqlite3
from Encryption import encrypt
from BusinessInfo import EnterWorkData
from Engine import main
from EmployeeCreation import employee_main

# Master key for the application (should be secured)
masterKey = 26012006

# LoginApp handles the login process and main window creation.
class LoginApp:
    def __init__(self, root):
        self.permissions = 0
        self.root = root
        self.root.title("Login")
        self.roles = ['Manager', 'Waiter', 'Runner', 'Bartender', 'Barback']
        self.setup_widgets()
        self.setup_db_connection()

    # Set up the login widgets.
    def setup_widgets(self):
        self.password_label = tkinter.Label(self.root, text="User Key:")
        self.password_label.grid(row=1, column=0, padx=10, pady=5)
        self.password_entry = tkinter.Entry(self.root, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)
        self.login_button = tkinter.Button(self.root, text="Login", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

    # Establish a connection to the SQLite database.
    def setup_db_connection(self):
        self.conn = sqlite3.connect("data.db")
        self.cur = self.conn.cursor()

    def login(self):
        user_key = self.password_entry.get()
        # Check if the entered key is the master key
        if user_key == str(masterKey):
            self.permissions = 2  # Grant highest permission level
            self.open_main_window(all_restaurants=True)  # Open the main window with access to all restaurants
            return

        if not user_key.isdigit() or len(user_key) != 4:
            messagebox.showerror("Error", "User key must be a 4-digit number")
            return

        self.user_key_encrypted = encrypt(user_key)
        self.cur.execute("SELECT role FROM Employee_data WHERE key = ?", (self.user_key_encrypted,))
        user_data = self.cur.fetchone()
        if user_data:
            messagebox.showinfo("Success", "Login successful!")
            if user_data[0] == 'Manager':
                self.permissions += 1
            self.open_main_window()
        else:
            messagebox.showerror("Error", "Invalid user key")

    # Open the main application window after successful login.
    def open_main_window(self, all_restaurants=False):
        self.main_window = tkinter.Tk()
        self.main_window.title("Main Menu")
        if all_restaurants:
            view_restaurants_button = tkinter.Button(self.main_window, text="View All Restaurants", command=self.view_all_restaurants)
            view_restaurants_button.pack(pady=10)
        else:
            view_restaurants_button = tkinter.Button(self.main_window, text="View Restaurants", command=self.view_restaurants)
            view_restaurants_button.pack(pady=10)
        create_restaurant_button = tkinter.Button(self.main_window, text="Create Restaurant", command=self.create_restaurant)
        create_restaurant_button.pack(pady=10)
        self.main_window.mainloop()  # Start the main loop for the main window

    def view_all_restaurants(self):
        # Create a new window to display all restaurant names and additional options
        all_view_window = tkinter.Toplevel()
        all_view_window.title("View All Restaurants")

        # Query the database to get all restaurant names
        self.cur.execute("SELECT restaurantName FROM restaurant_data")
        all_restaurant_data = self.cur.fetchall()

        # Create a dropdown menu to display all restaurant names
        all_selected_restaurant = tkinter.StringVar(all_view_window)
        all_selected_restaurant.set(all_restaurant_data[0][0] if all_restaurant_data else "No Restaurants")

        all_dropdown_menu = tkinter.OptionMenu(all_view_window, all_selected_restaurant, *[restaurant[0] for restaurant in all_restaurant_data])
        all_dropdown_menu.pack(padx=10, pady=10)

        # Create buttons for additional options, similar to view_restaurants
        edit_all_restaurant_button = tkinter.Button(all_view_window, text="Edit Restaurant Budget", command=lambda: self.edit_restaurant(all_selected_restaurant.get()))
        edit_all_restaurant_button.pack(pady=5)

        view_all_employees_button = tkinter.Button(all_view_window, text="View Employees", command=lambda: self.view_employees(all_selected_restaurant.get()))
        view_all_employees_button.pack(pady=5)

        view_all_rota_button = tkinter.Button(all_view_window, text="View Rota", command=lambda: self.view_rota(all_selected_restaurant.get()))
        view_all_rota_button.pack(pady=10)

        create_all_rota_button = tkinter.Button(all_view_window, text="Create Rota", command=lambda: main(self.permissions, all_selected_restaurant.get()))
        create_all_rota_button.pack(pady=10)

        delete_all_restaurant_button = tkinter.Button(all_view_window, text="Delete Restaurant", command=lambda: self.delete_restaurant_data(all_selected_restaurant.get()))
        delete_all_restaurant_button.pack(pady=5)

    def view_wages(self, restaurant_name):
        if self.permissions < 1:
            messagebox.showerror("Permission Denied", "You need higher permissions to view the wages.")
            return
        # Retrieve the text data for wages from the database
        self.cur.execute("SELECT currentWages FROM current_data WHERE restaurantName = ?", (restaurant_name,))
        wages_data = self.cur.fetchone()[0]

        # Display the wages information in a message box
        messagebox.showinfo("Wages Information", wages_data)
            
    def view_rota(self, restaurant_name):
        # Retrieve the BLOB data for the pastRota image from the database
        self.cur.execute("SELECT currentRota FROM current_data WHERE restaurantName = ?", (restaurant_name,))
        rota_blob = self.cur.fetchone()[0]

        # Convert the BLOB data to an image
        image_data = io.BytesIO(rota_blob)
        image = Image.open(image_data)

        # Create a new window to display the rota
        rota_window = tkinter.Toplevel()
        rota_window.title("View Rota")

        # Convert the image to a format Tkinter can use and display it
        photo_image = ImageTk.PhotoImage(image)
        image_label = ttk.Label(rota_window, image=photo_image)
        image_label.image = photo_image  # Keep a reference to avoid garbage collection
        image_label.pack()

        # Button to view wages
        view_wages_button = tkinter.Button(rota_window, text="View Wages", command=lambda: self.view_wages(restaurant_name))
        view_wages_button.pack(side=tkinter.BOTTOM, pady=10)

        # Show the window with the image
        rota_window.mainloop()

    def view_restaurants(self):
        # Create a new window to display restaurant names and additional options
        view_window = tkinter.Toplevel()
        view_window.title("View Restaurants")

        # Query the database to get restaurant names associated with the encrypted user key
        self.cur.execute("SELECT restaurantName FROM Employee_data WHERE key = ?", (self.user_key_encrypted,))
        restaurant_data = self.cur.fetchall()

        # Create a dropdown menu to display restaurant names
        selected_restaurant = tkinter.StringVar(view_window)
        selected_restaurant.set(restaurant_data[0] if restaurant_data else "No Restaurants")

        dropdown_menu = tkinter.OptionMenu(view_window, selected_restaurant, *restaurant_data)
        dropdown_menu.pack(padx=10, pady=10)

        # Create buttons for additional options
        edit_restaurant_button = tkinter.Button(view_window, text="Edit Restaurant Budget", command=lambda: self.edit_restaurant(selected_restaurant.get()[2:-3]))
        edit_restaurant_button.pack(pady=5)

        view_employees_button = tkinter.Button(view_window, text="View Employees", command=lambda: self.view_employees(selected_restaurant.get()[2:-3]))
        view_employees_button.pack(pady=5)

        view_rota_button = tkinter.Button(view_window, text="View Rota", command=lambda: self.view_rota(selected_restaurant.get()[2:-3]))
        view_rota_button.pack(pady=10)

        create_rota_button = tkinter.Button(view_window, text="Create Rota", command=lambda: main(self.permissions, selected_restaurant.get()[2:-3]))
        create_rota_button.pack(pady=10)

        delete_restaurant_button = tkinter.Button(view_window, text="Delete Restaurant", command=lambda: self.delete_restaurant_data(selected_restaurant.get()[2:-3]))
        delete_restaurant_button.pack(pady=5)
    
    # Define methods for the additional functionalities
    def view_employees(self, restaurant_name):
        if self.permissions < 1:
            messagebox.showerror("Permission Denied", "You need higher permissions to view employees.")
            return

        # Query the database to get employees and their keys associated with the selected restaurant
        self.cur.execute("SELECT key, firstname FROM Employee_data WHERE restaurantName = ?", (restaurant_name,))
        employee_data = self.cur.fetchall()

        # Create a new window to display employee names
        employees_window = tkinter.Toplevel()
        employees_window.title("View Employees")

        # Create a label to display employee names
        employee_label = tkinter.Label(employees_window, text="Employees:")
        employee_label.pack()

        # Create a listbox to display employee names
        employee_listbox = tkinter.Listbox(employees_window)
        employee_dict = {}  # Dictionary to map employee names to their user keys
        for employee in employee_data:
            employee_listbox.insert(tkinter.END, employee[1])
            employee_dict[employee[1]] = employee[0]  # Map name to user key
        employee_listbox.pack()

        # Button to add a new employee
        add_employee_button = tkinter.Button(employees_window, text="Add Employee", command=lambda: employee_main())
        add_employee_button.pack(pady=5)

        edit_employee_button = tkinter.Button(employees_window, text="Edit Employee", command=lambda: self.edit_employee(selected_employee.get()))
        edit_employee_button.pack(pady=5)

        # Button to delete an employee
        delete_employee_button = tkinter.Button(employees_window, text="Delete Employee", command=lambda: self.delete_employee(selected_employee.get()))
        delete_employee_button.pack(pady=5)

        # Function to handle the selection of an employee from the listbox
        def on_employee_select(event):
            selection = event.widget.curselection()
            if selection:
                index = selection[0]
                name = event.widget.get(index)
                selected_employee.set(employee_dict[name])  # Set the selected employee's user key

        # Bind the listbox select event to the function
        employee_listbox.bind('<<ListboxSelect>>', on_employee_select)

        # StringVar to hold the selected employee's user key
        selected_employee = tkinter.StringVar(employees_window)
        selected_employee.set("Select an employee")

    def edit_employee(self, employee_id):
        # Create a new window for editing employee details
        edit_employee_window = tkinter.Toplevel()
        edit_employee_window.title("Edit Employee Details")

        # Query the database to get the current details of the selected employee using the unique ID
        self.cur.execute("SELECT age, role, pay FROM Employee_data WHERE key = ?", (employee_id,))
        employee_info = self.cur.fetchone()

        # Header for Age
        age_header = tkinter.Label(edit_employee_window, text="Age:")
        age_header.pack(pady=(10, 0))

        # Use a Spinbox for age selection and make it read-only
        age_spinbox = tkinter.Spinbox(edit_employee_window, from_=16, to=99, state="readonly")
        age_spinbox.delete(0, 'end')  # Clear the spinbox
        age_spinbox.insert(0, employee_info[0])  # Set to current age
        age_spinbox.pack(pady=5)

        # Header for Role
        role_header = tkinter.Label(edit_employee_window, text="Role:")
        role_header.pack(pady=(10, 0))

        # Use a Combobox for role selection and make it read-only
        role_combobox = ttk.Combobox(edit_employee_window, values=self.roles, state="readonly")
        role_combobox.set(employee_info[1])  # Set to current role
        role_combobox.pack(pady=5)

        # Header for Pay
        pay_header = tkinter.Label(edit_employee_window, text="Pay:")
        pay_header.pack(pady=(10, 0))

        # Entry widget for pay
        pay_entry = tkinter.Entry(edit_employee_window)
        pay_entry.insert(0, employee_info[2])  # Set to current pay
        pay_entry.pack(pady=5)

        submit_button = tkinter.Button(edit_employee_window, text="Submit Changes",
                                    command=lambda: self.submit_employee_changes(employee_id,
                                                                                    age_spinbox.get(),
                                                                                    role_combobox.get(),
                                                                                    pay_entry.get(),
                                                                                    edit_employee_window))
        submit_button.pack(pady=10)

    def submit_employee_changes(self, employee_id, new_age, new_role, new_pay, edit_window):
        # Validate the pay before updating
        try:
            new_pay = float(new_pay)  # Attempt to convert the pay to a float
        except ValueError:
            messagebox.showerror("Error", "Pay must be a valid number.")
            return

        # Update the employee details in the database using the employee ID
        self.cur.execute("UPDATE Employee_data SET age = ?, role = ?, pay = ? WHERE key = ?",
                        (new_age, new_role, new_pay, employee_id))
        self.conn.commit()

        # Inform the user that the changes have been saved
        messagebox.showinfo("Success", "Employee details updated successfully.")

        # Close the edit window
        edit_window.destroy()
    def edit_restaurant(self, restaurantName):
        if self.permissions < 1:
            messagebox.showerror("Permission Denied", "You need higher permissions to edit restaurants.")
            return
        # Create a new window to edit the budget
        edit_window = tkinter.Toplevel()
        edit_window.title("Edit Business Information")

        # Initialize the main frame
        self.frame = tkinter.Frame(edit_window)
        self.frame.pack()

        # Create a label frame for user information
        self.user_info_frame = tkinter.LabelFrame(self.frame, text="Business Information")
        self.user_info_frame.grid(row=0, column=0, padx=20, pady=10)

        # Retrieve existing business details from the database
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()

        # Query the database to get the existing budget
        cursor.execute("SELECT restaurantBudget FROM restaurant_data WHERE restaurantName=?", (restaurantName,))
        budget_data = cursor.fetchone()

        conn.close()

        # Create a label and entry widget for editing the budget
        budget_label = tkinter.Label(self.user_info_frame, text="Weekly Budget")
        budget_label.grid(row=0, column=0, padx=10, pady=5)

        self.budget_entry = tkinter.Entry(self.user_info_frame)
        self.budget_entry.insert(0, budget_data[0])  # Populate the entry with existing budget
        self.budget_entry.grid(row=0, column=1, padx=30, pady=5)

        # Button to update the budget
        update_button = tkinter.Button(self.user_info_frame, text="Update", command=self.update_budget)
        update_button.grid(row=1, column=0, columnspan=2, pady=(5, 0), sticky="we")

        # Function to destroy the window after displaying the messagebox
        def destroy_window():
            edit_window.destroy()

        # Button to update the budget
        update_button = tkinter.Button(self.user_info_frame, text="Update", command=lambda: [self.update_budget(), destroy_window()])
        update_button.grid(row=1, column=0, columnspan=2, pady=(5, 0), sticky="we")

    def delete_restaurant_data(self, restaurant_name):
        if self.permissions < 2:
            messagebox.showerror("Permission Denied", "You need higher permissions to delete a restaurant.")
            return
        # Define a function to handle deletion after confirmation
        # Define a function to handle deletion after confirmation
        def confirm_delete():
            # Delete restaurant data from the days_data table
            self.cur.execute("DELETE FROM days_data WHERE restaurantName=?", (restaurant_name,))

            # Delete restaurant data from the restaurant_data table
            self.cur.execute("DELETE FROM restaurant_data WHERE restaurantName=?", (restaurant_name,))

            # Delete employee data associated with the restaurant
            self.cur.execute("DELETE FROM Employee_data WHERE restaurantName=?", (restaurant_name,))

            self.conn.commit()

            # Inform the user that the restaurant and related information have been deleted
            messagebox.showinfo("Success", "Restaurant and related information have been deleted.")

        # Ask for confirmation before deleting
        if messagebox.askyesno("Confirmation", "Are you sure you want to delete this restaurant and all related information?"):
            confirm_delete()



    def update_budget(self):
        try:
            new_budget = float(self.budget_entry.get())  # Get the new budget value from the entry widget
        except ValueError:
            messagebox.showerror("Error", "Weekly budget must be a valid number.")
            return

        # Update the budget in the database
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()

        cursor.execute("UPDATE restaurant_data SET restaurantBudget=?", (new_budget,))

        conn.commit()
        conn.close()

        # Inform the user that the budget update was successful
        messagebox.showinfo("Success", "Weekly budget updated successfully.")

    def create_restaurant(self):
        if self.permissions < 2:
            messagebox.showerror("Permission Denied", "You need higher permissions to create a restaurant.")
            return
        # Create a new window to enter business information
        business_window = tkinter.Toplevel()
        business_app = EnterWorkData(business_window)

if __name__ == "__main__":
    root = tkinter.Tk()
    app = LoginApp(root)
    root.mainloop()
import sqlite3
from Encryption import decrypt

class Employee:
    def __init__(self, firstname, lastname, age, role, gender, pay, key):
        # Initialize Employee object with provided attributes
        self.name = firstname.strip().capitalize() + ' ' + lastname.strip().capitalize()
        self.age = age
        self.role = role
        self.gender = gender
        self.key = key
        self.pay = pay

def Serialize(dict,list,restaurantName):
    # Retrieve employee data from the database
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT firstname, lastname, age, role, gender, pay, key FROM Employee_Data where restaurantName=?", (restaurantName, ))
    employees_data = cursor.fetchall()
    # Organize employee data as objects, stored in the dictionary by key
    for data in employees_data:
        firstname, lastname, age, role, gender, pay, key= data
        key=decrypt(key)
        list.append(key)
        employee = Employee(firstname, lastname, age, role, gender, pay, key)
        dict.setdefault(key, []).append(employee)
    conn.close()
import tkinter as tk
from datetime import datetime, timedelta, date 
from ObjectCreation import Serialize
import sqlite3
import math
import io
from PIL import ImageGrab
import random

class RotaApp:
    def __init__(self, root, restaurant, shifts, days):
        # Initialize RotaApp object
        self.roles = ['Manager', 'Waiter', 'Runner', 'Bartender', 'Barback']                    
        self.restaurant = restaurant
        self.employees = {}
        self.keys = []
        self.shifts = shifts
        Serialize(self.employees, self.keys, self.restaurant)
        
        self.root = root
        self.root.title("Weekly Rota")
        self.days = days
    
        self.row_index = 1  # Initialize row index

        # Connect to the database
        self.conn = sqlite3.connect('data.db')
        self.cursor = self.conn.cursor()
         # Calculate the first day of the current week
        today = datetime.now()
        self.first_day_of_week = today - timedelta(days=today.weekday())

        # Add label for the week commencing
        tk.Label(root, text=f"Week Commencing: {self.first_day_of_week.strftime('%d-%m-%Y')}").grid(row=0, columnspan=len(self.days) + 1)
        # Create the timetable GUI
        self.calculate_max()
        self.day_labels()
        self.employees_shifts = self.generate_shift_schedules()  # Store generated shift schedules
        self.populate_table(self.employees_shifts)  # Pass shift schedules to populate_table

        # Add Save Schedule button
        save_button = tk.Button(root, text="Save Schedule", command=self.save_schedule)
        save_button.grid(row=self.row_index, column=0, pady=10, padx=5)

        # Add View Wages button
        view_wages_button = tk.Button(root, text="View Wages", command=self.view_wages)
        view_wages_button.grid(row=self.row_index, column=1, pady=10, padx=5)

    def calculate_max(self):
        # Determine maximum name and role lengths
        self.max_name_length = max(len(self.employees[emp_id][0].name) for emp_id in self.employees.keys())
        self.max_role_length = max(len(self.employees[emp_id][0].role) for emp_id in self.employees.keys())

    def day_labels(self):
        # Create labels for days
        for i, day in enumerate(self.days):
            tk.Label(self.root, text=day, width=10, relief=tk.RIDGE).grid(row=1, column=i + 1)

    def populate_table(self, employees_shifts):
        # Group employees by role
        employees_by_role = {role: [] for role in self.roles}
        for emp_id in self.employees.keys():
            employee = self.employees[emp_id][0]
            employees_by_role[employee.role].append(employee)

        # Populate timetable with employee data grouped by role
        for role, employees in employees_by_role.items():
            if employees != []:
                tk.Label(self.root, text=role, width=self.max_role_length, relief=tk.RIDGE).grid(row=self.row_index, column=0)
                self.row_index += 1
                for employee in employees:
                    tk.Label(self.root, text=employee.name, width=self.max_name_length, relief=tk.RIDGE).grid(row=self.row_index, column=0)
                    for j, day in enumerate(self.days):
                        shift_info = employees_shifts[day].get(employee.key)
                        if shift_info:
                            shift_found = False
                            for shift_tuple in shift_info:
                                shift_day, shift_time, shift_role = shift_tuple
                                if shift_role == role:
                                    shift_found = True
                                    shift_time = f"{shift_time.split('-')[0]}-{shift_time.split('-')[1]}"  # Adjust the format if needed
                                    tk.Label(self.root, text=shift_time, width=self.max_name_length, relief=tk.RIDGE).grid(row=self.row_index, column=j + 1)
                                    break
                            if not shift_found:
                                tk.Label(self.root, text="OFF", width=self.max_name_length, relief=tk.RIDGE).grid(row=self.row_index, column=j + 1)
                        else:
                            tk.Label(self.root, text="OFF", width=self.max_name_length, relief=tk.RIDGE).grid(row=self.row_index, column=j + 1)

                    self.row_index += 1

                tk.Label(self.root, text="", width=10).grid(row=self.row_index, column=0)
                self.row_index += 1

    def view_wages(self):
        # Create a new window to display wages
        wages_window = tk.Toplevel(self.root)
        wages_window.title("Wages")

        # Retrieve the wage bill text
        wages_text = self.calculate_wages_text(self.employees_shifts)

        # Create a text widget to display the combined wage bill and budget status
        text_widget = tk.Text(wages_window, wrap='word', height=20, width=50)
        text_widget.pack(expand=True, fill='both')

        # Insert the combined wages text into the text widget
        text_widget.insert('1.0', wages_text)

        # Make the text widget read-only
        text_widget.config(state='disabled')

        return wages_text

    def combine_shifts(self, employees_shifts):
        # Iterate through each day
        for day, shifts_info in employees_shifts.items():
            # Iterate through each employee's shifts
            for employee_id, shifts in shifts_info.items():
                combined_shifts = []
                current_shift_start = None
                current_shift_end = None
                # Sort shifts by start time
                shifts.sort(key=lambda x: x[1])

                for shift in shifts:
                    shift_start, shift_end = shift[1].split('-')
                    # If no current shift, set it as the current shift
                    if current_shift_start is None:
                        current_shift_start = shift_start
                        current_shift_end = shift_end
                    # If consecutive shift found, update the end time of the current shift
                    elif shift_start == current_shift_end:
                        current_shift_end = shift_end
                    # If not consecutive, add the current shift and start a new one
                    else:
                        combined_shifts.append((day, f"{current_shift_start}-{current_shift_end}", shift[2]))
                        current_shift_start = shift_start
                        current_shift_end = shift_end
                
                # Add the last combined shift
                combined_shifts.append((day, f"{current_shift_start}-{current_shift_end}", shift[2]))

                # Update employee's shifts with the combined shifts
                employees_shifts[day][employee_id] = combined_shifts

        return employees_shifts


    def generate_shift_schedules(self):
        # Initialize necessary variables
        covers = {}
        assignedShifts = {day: {shift: {role: [] for role in self.roles} for shift in self.shifts[day]} for day in self.days}
        employees_shifts = {day: {} for day in self.days}
        employees_by_role = {role: [] for role in self.roles}
        for emp_id in self.employees.keys():
            employee = self.employees[emp_id][0]
            employees_by_role[employee.role].append(employee)

        # Calculate the total shift points needed for each role on each day
        total_shift_points = {day: {role: 0 for role in self.roles} for day in self.days}
        for day in self.days:
            if day != "Sunday":
                covers[day] = random.randint(25,75)
            else:
                covers[day] = random.randint(75,125)
            for role in self.roles:
                if role == 'Manager':
                    total_shift_points[day][role] = 1
                elif role == 'Bartender':
                    total_shift_points[day][role] = 1
                elif role == 'Waiter':
                    total_shift_points[day][role] = 1
                if covers[day]>25:
                    if role == 'Barback' and covers[day] > 25:
                        total_shift_points[day][role] = 1
                    if role == 'Runner':
                        total_shift_points[day][role] = max(1, min(math.ceil(covers[day] / 50), 4))

        # Assign shifts to employees
        for day in self.days:
            todayShifts=self.shifts[day]
            employees_needed = {role: total_shift_points[day][role] for role in self.roles}
            for role in self.roles:
                employeesAvailable = employees_by_role[role]
                random.shuffle(employeesAvailable)
                if employees_needed[role] > 0:
                    shifts_per_employee = [len(todayShifts) // len(employeesAvailable) + (1 if i < len(todayShifts) % len(employeesAvailable) else 0) for i in range(len(employeesAvailable))]
                    shift_index = 0
                    for employee, num_shifts in zip(employeesAvailable, shifts_per_employee):
                        for _ in range(num_shifts):
                            assigned_shift = todayShifts[shift_index]
                            assignedShifts[day][assigned_shift][role].append(employee)
                            if employee.key not in employees_shifts[day]:
                                employees_shifts[day][employee.key] = []
                            employees_shifts[day][employee.key].append((day, assigned_shift, role))
                            shift_index += 1
        employees_shifts = self.combine_shifts(employees_shifts)
        return employees_shifts
    
    def save_schedule(self):
        # Get the dimensions of the GUI window
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()

        # Get the position of the GUI window relative to the screen
        window_x = self.root.winfo_rootx()
        window_y = self.root.winfo_rooty()

        # Calculate the bounding box for the screenshot
        bbox = (window_x, window_y, window_x + window_width, window_y + window_height - 40)

        # Grab the screenshot of the entire GUI window
        screenshot = ImageGrab.grab(bbox=bbox)

        # Convert image to binary data
        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        # Get the first day of the week
        today = date.today()
        first_day_of_week = today - timedelta(days=today.weekday())

        # Convert first day of the week to string in the format "dd/mm/yyyy"
        first_day_of_week_str = first_day_of_week.strftime('%d-%m-%Y')


        # Update 'currentRota' column with the rota PNG
        self.cursor.execute(f"UPDATE current_data SET currentRota = ? WHERE restaurantName = ?", (img_byte_arr, self.restaurant))

        # Save wages text as a text file
        wages_text = self.calculate_wages_text(self.employees_shifts)

        # Update 'currentWages' column with the wage text file path
        self.cursor.execute(f"UPDATE current_data SET currentWages = ? WHERE restaurantName = ?", (wages_text, self.restaurant))

        self.conn.commit()

        print("Schedule saved to the database.")
    def calculate_wages_text(self, employees_shifts):
        wages_text = "Weekly Wages:\n"
        total_wage_bill = 0
        employee_wages = {}

        for day, shifts_info in employees_shifts.items():
            for employee_id, shifts in shifts_info.items():
                total_hours_worked = 0
                employee_name = self.employees[employee_id][0].name
                hourly_pay_rate = self.employees[employee_id][0].pay

                for shift in shifts:
                    shift_start, shift_end = shift[1].split('-')
                    start_hour, start_minute = map(int, shift_start.split(':'))
                    end_hour, end_minute = map(int, shift_end.split(':'))

                    if end_hour == 0:  # Handle shifts ending at midnight
                        end_hour = 24

                    if start_hour > end_hour:  # Adjust for shifts starting before midnight and ending after midnight
                        total_hours_worked += (24 - start_hour) + end_hour + (end_minute - start_minute) / 60
                    else:
                        total_hours_worked += end_hour - start_hour + (end_minute - start_minute) / 60

                if total_hours_worked < 0:
                    print(f"Error: Negative hours worked for employee {employee_id} on {day}")
                    continue  # Skip calculation for this employee

                weekly_wage = total_hours_worked * hourly_pay_rate

                # Accumulate total wage for the week for each employee
                if employee_id not in employee_wages:
                    employee_wages[employee_id] = 0
                employee_wages[employee_id] += weekly_wage

        # Output total weekly wages for each employee
        for employee_id, total_wage in employee_wages.items():
            employee_name = self.employees[employee_id][0].name
            wages_text += f"{employee_name}: ${total_wage:.2f}\n"
            total_wage_bill += total_wage

        wages_text += f"\nTotal Wage Bill: ${total_wage_bill:.2f}"
        # Extract the total wages amount from the wages_text
        total_wages = float(wages_text.split('Total Wage Bill: $')[-1].strip())

        # Retrieve the restaurant budget from the restaurant_data table
        self.cursor.execute("SELECT restaurantBudget FROM restaurant_data WHERE restaurantName = ?", (self.restaurant, ))
        budget_data = self.cursor.fetchone()
        if budget_data:
            restaurant_budget = float(budget_data[0])

            # Calculate the difference between the total wages and the restaurant budget
            budget_difference = total_wages - restaurant_budget

            # Determine the budget status and the amount by which it is over or within the budget
            if budget_difference > 0:
                budget_status = "Over Budget by ${:.2f}".format(budget_difference)
            else:
                budget_status = "Within Budget by ${:.2f}".format(abs(budget_difference))

            # Combine the wages text and the budget status into one string
            wages_text = "{}\n\nBudget Status: {}".format(wages_text, budget_status)

        return wages_text

