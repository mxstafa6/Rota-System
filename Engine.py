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