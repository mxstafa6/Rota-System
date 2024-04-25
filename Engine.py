import sqlite3
from ObjectCreation import Serialize

monday={}
tuesday={}
wednesday={}
thursday={}
friday={}
saturday={}
sunday={}

class Rota:
    def __init__(self, restaurantName):
        conn = sqlite3.connect('data.db')  # Connect to the SQLite database
        cursor = conn.cursor()
        # Check if the restaurant name already exists in the database
        cursor.execute("SELECT restaurantName FROM Employee_Data WHERE restaurantName=?", (restaurantName,) )
        conn.close()
