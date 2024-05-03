import sqlite3

conn = sqlite3.connect('data.db')
cursor = conn.cursor()
cursor.execute("INSERT INTO current_data (restaurantName) VALUES (?)", ('Marlos',))
conn.commit()
