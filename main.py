import tkinter
import io
from PIL import Image, ImageTk # type: ignore
from tkinter import messagebox, ttk
import sqlite3
from Encryption import encrypt
from BusinessInfo import EnterWorkData
from TableDrawer import main, Stack
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
        self.action_stack = Stack()

    # Set up the login widgets.
    def setup_widgets(self):
        self.password_label = tkinter.Label(self.root, text="User Key:")
        self.password_label.grid(row=1, column=0, padx=10, pady=5)
        self.password_entry = tkinter.Entry(self.root, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)
        self.login_button = tkinter.Button(self.root, text="Login", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, padx=10, pady=5)
        self.exit_button = tkinter.Button(self.root, text="Exit", command=quit)
        self.exit_button.grid(row=2, column=1, columnspan=2, padx=10, pady=5)

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
        try:
            self.cur.execute("SELECT role FROM employee_data WHERE key = ?", (self.user_key_encrypted,))
            user_data = self.cur.fetchone()
            if user_data:
                messagebox.showinfo("Success", "Login successful!")
                if user_data[0] == 'Manager':
                    self.permissions += 1
                self.open_main_window()
            else:
                messagebox.showerror("Error", "Invalid user key")
        except:
            messagebox.showerror("Error", "Login using the master key.")
            return

    # Open the main application window after successful login.
    def open_main_window(self, all_restaurants=False):
        # Destroy the existing main_window if it exists
        if hasattr(self, 'main_window'):
            self.main_window.destroy()

        self.main_window = tkinter.Toplevel(self.root)
        self.main_window.title("Main Menu")

        if all_restaurants:
            view_restaurants_button = tkinter.Button(self.main_window, text="View All Restaurants", command=self.view_all_restaurants)
            view_restaurants_button.pack(pady=10)
        else:
            view_restaurants_button = tkinter.Button(self.main_window, text="View Restaurants", command=self.view_restaurants)
            view_restaurants_button.pack(pady=10)
        create_restaurant_button = tkinter.Button(self.main_window, text="Create Restaurant", command=self.create_restaurant)
        create_restaurant_button.pack(pady=10)
        # Button to view the action stack
        view_action_stack_button = tkinter.Button(self.main_window, text="View Action Stack", command=self.view_action_stack)
        view_action_stack_button.pack(pady=10)
        self.root.withdraw()  # Hide the login window
        self.main_window.mainloop()  # Start the main loop for the main window
    def view_action_stack(self):
        if self.permissions < 1:
            messagebox.showerror("Permission Denied", "You need higher permissions to view past actions.")
            return
        # Create a new window to display the action stack
        stack_window = tkinter.Toplevel()
        stack_window.title("Action Stack")

        # Create a listbox to display the action stack
        stack_listbox = tkinter.Listbox(stack_window, width=50)
        stack_listbox.pack(padx=10, pady=10)

        # Populate the listbox with the contents of the action stack
        for action in reversed(self.action_stack.items):
            if action[1] == "employee_update":
                employee_id, _, _ = action
                stack_listbox.insert(tkinter.END, f"Edited employee {employee_id}")
            elif action[1] == "budget_update":
                restaurant_name, _, _ = action
                stack_listbox.insert(tkinter.END, f"Updated budget for {restaurant_name}")
            elif action[0] == "create_restaurant":  # Check for the specific action tuple
                stack_listbox.insert(tkinter.END, "Created a new restaurant")
    def view_all_restaurants(self):
        # Create a new window to display all restaurant names and additional options
        all_view_window = tkinter.Toplevel()
        all_view_window.title("View All Restaurants")
        try:
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
        except:
            messagebox.showerror("Error", "No restaurants available to view.")
            all_view_window.destroy()  # Close the view window as there's nothing to show
            return

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
        try:
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
        except:
            messagebox.showerror("Error", "No rota to view.")

    def view_restaurants(self):
        # Create a new window to display restaurant names and additional options
        view_window = tkinter.Toplevel()
        view_window.title("View Restaurants")
        try:
            # Query the database to get restaurant names associated with the encrypted user key
            self.cur.execute("SELECT restaurantName FROM employee_data WHERE key = ?", (self.user_key_encrypted,))
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
        except:
            messagebox.showerror("Error", "No restaurants available to view.")
            view_window.destroy()  # Close the view window as there's nothing to show
            return
        
    # Define methods for the additional functionalities
    def view_employees(self, restaurant_name):
        if self.permissions < 1:
            messagebox.showerror("Permission Denied", "You need higher permissions to view employees.")
            return
        try:
            self.cur.execute("SELECT key, firstname FROM employee_data WHERE restaurantName = ?", (restaurant_name,))
            employee_data = self.cur.fetchall()

            # Sort the employee data in alphabetical order by their first name using Merge Sort
            merge_sort(employee_data)

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
        except:
            messagebox.showerror("Error", "No employee table available.")
    def delete_employee(self, employee_key):
        try:
            # Delete the employee data from the employee_data table
            self.cur.execute("DELETE FROM employee_data WHERE key=?", (employee_key,))
            self.conn.commit()

            # Inform the user that the employee has been deleted
            messagebox.showinfo("Success", "Employee has been deleted successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while deleting the employee: {str(e)}")
    def edit_employee(self, employee_id):
        # Create a new window for editing employee details
        edit_employee_window = tkinter.Toplevel()
        edit_employee_window.title("Edit Employee Details")

        # Query the database to get the current details of the selected employee using the unique ID
        self.cur.execute("SELECT age, role, pay FROM employee_data WHERE key = ?", (employee_id,))
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
        # Push the current employee details to the action stack
          # Push a generic message to the action stack without details
        self.action_stack.push((employee_id, "employee_update", None))

        # Update the employee details in the database using the employee ID
        self.cur.execute("UPDATE employee_data SET age = ?, role = ?, pay = ? WHERE key = ?",
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

        # Function to destroy the window after displaying the messagebox
        def destroy_window():
            edit_window.destroy()

        # Button to update the budget
        update_button = tkinter.Button(self.user_info_frame, text="Update", command=lambda: [self.update_budget(restaurantName), destroy_window()])
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
            self.cur.execute("DELETE FROM employee_data WHERE restaurantName=?", (restaurant_name,))

            self.cur.execute("DELETE FROM current_data WHERE restaurantName=?", (restaurant_name,))

            self.conn.commit()

            # Inform the user that the restaurant and related information have been deleted
            messagebox.showinfo("Success", "Restaurant and related information have been deleted.")

        # Ask for confirmation before deleting
        if messagebox.askyesno("Confirmation", "Are you sure you want to delete this restaurant and all related information?"):
            confirm_delete()



    def update_budget(self, restaurantName):
        try:
            new_budget = float(self.budget_entry.get())  # Get the new budget value from the entry widget
        except ValueError:
            messagebox.showerror("Error", "Weekly budget must be a valid number.")
            return
        # Push the current budget to the action stack
        self.action_stack.push((restaurantName, "budget_update", None))
        # Update the budget in the database
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()

        cursor.execute("UPDATE restaurant_data SET restaurantBudget=? WHERE restaurantName=?", (new_budget, restaurantName))

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

        self.action_stack.push(("create_restaurant", None, None))

#Sorts employees alphabetically
def merge_sort(employee_list):
    if len(employee_list) > 1:
        mid = len(employee_list) // 2
        left_half = employee_list[:mid]
        right_half = employee_list[mid:]

        merge_sort(left_half)
        merge_sort(right_half)

        i = j = k = 0
        while i < len(left_half) and j < len(right_half):
            if left_half[i][1] < right_half[j][1]:  # Compare the names
                employee_list[k] = left_half[i]
                i += 1
            else:
                employee_list[k] = right_half[j]
                j += 1
            k += 1

        while i < len(left_half):
            employee_list[k] = left_half[i]
            i += 1
            k += 1

        while j < len(right_half):
            employee_list[k] = right_half[j]
            j += 1
            k += 1

if __name__ == "__main__":
    root = tkinter.Tk()
    app = LoginApp(root)
    root.mainloop()
