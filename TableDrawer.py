import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta, date
import io
import math
from PIL import ImageGrab # type: ignore
import random
from Engine import RestaurantInformationRetriever

class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if self.items:
            return self.items.pop()

    def peek(self):
        if self.items:
            return self.items[-1]

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

# Node class for the linked list
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

# Linked list class implementation
class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

    def remove(self, key):
        current = self.head
        previous = None
        while current and current.data._key != key:
            previous = current
            current = current.next
        if previous is None:
            self.head = current.next
        elif current:
            previous.next = current.next

    def display(self):
        elements = []
        current = self.head
        while current:
            elements.append(current.data._name)
            current = current.next
        return elements

# Base class for all types of employees
class Employee:
    def __init__(self, firstname, lastname, age, role, gender, pay, key):
        self._name = firstname.strip().capitalize() + ' ' + lastname.strip().capitalize()
        self._age = age
        self._role = role
        self._gender = gender
        self._pay = pay
        self._key = key

    def calculate_weekly_wage(self, hours_worked):
        return hours_worked * self._pay

# Derived class for Managers with a bonus calculation
class Manager(Employee):
    def __init__(self, firstname, lastname, age, role, gender, pay, key, bonus_rate):
        super().__init__(firstname, lastname, age, role, gender, pay, key)
        self._bonus_rate = bonus_rate

    def calculate_weekly_wage(self, hours_worked):
        base_wage = super().calculate_weekly_wage(hours_worked)
        bonus = base_wage * self._bonus_rate
        return base_wage + bonus

class EmployeeFactory:
    @staticmethod
    def create_employee(role, firstname, lastname, age, gender, pay, key):
        if role == "Manager":
            return Manager(firstname, lastname, age, role, gender, pay, key, bonus_rate=0.1)
        else:
            return Employee(firstname, lastname, age, role, gender, pay, key)

def Serialize(keys, restaurant_name):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT firstname, lastname, age, role, gender, pay, key FROM Employee_Data WHERE restaurantName=?", (restaurant_name,))
    employees_list = LinkedList()  # Create a new linked list
    for row in cursor.fetchall():
        firstname, lastname, age, role, gender, pay, key = row
        # Use the factory to create Employee or Manager
        employee = EmployeeFactory.create_employee(role, firstname, lastname, age, gender, pay, key)
        employees_list.append(employee)  # Append the employee to the linked list
        keys.append(key)
    conn.close()
    return employees_list

