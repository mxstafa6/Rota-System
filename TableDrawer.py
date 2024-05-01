import tkinter as tk
from ObjectCreation import Serialize
import math
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

        # Create the timetable GUI
        self.calculate_max()
        self.day_labels()
        employees_shifts = self.generate_shift_schedules()  # Store generated shift schedules
        self.populate_table(employees_shifts)  # Pass shift schedules to populate_table


    def calculate_max(self):
        # Determine maximum name and role lengths
        self.max_name_length = max(len(self.employees[emp_id][0].name) for emp_id in self.employees.keys())
        self.max_role_length = max(len(self.employees[emp_id][0].role) for emp_id in self.employees.keys())

    def day_labels(self):
        # Create labels for days
        for i, day in enumerate(self.days):
            tk.Label(self.root, text=day, width=10, relief=tk.RIDGE).grid(row=0, column=i + 1)

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
                covers[day] = random.randint(0,75)
            else:
                covers[day] = random.randint(75,125)
            for role in self.roles:
                if role == 'Manager':
                    total_shift_points[day][role] = 1
                elif role == 'Bartender':
                    total_shift_points[day][role] = 1
                elif role == 'Waiter':
                    total_shift_points[day][role] = 1
                if covers[day]>50:
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
        self.calculate_budget(employees_shifts)
        return employees_shifts
    def calculate_budget(self, employees_shifts):
        total_budget = 0
        employee_pay_weekly = {}  # Dictionary to store weekly pay for each employee
        
        for day, shifts_info in employees_shifts.items():
            for employee_id, shifts in shifts_info.items():
                total_hours_worked = 0
                
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
                
                employee = self.employees.get(employee_id)
                if employee:
                    employee = employee[0]
                    if employee.pay < 0:
                        print(f"Error: Negative pay rate for employee {employee_id}")
                        continue  # Skip calculation for this employee
                    
                    weekly_pay = total_hours_worked * employee.pay
                    total_budget += weekly_pay
                    employee_pay_weekly[employee.name] = employee_pay_weekly.get(employee.name, 0) + weekly_pay
                else:
                    print(f"Error: Employee {employee_id} not found")
        
        if total_budget < 0:
            print("Warning: Total budget is negative.")
        
        print("Total Budget:", total_budget)
        print("Employee Pay Weekly:")
        for employee_name, weekly_pay in employee_pay_weekly.items():
            print(f"{employee_name}: ${weekly_pay:.2f}")