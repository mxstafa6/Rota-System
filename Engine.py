import tkinter as tk
import sqlite3

conn = sqlite3.connect('data.db')
cursor = conn.cursor()
cursor.execute("SELECT firstname, lastname, age, role, gender FROM Employee_Data")
employees_data = cursor.fetchall()

class Employee:
    def __init__(self, firstname, lastname, age, role, gender):
        self.firstname = firstname.strip()
        self.lastname = lastname.strip()
        self.age = age
        self.role = role
        self.gender = gender

class RotaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weekly Rota")

        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.employees = {}
        self.row_index = 1  # Initialize the row index
        self.create_employee_roles_dict()

        self.create_timetable()

    def create_employee_roles_dict(self):
        # Populate employees dictionary categorized by role
        for data in employees_data:
            firstname, lastname, age, role, gender = data
            employee = Employee(firstname, lastname, age, role, gender)
            if role not in self.employees:
                self.employees[role] = []
            self.employees[role].append(employee)

    def create_timetable(self):
        # Display days at the top of the table
        for i, day in enumerate(self.days):
            tk.Label(self.root, text=day, width=10, relief=tk.RIDGE).grid(row=0, column=i + 1)

        # Display roles, employees, and empty entries with gaps
        for role, employees in self.employees.items():
            tk.Label(self.root, text=role, width=10, relief=tk.RIDGE).grid(row=self.row_index, column=0)
            self.row_index += 1  # Move to the next row for the role header
            for employee in employees:
                employee_name = f"{employee.firstname} {employee.lastname}"
                tk.Label(self.root, text=employee_name, width=10, relief=tk.RIDGE).grid(row=self.row_index, column=0)
                for j in range(len(self.days)):
                    entry = tk.Entry(self.root, width=10, relief=tk.SOLID)
                    entry.grid(row=self.row_index, column=j + 1)
                self.row_index += 1  # Move to the next row for the empty entries
            self.row_index += 1  # Add a gap between roles


if __name__ == "__main__":
    root = tk.Tk()
    app = RotaApp(root)
    root.mainloop()
