from tkinter import *
root = Tk()    
users = ['Anne', 'Bea', 'Chris', 'Bob', 'Helen']
selected_users=[]
for x in range(len(users)):
    l = Checkbutton(root, text=users[x], variable=users[x],command=lambda x=users[x]:selected_users.append(x))
    l.pack(anchor = 'w')
Button(root,text="Ok",command=lambda: [print(selected_users),root.destroy()]).pack()
root.mainloop()