import sqlite3
from Encryption import decrypt

class Employee:
    def __init__(self, firstname, lastname, age, role, gender, pay, ability, key):
        # Initialize Employee object with provided attributes
        self.name = firstname.strip().capitalize() + ' ' + lastname.strip().capitalize()
        self.age = age
        self.role = role
        self.gender = gender
        self.key = key
        self.pay = pay
        self.ability = ability

def Serialize(dict,list,restaurantName):
    # Retrieve employee data from the database
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT firstname, lastname, age, role, gender, pay, ability, key FROM Employee_Data where restaurantName=?", (restaurantName, ))
    employees_data = cursor.fetchall()
    # Organize employee data as objects, stored in the dictionary by key
    for data in employees_data:
        firstname, lastname, age, role, gender, pay, ability, key= data
        list.append(key)
        employee = Employee(firstname, lastname, age, role, gender, pay, ability, decrypt(key))
        dict.setdefault(key, []).append(employee)
    conn.close()