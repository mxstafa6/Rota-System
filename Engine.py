import sqlite3
import tkinter as tk
import math
from datetime import datetime, timedelta
from ObjectCreation import Serialize
from TableDrawer import RotaApp

class RestaurantInformationRetriever:
    def __init__(self, restaurantName):
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        self.restaurantname = restaurantName
        self.check_off_days()
        self.shifts = {}
        self.covers = {}
        for day in self.days:
            self.shifts[day] = None
            self.covers[day] = 0
        self.get_shift()

    def check_off_days(self):
        # Connect to the SQLite database
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()

        # Execute the query to select all columns with the value "OFF-OFF" for the specified restaurant
        cursor.execute(f"SELECT * FROM days_data WHERE restaurantName = ? AND "
                       f"(Monday = 'OFF-OFF' OR Tuesday = 'OFF-OFF' OR Wednesday = 'OFF-OFF' OR Thursday = 'OFF-OFF' OR "
                       f"Friday = 'OFF-OFF' OR Saturday = 'OFF-OFF' OR Sunday = 'OFF-OFF')", (self.restaurantname,))

        # Fetch the column names
        columns = [description[0] for description in cursor.description]

        # Iterate over the columns and remove days marked as off
        for column in columns:
            # Skip the restaurantName column``
            if column == 'restaurantName':
                continue
            # If the day is off, remove it from the list of days
            cursor.execute(f"SELECT {column} FROM days_data WHERE restaurantName = ? AND {column} = 'OFF-OFF'",
                           (self.restaurantname,))
            # Fetch the result
            result = cursor.fetchone()
            # If the result is not None, the day is off
            if result is not None:
                self.days.remove(column)

        # Close the cursor and connection
        cursor.close()
        conn.close()

    def get_shift(self):
        # Connect to the SQLite database
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        
        for day in self.days:
            cursor.execute(f"SELECT {day} FROM days_data WHERE restaurantName = ?",
                        (self.restaurantname,))
            shift = cursor.fetchone()[0]
            
            # Split the shift into open and close time
            open_time, _, close_time = shift.partition('-')
            
            # Parse the time strings into datetime objects
            open_datetime = datetime.strptime(open_time.strip(), "%H:%M")
            close_datetime = datetime.strptime(close_time.strip(), "%H:%M")
            
            # Calculate the difference between open and close time
            if close_datetime < open_datetime:  # Adjust for closing time before opening time
                close_datetime += timedelta(days=1)  # Increment day for closing time
                
            time_difference = close_datetime - open_datetime
            time_difference_minutes = abs(time_difference.total_seconds() // 60)
            
            # Calculate the number of shifts needed
            num_shifts = math.ceil(time_difference_minutes / 360)
            
            # Calculate the duration of each shift
            shift_duration = time_difference_minutes / num_shifts
            
            shifts = []
            for i in range(num_shifts):
                # Calculate shift start and end times
                shift_start = open_datetime + timedelta(minutes=shift_duration * i)
                shift_end = shift_start + timedelta(minutes=shift_duration)
                shift_str = f"{shift_start:%H:%M}-{shift_end:%H:%M}"  # Format as XX:XX-XX:XX
                shifts.append(shift_str)
            
            # Store shifts in the dictionary
            self.shifts[day] = shifts

app = RestaurantInformationRetriever('Aura')
root = tk.Tk()
app = RotaApp(root, 'Aura', app.shifts, app.days)
root.mainloop()