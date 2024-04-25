import tkinter as tk
import sqlite3
from ObjectCreation import Serialize
from EmployeeCreation import roles

class RotaApp:
    def __init__(self, root):
        # Initialize RotaApp object
        self.employees={}
        self.keys=[]
        Serialize(self.employees,self.keys, '1a')
        
        self.root = root
        self.root.title("Weekly Rota")
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        self.row_index = 1  # Initialize row index

        # Create the timetable GUI
        self.calculate_max()
        self.day_labels()
        self.populate_table()
    
    def calculate_max(self):
        # Determine maximum name and role lengths
        self.max_name_length = max(len(emp.name) for emp_list in self.employees.values() for emp in emp_list)
        self.max_role_length = max(len(emp.role) for emp_list in self.employees.values() for emp in emp_list)

    def day_labels(self):
        # Create labels for days
        for i, day in enumerate(self.days):
            tk.Label(self.root, text=day, width=10, relief=tk.RIDGE).grid(row=0, column=i + 1)

    def populate_table(self):
        # Group employees by role
        employees_by_role = {role: [] for role in roles}
        for employees in self.employees.values():
            for employee in employees:
                employees_by_role[employee.role].append(employee)

        # Populate timetable with employee data grouped by role
        for role, employees in employees_by_role.items():
            if employees != []:
                tk.Label(self.root, text=role, width=self.max_role_length, relief=tk.RIDGE).grid(row=self.row_index, column=0)
                self.row_index += 1
                for employee in employees:
                    tk.Label(self.root, text=employee.name, width=self.max_name_length, relief=tk.RIDGE).grid(row=self.row_index, column=0)
                    for j in range(len(self.days)):
                        entry = tk.Entry(self.root, width=self.max_name_length, relief=tk.SOLID)
                        entry.grid(row=self.row_index, column=j + 1)
                    self.row_index += 1

                tk.Label(self.root, text="", width=10).grid(row=self.row_index, column=0)
                self.row_index += 1

if __name__ == "__main__":
    # Create Tkinter root window and start the event loop
    root = tk.Tk()
    app = RotaApp(root)
    root.mainloop()
