import sqlite3

monday={}
tuesday={}
wednesday={}
thursday={}
friday={}
saturday={}
sunday={}

class Rota()
conn = sqlite3.connect('data.db')  # Connect to the SQLite database
cursor = conn.cursor()
# Check if the restaurant name already exists in the database
cursor.execute("SELECT restaurantName FROM restaurant_data WHERE restaurantName=?")
existing_name = cursor.fetchone()
conn.close()