import sqlite3

class Employee:
    def __init__(self, firstname, lastname, age, role, gender):
        # Initialize Employee object with provided attributes
        self.firstname = firstname.strip()
        self.lastname = lastname.strip()
        self.age = age
        self.role = role
        self.gender = gender
# Retrieve employee data from the database
conn = sqlite3.connect('data.db')
cursor = conn.cursor()
cursor.execute("SELECT firstname, lastname, age, role, gender, key FROM Employee_Data")
employees_data = cursor.fetchall()

# Organize employee data as objects, stored in the dictionary by role
employees = {}
for data in employees_data:
    firstname, lastname, age, role, gender, key= data
    print(role)
    employee = Employee(firstname, lastname, age, role, gender)
    employees.setdefault(key, []).append(employee)

print(employees.items)
for key, employee_list in employees.items():
    print(f"Employees in key '{key}':")
    for employee in employee_list:
        print(f"{employee.firstname} {employee.lastname}: {employee.age} years old")
    print()  # Add an empty line for better readability

conn.close()