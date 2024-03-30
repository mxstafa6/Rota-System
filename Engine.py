import tkinter as tk

class TimetableApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weekly Timetable")

        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.hours = ["8:00 AM", "9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM", "6:00 PM", "7:00 PM"]

        self.create_timetable()

    def create_timetable(self):
        for i, day in enumerate(self.days):
            tk.Label(self.root, text=day, width=10, relief=tk.RIDGE).grid(row=0, column=i+1)
        
        for i, hour in enumerate(self.hours):
            tk.Label(self.root, text=hour, width=10, relief=tk.RIDGE).grid(row=i+1, column=0)
            
            for j in range(len(self.days)):
                entry = tk.Entry(self.root, width=10, relief=tk.SOLID)
                entry.grid(row=i+1, column=j+1)

if __name__ == "__main__":
    root = tk.Tk()
    app = TimetableApp(root)
    root.mainloop()