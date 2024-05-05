import tkinter as tk
from datetime import datetime, timedelta, date 
from ObjectCreation import Serialize
import sqlite3
import math
import io
from PIL import ImageGrab
import random

class RotaApp:
    def __init__(self, root, restaurant, shifts, days):
        # Initialize RotaApp object
        self.roles = ['Manager', 'Waiter', 'Runner', 'Bartender', 'Barback']                    
        self.restaurant = restaurant
        self.employees = {}
        self.keys = []
        self.shifts = shifts
        Serialize(self.employees, self.keys, self.restaurant)
        
        self.root = root
        self.root.title("Weekly Rota")
        self.days = days
    
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
        self.max_name_length = max(len(self.employees[emp_id][0].name) for emp_id in self.employees.keys())
        self.max_role_length = max(len(self.employees[emp_id][0].role) for emp_id in self.employees.keys())

    def day_labels(self):
        # Create labels for days
        for i, day in enumerate(self.days):
            tk.Label(self.root, text=day, width=10, relief=tk.RIDGE).grid(row=1, column=i + 1)

    def populate_table(self, employees_shifts):
        # Group employees by role
        employees_by_role = {role: [] for role in self.roles}
        for emp_id in self.employees.keys():
            employee = self.employees[emp_id][0]
            employees_by_role[employee.role].append(employee)

        # Populate timetable with employee data grouped by role
        for role, employees in employees_by_role.items():
            if employees != []:
                tk.Label(self.root, text=role, width=self.max_role_length, relief=tk.RIDGE).grid(row=self.row_index, column=0)
                self.row_index += 1
                for employee in employees:
                    tk.Label(self.root, text=employee.name, width=self.max_name_length, relief=tk.RIDGE).grid(row=self.row_index, column=0)
                    for j, day in enumerate(self.days):
                        shift_info = employees_shifts[day].get(employee.key)
                        if shift_info:
                            shift_found = False
                            for shift_tuple in shift_info:
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
        # Iterate through each day
        for day, shifts_info in employees_shifts.items():
            # Iterate through each employee's shifts
            for employee_id, shifts in shifts_info.items():
                combined_shifts = []
                current_shift_start = None
                current_shift_end = None
                # Sort shifts by start time
                shifts.sort(key=lambda x: x[1])

                for shift in shifts:
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
                        combined_shifts.append((day, f"{current_shift_start}-{current_shift_end}", shift[2]))
                        current_shift_start = shift_start
                        current_shift_end = shift_end
                
                # Add the last combined shift
                combined_shifts.append((day, f"{current_shift_start}-{current_shift_end}", shift[2]))

                # Update employee's shifts with the combined shifts
                employees_shifts[day][employee_id] = combined_shifts

        return employees_shifts


    def generate_shift_schedules(self):
        # Initialize necessary variables
        covers = {}
        assignedShifts = {day: {shift: {role: [] for role in self.roles} for shift in self.shifts[day]} for day in self.days}
        employees_shifts = {day: {} for day in self.days}
        employees_by_role = {role: [] for role in self.roles}
        for emp_id in self.employees.keys():
            employee = self.employees[emp_id][0]
            employees_by_role[employee.role].append(employee)

        # Calculate the total shift points needed for each role on each day
        total_shift_points = {day: {role: 0 for role in self.roles} for day in self.days}
        for day in self.days:
            if day != "Sunday":
                covers[day] = random.randint(25,75)
            else:
                covers[day] = random.randint(75,125)
            for role in self.roles:
                if role == 'Manager':
                    total_shift_points[day][role] = 1
                elif role == 'Bartender':
                    total_shift_points[day][role] = 1
                elif role == 'Waiter':
                    total_shift_points[day][role] = 1
                if covers[day]>25:
                    if role == 'Barback' and covers[day] > 25:
                        total_shift_points[day][role] = 1
                    if role == 'Runner':
                        total_shift_points[day][role] = max(1, min(math.ceil(covers[day] / 50), 4))

        # Assign shifts to employees
        for day in self.days:
            todayShifts=self.shifts[day]
            employees_needed = {role: total_shift_points[day][role] for role in self.roles}
            for role in self.roles:
                employeesAvailable = employees_by_role[role]
                random.shuffle(employeesAvailable)
                if employees_needed[role] > 0:
                    shifts_per_employee = [len(todayShifts) // len(employeesAvailable) + (1 if i < len(todayShifts) % len(employeesAvailable) else 0) for i in range(len(employeesAvailable))]
                    shift_index = 0
                    for employee, num_shifts in zip(employeesAvailable, shifts_per_employee):
                        for _ in range(num_shifts):
                            assigned_shift = todayShifts[shift_index]
                            assignedShifts[day][assigned_shift][role].append(employee)
                            if employee.key not in employees_shifts[day]:
                                employees_shifts[day][employee.key] = []
                            employees_shifts[day][employee.key].append((day, assigned_shift, role))
                            shift_index += 1
        employees_shifts = self.combine_shifts(employees_shifts)
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

        for day, shifts_info in employees_shifts.items():
            for employee_id, shifts in shifts_info.items():
                total_hours_worked = 0
                employee_name = self.employees[employee_id][0].name
                hourly_pay_rate = self.employees[employee_id][0].pay

                for shift in shifts:
                    shift_start, shift_end = shift[1].split('-')
                    start_hour, start_minute = map(int, shift_start.split(':'))
                    end_hour, end_minute = map(int, shift_end.split(':'))

                    if end_hour == 0:  # Handle shifts ending at midnight
                        end_hour = 24

                    if start_hour > end_hour:  # Adjust for shifts starting before midnight and ending after midnight
                        total_hours_worked += (24 - start_hour) + end_hour + (end_minute - start_minute) / 60
                    else:
                        total_hours_worked += end_hour - start_hour + (end_minute - start_minute) / 60

                if total_hours_worked < 0:
                    print(f"Error: Negative hours worked for employee {employee_id} on {day}")
                    continue  # Skip calculation for this employee

                weekly_wage = total_hours_worked * hourly_pay_rate

                # Accumulate total wage for the week for each employee
                if employee_id not in employee_wages:
                    employee_wages[employee_id] = 0
                employee_wages[employee_id] += weekly_wage

        # Output total weekly wages for each employee
        for employee_id, total_wage in employee_wages.items():
            employee_name = self.employees[employee_id][0].name
            wages_text += f"{employee_name}: £{total_wage:.2f}\n"
            total_wage_bill += total_wage

        wages_text += f"\nTotal Wage Bill: £{total_wage_bill:.2f}"
        # Extract the total wages amount from the wages_text
        total_wages = float(wages_text.split('Total Wage Bill: £')[-1].strip())

        # Retrieve the restaurant budget from the restaurant_data table
        self.cursor.execute("SELECT restaurantBudget FROM restaurant_data WHERE restaurantName = ?", (self.restaurant, ))
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

