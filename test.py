import math
import random
from ObjectCreation import Serialize

employees = {}
keys = []
Serialize(employees, keys, 'Aura')

roles = ['Manager', 'Waiter', 'Runner', 'Bartender', 'Barback']
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
covers = {day: random.randint(0, 375) for day in days}
shifts=['08:00-13:20', '13:20-18:40', '18:40-00:00']

for day in days:
    employeesNeeded = {role: 0 for role in roles}  # Initialize with all roles and 0 employees needed

    if covers[day] > 25:
        employeesNeeded['Waiter'] += math.ceil(covers[day] / 25)
        if math.ceil(covers[day] / 25) > 8:
            employeesNeeded['Waiter'] = 8

    if covers[day] > 50:
        employeesNeeded['Runner'] += math.ceil(covers[day] / 50)
        employeesNeeded['Barback'] = 1
        if employeesNeeded['Runner'] > 4:
            employeesNeeded['Runner'] = 4

    if covers[day] > 75:
        employeesNeeded['Manager'] += math.ceil(covers[day] / 75)
        employeesNeeded['Bartender'] += math.ceil(covers[day] / 75)
        if math.ceil(covers[day] / 75) > 3:
            employeesNeeded['Manager'] = 3
            employeesNeeded['Bartender'] = 3
    
    else:
        employeesNeeded['Manager'] = 1
        employeesNeeded['Bartender'] = 1
        employeesNeeded['Waiter'] = 1
    