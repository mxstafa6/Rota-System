import tkinter as tk
import sqlite3

class Employee:
    def __init__(self, firstname, lastname, age, role, gender):
        # Initialize Employee object with provided attributes
        self.firstname = firstname.strip()
        self.lastname = lastname.strip()
        self.age = age
        self.role = role
        self.gender = gender

class RotaApp:
    def __init__(self, root):
        # Initialize RotaApp object
        self.root = root
        self.root.title("Weekly Rota")

        # Days of the week
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        # Fetch employee data from the database
        self.employees = self.get_employee_data()
        self.row_index = 1  # Initialize row index

        # Create the timetable GUI
        self.create_timetable()

    def get_employee_data(self):
        # Retrieve employee data from the database
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT firstname, lastname, age, role, gender FROM Employee_Data")
        employees_data = cursor.fetchall()

        # Organize employee data into a dictionary
        employees = {}
        for data in employees_data:
            firstname, lastname, age, role, gender = data
            employee = Employee(firstname, lastname, age, role, gender)
            employees.setdefault(role, []).append(employee)
        
        conn.close()
        return employees

    def create_timetable(self):
        # Determine maximum name and role lengths
        max_name_length = max(len(f"{emp.firstname} {emp.lastname}") for emp_list in self.employees.values() for emp in emp_list)
        max_role_length = max(len(role) for role in self.employees.keys())
        
        # Create labels for days
        for i, day in enumerate(self.days):
            tk.Label(self.root, text=day, width=10, relief=tk.RIDGE).grid(row=0, column=i + 1)

        # Populate timetable with employee data
        for role, employees in self.employees.items():
            tk.Label(self.root, text=role, width=max_role_length, relief=tk.RIDGE).grid(row=self.row_index, column=0)
            self.row_index += 1
            
            for employee in employees:
                employee_name = f"{employee.firstname} {employee.lastname}"
                tk.Label(self.root, text=employee_name, width=max_name_length, relief=tk.RIDGE).grid(row=self.row_index, column=0)
                
                for j in range(len(self.days)):
                    entry = tk.Entry(self.root, width=max_name_length, relief=tk.SOLID)
                    entry.grid(row=self.row_index, column=j + 1)
                    
                self.row_index += 1

            self.row_index += 1
            tk.Label(self.root, text="", width=10).grid(row=self.row_index, column=0)
            self.row_index += 1
        print(self.employees)
if __name__ == "__main__":
    # Create Tkinter root window and start the event loop
    root = tk.Tk()
    app = RotaApp(root)
    root.mainloop()
