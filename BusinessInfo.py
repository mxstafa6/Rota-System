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
                           (restaurantName TEXT, pastRota BLOB, pastData TEXT)''')
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