class RotaApp:
    def __init__(self, root,  restaurant_name):
        # Initialize RotaApp object
        self.roles = ['Manager', 'Waiter', 'Runner', 'Bartender', 'Barback']   
        self.restaurant_info = RestaurantInformationRetriever(restaurant_name)      
        self.restaurant = self.restaurant_info.restaurant_name
        self.employees = LinkedList()
        self.keys = []
        self.shifts = self.restaurant_info.shifts
        self.employees = Serialize(self.keys, self.restaurant)
        
        self.root = root
        self.root.title("Weekly Rota")
        self.days = self.restaurant_info.days
    
        self.row_index = 1  # Initialize row index

        # Connect to the database
        self.conn = sqlite3.connect('data.db')
        self.cursor = self.conn.cursor()
         # Calculate the first day of the current week
        today = datetime.now()
        self.first_day_of_week = today - timedelta(days=today.weekday())

        # Add label for the week commencing
        tk.Label(root, text=f"Week Commencing: {self.first_day_of_week.strftime('%d-%m-%Y')}").grid(row=0, columnspan=len(self.days) + 1)
        # Create the timetable GUI
        self.calculate_max()
        self.day_labels()
        self.employees_shifts = self.generate_shift_schedules()  # Store generated shift schedules
        self.populate_table(self.employees_shifts)  # Pass shift schedules to populate_table

        # Add Save Schedule button
        save_button = tk.Button(root, text="Save Schedule", command=self.save_schedule)
        save_button.grid(row=self.row_index, column=0, pady=10, padx=5)

        # Add View Wages button
        view_wages_button = tk.Button(root, text="View Wages", command=self.view_wages)
        view_wages_button.grid(row=self.row_index, column=1, pady=10, padx=5)

    def calculate_max(self):
        # Determine maximum name and role lengths
        max_name_length = 0
        max_role_length = 0
        current = self.employees.head
        while current:
            max_name_length = max(max_name_length, len(current.data._name))
            max_role_length = max(max_role_length, len(current.data._role))
            current = current.next
        self.max_name_length = max_name_length
        self.max_role_length = max_role_length

    def day_labels(self):
        # Create a stack to manage the day labels
        day_label_stack = Stack()
        for i, day in enumerate(self.days):
            label = tk.Label(self.root, text=day, width=10, relief=tk.RIDGE)
            label.grid(row=1, column=i + 1)
            day_label_stack.push(label) # Push the label onto the stack

        while not day_label_stack.is_empty():
            label = day_label_stack.pop()  # Pop the label from the stack
    def populate_table(self, employees_shifts):
        # Group employees by role
        employees_by_role = {role: [] for role in self.roles}
        employee_names = self.employees.display()
        for employee_name in employee_names:
            employee = self.employees.head
            while employee:
                if employee.data._name == employee_name:
                    employees_by_role[employee.data._role].append(employee.data)
                    break
                employee = employee.next

        # Populate timetable with employee data grouped by role
        for role, employees in employees_by_role.items():
            if employees != []:
                tk.Label(self.root, text=role, width=self.max_role_length, relief=tk.RIDGE).grid(row=self.row_index, column=0)
                self.row_index += 1
                for employee in employees:
                    tk.Label(self.root, text=employee._name, width=self.max_name_length, relief=tk.RIDGE).grid(row=self.row_index, column=0)
                    for j, day in enumerate(self.days):
                        shift_info = employees_shifts[self.keys.index(employee._key)][j]
                        if shift_info:
                            shift_found = False
                            for shift_tuple in shift_info[self.roles.index(role)]:
                                shift_day, shift_time, shift_role = shift_tuple
                                if shift_role == role:
                                    shift_found = True
                                    shift_time = f"{shift_time.split('-')[0]}-{shift_time.split('-')[1]}"  # Adjust the format if needed
                                    tk.Label(self.root, text=shift_time, width=self.max_name_length, relief=tk.RIDGE).grid(row=self.row_index, column=j + 1)
                                    break
                            if not shift_found:
                                tk.Label(self.root, text="OFF", width=self.max_name_length, relief=tk.RIDGE).grid(row=self.row_index, column=j + 1)
                        else:
                            tk.Label(self.root, text="OFF", width=self.max_name_length, relief=tk.RIDGE).grid(row=self.row_index, column=j + 1)

                    self.row_index += 1

                tk.Label(self.root, text="", width=10).grid(row=self.row_index, column=0)
                self.row_index += 1

    def view_wages(self):
        # Create a new window to display wages
        wages_window = tk.Toplevel(self.root)
        wages_window.title("Wages")

        # Retrieve the wage bill text
        wages_text = self.calculate_wages_text(self.employees_shifts)

        # Create a text widget to display the combined wage bill and budget status
        text_widget = tk.Text(wages_window, wrap='word', height=20, width=50)
        text_widget.pack(expand=True, fill='both')

        # Insert the combined wages text into the text widget
        text_widget.insert('1.0', wages_text)

        # Make the text widget read-only
        text_widget.config(state='disabled')

        return wages_text

    def combine_shifts(self, employees_shifts):
        # Iterate through each employee
        for employee_shifts in employees_shifts:
            # Iterate through each day
            for day_shifts in employee_shifts:
                # Iterate through each role
                for role_shifts in day_shifts:
                    combined_shifts = []
                    current_shift_start = None
                    current_shift_end = None
                    # Sort shifts by start time
                    role_shifts.sort(key=lambda x: x[1])

                    for shift in role_shifts:
                        shift_start, shift_end = shift[1].split('-')
                        # If no current shift, set it as the current shift
                        if current_shift_start is None:
                            current_shift_start = shift_start
                            current_shift_end = shift_end
                        # If consecutive shift found, update the end time of the current shift
                        elif shift_start == current_shift_end:
                            current_shift_end = shift_end
                        # If not consecutive, add the current shift and start a new one
                        else:
                            combined_shifts.append((shift[0], f"{current_shift_start}-{current_shift_end}", shift[2]))
                            current_shift_start = shift_start
                            current_shift_end = shift_end

                    # Add the last combined shift
                    combined_shifts.append((shift[0], f"{current_shift_start}-{current_shift_end}", shift[2]))

                    # Update employee's shifts with the combined shifts
                    day_shifts[day_shifts.index(role_shifts)] = combined_shifts

        return employees_shifts

    def generate_shift_schedules(self):
        # Initialize necessary variables
        covers = {}
        assignedShifts = [[[] for _ in range(len(self.roles))] for _ in range(len(self.days))]
        employees_shifts = [[[[] for _ in range(len(self.roles))] for _ in range(len(self.days))] for _ in range(len(self.keys))]
        employees_by_role = {role: [] for role in self.roles}
        employee_names = self.employees.display()
        for employee_name in employee_names:
            employee = self.employees.head
            while employee:
                if employee.data._name == employee_name:
                    employees_by_role[employee.data._role].append(employee.data)
                    break
                employee = employee.next

        # Calculate the total shift points needed for each role on each day
        total_shift_points = {day: {role: 0 for role in self.roles} for day in self.days}
        for day in self.days:
            if day != "Sunday":
                covers[day] = random.randint(25, 75)
            else:
                covers[day] = random.randint(75, 125)
            for role in self.roles:
                if role == 'Manager':
                    total_shift_points[day][role] = 1
                elif role == 'Bartender':
                    total_shift_points[day][role] = 1
                elif role == 'Waiter':
                    total_shift_points[day][role] = 1
                if covers[day] > 25:
                    if role == 'Barback' and covers[day] > 25:
                        total_shift_points[day][role] = 1
                    if role == 'Runner':
                        total_shift_points[day][role] = max(1, min(math.ceil(covers[day] / 50), 4))

        # Assign shifts to employees
        for day_index, day in enumerate(self.days):
            todayShifts = self.shifts[day]
            employees_needed = {role: total_shift_points[day][role] for role in self.roles}
            for role_index, role in enumerate(self.roles):
                employeesAvailable = employees_by_role[role]
                random.shuffle(employeesAvailable)
                if employees_needed[role] > 0:
                    shifts_per_employee = [len(todayShifts) // len(employeesAvailable) + (1 if i < len(todayShifts) % len(employeesAvailable) else 0) for i in range(len(employeesAvailable))]
                    shift_index = 0
                    for employee_index, employee in enumerate(employeesAvailable):
                        for num_shifts in shifts_per_employee[employee_index:employee_index+1]:
                            for _ in range(num_shifts):
                                assigned_shift = todayShifts[shift_index]
                                assignedShifts[day_index][role_index].append(employee)
                                employees_shifts[self.keys.index(employee._key)][day_index][role_index].append((day, assigned_shift, role))
                                shift_index += 1
        return employees_shifts

    def save_schedule(self):
        # Get the dimensions of the GUI window
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()

        # Get the position of the GUI window relative to the screen
        window_x = self.root.winfo_rootx()
        window_y = self.root.winfo_rooty()

        # Calculate the bounding box for the screenshot
        bbox = (window_x, window_y, window_x + window_width, window_y + window_height - 40)

        # Grab the screenshot of the entire GUI window
        screenshot = ImageGrab.grab(bbox=bbox)

        # Convert image to binary data
        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        # Get the first day of the week
        today = date.today()
        first_day_of_week = today - timedelta(days=today.weekday())

        # Convert first day of the week to string in the format "dd/mm/yyyy"
        first_day_of_week_str = first_day_of_week.strftime('%d-%m-%Y')

        # Update 'currentRota' column with the rota PNG
        self.cursor.execute(f"UPDATE current_data SET currentRota = ? WHERE restaurantName = ?", (img_byte_arr, self.restaurant))

        # Save wages text as a text file
        wages_text = self.calculate_wages_text(self.employees_shifts)

        # Update 'currentWages' column with the wage text file path
        self.cursor.execute(f"UPDATE current_data SET currentWages = ? WHERE restaurantName = ?", (wages_text, self.restaurant))

        self.conn.commit()

        print("Schedule saved to the database.")

    def calculate_wages_text(self, employees_shifts):
        wages_text = "Weekly Wages:\n"
        total_wage_bill = 0
        employee_wages = {}
        employee_names = self.employees.display()

        # Calculate the average hourly pay
        self.cursor.execute("SELECT AVG(pay) AS 'Average Hourly Pay' FROM Employee_Data GROUP BY restaurantName;")
        result = self.cursor.fetchone()
        if result:
            average_hourly_pay = result[0]
        else:
            average_hourly_pay = 0.0

        for employee_index, employee_shifts in enumerate(employees_shifts):
            employee_name = employee_names[employee_index]
            employee = self.employees.head
            while employee:
                if employee.data._name == employee_name:
                    employee_id = employee.data._key
                    total_hours_worked = 0
                    hourly_pay_rate = employee.data._pay

                    for day_shifts in employee_shifts:
                        for role_shifts in day_shifts:
                            for shift in role_shifts:
                                shift_day, shift_time, shift_role = shift
                                shift_start, shift_end = shift_time.split('-')
                                start_hour, start_minute = map(int, shift_start.split(':'))
                                end_hour, end_minute = map(int, shift_end.split(':'))

                                if end_hour == 0:  # Handle shifts ending at midnight
                                    end_hour = 24

                                if start_hour > end_hour:  # Adjust for shifts starting before midnight and ending after midnight
                                    total_hours_worked += (24 - start_hour) + end_hour + (end_minute - start_minute) / 60
                                else:
                                    total_hours_worked += end_hour - start_hour + (end_minute - start_minute) / 60

                    if total_hours_worked < 0:
                        print(f"Error: Negative hours worked for employee {employee_id}")
                        continue  # Skip calculation for this employee

                    weekly_wage = employee.data.calculate_weekly_wage(total_hours_worked)

                    # Accumulate total wage for the week for each employee
                    if employee_id not in employee_wages:
                        employee_wages[employee_id] = 0
                    employee_wages[employee_id] += weekly_wage

                employee = employee.next

        # Output total weekly wages for each employee
        for employee_id, total_wage in employee_wages.items():
            employee = self.employees.head
            while employee:
                if employee.data._key == employee_id:
                    employee_name = employee.data._name
                    break
                employee = employee.next
            wages_text += f"{employee_name}: £{total_wage:.2f}\n"
            total_wage_bill += total_wage

        wages_text += f"\nTotal Wage Bill: £{total_wage_bill:.2f}"
        wages_text += f"\nAverage Hourly Pay: £{average_hourly_pay:.2f}"

        # Extract the total wages amount from the wages_text
        total_wages = float(wages_text.split('Total Wage Bill: £')[-1].split('\n')[0])

        # Retrieve the restaurant budget from the restaurant_data table
        self.cursor.execute("SELECT restaurantBudget FROM restaurant_data WHERE restaurantName = ?", (self.restaurant,))
        budget_data = self.cursor.fetchone()
        if budget_data:
            restaurant_budget = float(budget_data[0])

            # Calculate the difference between the total wages and the restaurant budget
            budget_difference = total_wages - restaurant_budget

            # Determine the budget status and the amount by which it is over or within the budget
            if budget_difference > 0:
                budget_status = "Over Budget by £{:.2f}".format(budget_difference)
            else:
                budget_status = "Within Budget by £{:.2f}".format(abs(budget_difference))

            # Combine the wages text and the budget status into one string
            wages_text = "{}\n\nBudget Status: {}".format(wages_text, budget_status)

        return wages_text
def main(permissions, restaurant_name):
    try:
        if permissions < 1:
            messagebox.showerror("Permission Denied", "You need higher permissions to create a rota.")
            return
        root = tk.Tk()
        RotaApp(root, restaurant_name)
        root.mainloop()
    except:
        messagebox.showerror("Error", "Not enough data.")