import tkinter
from tkinter import messagebox
from Encryption import encrypt
from BusinessInfo import EnterWorkData
import sqlite3

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

    def view_restaurants(self):
        # Create a new window to display restaurant names
        view_window = tkinter.Toplevel()
        view_window.title("View Restaurants")

        # Query the database to get restaurant names associated with the encrypted user key
        self.cur.execute("SELECT restaurantName FROM Employee_data WHERE key = ?", (self.user_key_encrypted, ))
        restaurant_data = self.cur.fetchall()

        # Create a dropdown menu to display restaurant names
        selected_restaurant = tkinter.StringVar(view_window)
        selected_restaurant.set(restaurant_data[0] if restaurant_data else "No Restaurants")

        dropdown_menu = tkinter.OptionMenu(view_window, selected_restaurant, *restaurant_data)
        dropdown_menu.pack(padx=10, pady=10)

        def show_selected():
            messagebox.showinfo("Selected Restaurant", f"You selected: {selected_restaurant.get()}")

        # Create a button to show the selected restaurant
        show_button = tkinter.Button(view_window, text="Show", command=show_selected)
        show_button.pack(pady=10)


    def create_restaurant(self):
        # Create a new window to enter business information
        business_window = tkinter.Toplevel()
        business_app = EnterWorkData(business_window)

if __name__ == "__main__":
    root = tkinter.Tk()
    app = LoginApp(root)
    root.mainloop()
