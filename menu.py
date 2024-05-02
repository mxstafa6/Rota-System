import tkinter
from tkinter import messagebox
from Encryption import encrypt
from BusinessInfo import EnterWorkData
import sqlite3
masterKey=26012006
class LoginApp:
    def __init__(self, root):
        self.permissions=0
        self.root = root
        self.root.title("Login")

        self.password_label = tkinter.Label(self.root, text="User Key:")
        self.password_label.grid(row=1, column=0, padx=10, pady=5)
        self.password_entry = tkinter.Entry(self.root, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)

        self.login_button = tkinter.Button(self.root, text="Login", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

        # Connect to SQLite database
        self.conn = sqlite3.connect("data.db")
        self.cur = self.conn.cursor()

    def login(self):
        user_key = self.password_entry.get()

        # Check if the user key is a 4-digit number
        if not user_key.isdigit() or len(user_key) != 4:
            messagebox.showerror("Error", "User key must be a 4-digit number")
            return

        # Encrypt the user key
        self.user_key_encrypted = encrypt(user_key)

        # Query the database to check if the user key exists
        self.cur.execute("SELECT * FROM Employee_data WHERE key = ?", (self.user_key_encrypted,))
        user_data = self.cur.fetchone()

        if user_data:
            messagebox.showinfo("Success", "Login successful!")
            # Destroy the login window
            self.root.destroy()
            # Open the main application window
            self.open_main_window()
        else:
            messagebox.showerror("Error", "Invalid user key")

    def open_main_window(self):
        main_window = tkinter.Tk()
        main_window.title("Main Menu")

        view_restaurants_button = tkinter.Button(main_window, text="View Restaurants", command=self.view_restaurants)
        view_restaurants_button.pack(pady=10)

        create_restaurant_button = tkinter.Button(main_window, text="Create Restaurant", command=self.create_restaurant)
        create_restaurant_button.pack(pady=10)

        create_rota_button = tkinter.Button(main_window, text="Create Rota", command=self.create_rota)
        create_rota_button.pack(pady=10)

        view_rota_button = tkinter.Button(main_window, text="View Rota", command=self.view_rota)
        view_rota_button.pack(pady=10)


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

        delete_restaurant_button = tkinter.Button(view_window, text="Delete Restaurant", command=lambda: self.delete_restaurant_data(selected_restaurant.get()[2:-3]))
        delete_restaurant_button.pack(pady=5)
    
    # Define methods for the additional functionalities
    def view_employees(self, restaurant_name):
        # Query the database to get employees associated with the selected restaurant
        self.cur.execute("SELECT firstname FROM Employee_data WHERE restaurantName = ?", (restaurant_name,))
        employee_data = self.cur.fetchall()

        # Create a new window to display employee names
        employees_window = tkinter.Toplevel()
        employees_window.title("View Employees")

        # Create a label to display employee names
        employee_label = tkinter.Label(employees_window, text="Employees:")
        employee_label.pack()

        # Create a listbox to display employee names
        employee_listbox = tkinter.Listbox(employees_window)
        for employee in employee_data:
            employee_listbox.insert(tkinter.END, employee[0])
        employee_listbox.pack()

    def edit_restaurant(self, restaurantName):
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
        # Create a new window to enter business information
        business_window = tkinter.Toplevel()
        business_app = EnterWorkData(business_window)

if __name__ == "__main__":
    root = tkinter.Tk()
    app = LoginApp(root)
    root.mainloop()
