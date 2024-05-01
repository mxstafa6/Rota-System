import tkinter as tk
from ObjectCreation import Serialize
import math
import random

class RotaApp:
    def __init__(self, root, restaurant):
        # Initialize RotaApp object
        self.roles = ['Manager', 'Waiter', 'Runner', 'Bartender', 'Barback']                    
        self.restaurant = restaurant
        self.employees = {}
        self.keys = []
        self.shifts = ['08:00-13:20', '13:20-18:40', '18:40-00:00']  # Add shifts attribute

        Serialize(self.employees, self.keys, self.restaurant)
        
        self.root = root
        self.root.title("Weekly Rota")
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        self.row_index = 1  # Initialize row index

        # Create the timetable GUI
        self.calculate_max()
        self.day_labels()
        employees_shifts = self.generate_shift_schedules()  # Store generated shift schedules
        self.populate_table(employees_shifts)  # Pass shift schedules to populate_table

    def calculate_max(self):
        # Determine maximum name and role lengths
        self.max_name_length = max(len(emp.name) for emp_list in self.employees.values() for emp in emp_list)
        self.max_role_length = max(len(emp.role) for emp_list in self.employees.values() for emp in emp_list)

    def day_labels(self):
        # Create labels for days
        for i, day in enumerate(self.days):
            tk.Label(self.root, text=day, width=10, relief=tk.RIDGE).grid(row=0, column=i + 1)

    def populate_table(self, employees_shifts):
        # Group employees by role
        employees_by_role = {role: [] for role in self.roles}
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
                    for j, day in enumerate(self.days):
                        shift_info = employees_shifts[day].get(employee.name)
                        if shift_info:
                            for shift in shift_info:
                                if shift['role'] == role:
                                    shift_time = f"{shift['start_time']}-{shift['end_time']}"
                                    tk.Label(self.root, text=shift_time, width=self.max_name_length, relief=tk.RIDGE).grid(row=self.row_index, column=j + 1)
                                    break
                            else:
                                tk.Label(self.root, text="OFF", width=self.max_name_length, relief=tk.RIDGE).grid(row=self.row_index, column=j + 1)
                        else:
                            tk.Label(self.root, text="OFF", width=self.max_name_length, relief=tk.RIDGE).grid(row=self.row_index, column=j + 1)
                    self.row_index += 1

                tk.Label(self.root, text="", width=10).grid(row=self.row_index, column=0)
                self.row_index += 1


    def generate_shift_schedules(self):
        # Initialize necessary variables
        covers = {day: random.randint(100, 450) for day in self.days}
        assignedShifts = {day: {shift: {role: [] for role in self.roles} for shift in self.shifts} for day in self.days}
        employees_shifts = {day: {} for day in self.days}

        # Iterate through each day
        for day in self.days:
            # Reset employees_by_role dictionary for each day
            employees_by_role = {role: [] for role in self.roles}
            employeesNeeded = {role: 0 for role in self.roles}
            total_shift_points = {role: 0 for role in self.roles}

            # Calculate the total shift points needed for each role on this day
            for role in self.roles:
                if covers[day] > 75:
                    if role == 'Manager':
                        total_shift_points[role] = min(math.ceil(covers[day] / 75), 3)
                    elif role == 'Bartender':
                        total_shift_points[role] = min(math.ceil(covers[day] / 50), 3)
                    elif role == 'Barback' and covers[day] > 25:
                        total_shift_points[role] = 1
                    elif role == 'Waiter':
                        waiters_needed = min(math.ceil(covers[day] / 25), 8)
                        total_shift_points[role] = max(1, waiters_needed)
                    elif role == 'Runner':
                        runners_needed = min(math.ceil(covers[day] / 50), 4)
                        total_shift_points[role] = max(1, runners_needed)
                else:
                    if role == 'Manager':
                        total_shift_points[role] = 1
                    elif role == 'Bartender':
                        total_shift_points[role] = min(math.ceil(covers[day] / 50), 3)
                    elif role == 'Barback' and covers[day] > 25:
                        total_shift_points[role] = 1
                    elif role == 'Waiter':
                        total_shift_points[role] = max(1, min(math.ceil(covers[day] / 25), 8))
                    elif role == 'Runner':
                        total_shift_points[role] = max(1, min(math.ceil(covers[day] / 50), 4))
            print(total_shift_points)
            # Assuming employees is a dictionary with roles as keys and lists of employees as values
            for role, employee_list in self.employees.items():
                random.shuffle(employee_list)  # Shuffle the list of employees for each role
                for employee in employee_list:
                    employees_by_role[employee.role].append(employee)

            # Calculate the number of employees needed for each role based on total shift points for the day
            for role in self.roles:
                if total_shift_points[role] > 0:
                    employeesNeeded[role] = math.ceil(total_shift_points[role] / len(self.shifts))

            # Assign shifts to employees and handle consecutive shifts
            for i, shift in enumerate(self.shifts):
                for role in self.roles:
                    random.shuffle(employees_by_role[role])
                    for _ in range(employeesNeeded[role]):
                        if employees_by_role[role]:
                            employee = employees_by_role[role].pop(0)

                            # Check if the number of employees assigned to the role for this shift exceeds required count
                            if len(assignedShifts[day][shift][role]) < employeesNeeded[role]:
                                assignedShifts[day][shift][role].append(employee)
                                if employee.name not in employees_shifts[day]:
                                    employees_shifts[day][employee.name] = []
                                employees_shifts[day][employee.name].append((day, shift, role))

                                # If there is no subsequent role to cover a shift, assign it to the previous employee who took a shift on that day
                                if i < len(self.shifts) - 1:
                                    next_shift = self.shifts[i + 1]
                                    if len(assignedShifts[day][next_shift][role]) == 0:
                                        assignedShifts[day][next_shift][role].append(employee)
                                        employees_shifts[day][employee.name].append((day, next_shift, role))

        # Combine consecutive shifts on the same day for each employee
        for day, shifts_info in employees_shifts.items():
            for employee, shifts_assigned in shifts_info.items():
                combined_shifts = []
                current_shift = None
                for assigned_day, assigned_shift, assigned_role in shifts_assigned:
                    if current_shift is None:
                        current_shift = {'start_time': assigned_shift.split('-')[0], 'end_time': assigned_shift.split('-')[1], 'role': assigned_role}
                    else:
                        if assigned_shift.split('-')[0] == current_shift['end_time']:
                            current_shift['end_time'] = assigned_shift.split('-')[1]
                        else:
                            combined_shifts.append(current_shift)
                            current_shift = {'start_time': assigned_shift.split('-')[0], 'end_time': assigned_shift.split('-')[1], 'role': assigned_role}
                combined_shifts.append(current_shift)
                shifts_info[employee] = combined_shifts

        return employees_shifts



if __name__ == "__main__":
    # Create Tkinter root window and start the event loop
    root = tk.Tk()
    app = RotaApp(root, 'Aura')
    root.mainloop()