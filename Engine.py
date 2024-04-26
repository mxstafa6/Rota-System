import sqlite3
from ObjectCreation import Serialize

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

class Rota:

    def __init__(self, restaurantName):
        self.restaurantname = restaurantName
        self.check_off_days(days)
        self.covers = {}
        for day in days:
            self.covers[day] = None
        self.employees = {}
        self.keys = []
        Serialize(self.employees, self.keys, restaurantName)

    def check_off_days(self, days):
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
            # Skip the restaurantName column
            if column == 'restaurantName':
                continue
            # If the day is off, remove it from the list of days
            cursor.execute(f"SELECT {column} FROM days_data WHERE restaurantName = ? AND {column} = 'OFF-OFF'",
                           (self.restaurantname,))
            # Fetch the result
            result = cursor.fetchone()
            # If the result is not None, the day is off
            if result is not None:
                days.remove(column)

        # Close the cursor and connection
        cursor.close()
        conn.close()

app = Rota('1a')
