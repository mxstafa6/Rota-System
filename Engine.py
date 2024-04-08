import tkinter as tk
import sqlite3

StaffDetails = {}

conn = sqlite3.connect('data.db')
cursor = conn.cursor()
cursor.execute("SELECT key FROM Employee_Data")
keys = cursor.fetchall()
cursor.execute("SELECT firstname FROM Employee_Data")  
firstnames=cursor.fetchall()
cursor.execute("SELECT lastname FROM Employee_Data")
lastnames=cursor.fetchall()
cursor.execute("SELECT age FROM Employee_Data")
ages=cursor.fetchall()
cursor.execute("SELECT role FROM Employee_Data")
roles=cursor.fetchall()
cursor.execute("SELECT gender FROM Employee_Data")
genders=cursor.fetchall()

class Employee():
    def __init__(self, name, age, role, gender):
        self.name = name
        self.age = age
        self.role = role
        self.gender = gender

class RotaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weekly Rota")

        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.employees = []

        self.create_timetable()

    def create_timetable(self):
        for i, day in enumerate(self.days):
            tk.Label(self.root, text=day, width=10, relief=tk.RIDGE).grid(row=0, column=i+1)
        
        for i, hour in enumerate(self.employees):
            tk.Label(self.root, text=hour, width=10, relief=tk.RIDGE).grid(row=i+1, column=0)
            
            for j in range(len(self.days)):
                entry = tk.Entry(self.root, width=10, relief=tk.SOLID)
                entry.grid(row=i+1, column=j+1)

if __name__ == "__main__":
    root = tk.Tk()
    app = RotaApp(root)
    root.mainloop()