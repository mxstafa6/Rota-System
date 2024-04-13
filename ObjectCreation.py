import sqlite3

class Employee:
    def __init__(self, firstname, lastname, age, role, gender):
        # Initialize Employee object with provided attributes
        self.firstname = firstname.strip().capitalize()
        self.lastname = lastname.strip().capitalize()
        self.age = age
        self.role = role
        self.gender = gender

def Serialize(dict,list):
    # Retrieve employee data from the database
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT firstname, lastname, age, role, gender, key FROM Employee_Data")
    employees_data = cursor.fetchall()
    # Organize employee data as objects, stored in the dictionary by key
    for data in employees_data:
        firstname, lastname, age, role, gender, key= data
        list.append(key)
        employee = Employee(firstname, lastname, age, role, gender)
        dict.setdefault(key, []).append(employee)
    conn.close()

