import math
import random
from ObjectCreation import Serialize

# Initialize necessary variables
employees = {}
keys = []
Serialize(employees, keys, 'Aura')

covers = {}
assignedShifts = {}
# Assuming the employees dictionary and other necessary variables are initialized properly

roles = ['Manager', 'Waiter', 'Runner', 'Bartender', 'Barback']
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
shifts = ['08:00-13:20', '13:20-18:40', '18:40-00:00']

employees_shifts = {day: {} for day in days}

# Generate random covers for each day
for day in days:
    covers[day] = random.randint(0, 95)

# Iterate through each day
for day in days:
    # Reset employees_by_role dictionary for each day
    employees_by_role = {role: [] for role in roles}

    employeesNeeded = {role: 0 for role in roles}

    # Assuming employees is a dictionary with roles as keys and lists of employees as values
    for role, employee_list in employees.items():
        random.shuffle(employee_list)  # Shuffle the list of employees for each role
        for employee in employee_list:
            employees_by_role[employee.role].append(employee)

    # Calculate the number of employees needed for each role based on covers for the day
    if covers[day] > 25:
        employeesNeeded['Waiter'] += math.ceil(covers[day] / 25)
        if employeesNeeded['Waiter'] > 8:
            employeesNeeded['Waiter'] = 8

    if covers[day] > 50:
        employeesNeeded['Runner'] += math.ceil(covers[day] / 50)
        employeesNeeded['Barback'] = 1
        if employeesNeeded['Runner'] > 4:
            employeesNeeded['Runner'] = 4

    if covers[day] > 75:
        employeesNeeded['Manager'] += math.ceil(covers[day] / 75)
        employeesNeeded['Bartender'] += math.ceil(covers[day] / 75)
        if employeesNeeded['Manager'] > 3:
            employeesNeeded['Manager'] = 3
        if employeesNeeded['Bartender'] > 3:
            employeesNeeded['Bartender'] = 3
    else:
        employeesNeeded['Manager'] = 1
        employeesNeeded['Bartender'] = 1
        employeesNeeded['Waiter'] = 1

    # Assign shifts to employees
    assignedShifts[day] = {shift: {role: [] for role in roles} for shift in shifts}
    for shift in shifts:
        for role in roles:
            for _ in range(employeesNeeded[role]):
                if employees_by_role[role]:
                    employee = employees_by_role[role].pop(0)
                    assignedShifts[day][shift][role].append(employee)
                    if employee.name not in employees_shifts[day]:
                        employees_shifts[day][employee.name] = []
                    employees_shifts[day][employee.name].append((day, shift, role))

    # If there is no subsequent role to cover a shift, assign it to the previous employee who took a shift on that day
    for i, shift in enumerate(shifts[:-1]):
        for role in roles:
            if len(assignedShifts[day][shift][role]) > 0:
                for next_shift in shifts[i + 1:]:
                    if len(assignedShifts[day][next_shift][role]) == 0:
                        employee = assignedShifts[day][shift][role][0]
                        assignedShifts[day][next_shift][role].append(employee)
                        if employee.name not in employees_shifts[day]:
                            employees_shifts[day][employee.name] = []
                        employees_shifts[day][employee.name].append((day, next_shift, role))

# Combine consecutive shifts on the same day for each employee
for day, shifts_info in employees_shifts.items():
    for employee, shifts_assigned in shifts_info.items():
        combined_shifts = []
        current_shift = None
        for assigned_day, assigned_shift, assigned_role in shifts_assigned:
            if current_shift is None:
                current_shift = {'start_time': assigned_shift.split('-')[0], 'end_time': assigned_shift.split('-')[1]}
            else:
                if assigned_shift.split('-')[0] == current_shift['end_time']:
                    current_shift['end_time'] = assigned_shift.split('-')[1]
                else:
                    combined_shifts.append(current_shift)
                    current_shift = {'start_time': assigned_shift.split('-')[0], 'end_time': assigned_shift.split('-')[1]}
        combined_shifts.append(current_shift)
        shifts_info[employee] = combined_shifts

# Print combined shifts
for day, shifts_info in employees_shifts.items():
    print(f"For {day}:")
    for employee, combined_shifts in shifts_info.items():
        print(f"Employee: {employee}")
        for combined_shift in combined_shifts:
            print(f"\tShift(s): {combined_shift['start_time']}-{combined_shift['end_time']}")
