import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import re

def create_table():
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT, first_name TEXT, last_name TEXT, email TEXT, age INTEGER, sex TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, start_date TEXT, end_date TEXT, priority TEXT, description TEXT, user_id INTEGER, FOREIGN KEY(user_id) REFERENCES users(rowid))''')
    conn.commit()
    conn.close()

def login():
    username = username_entry.get()
    password = password_entry.get()
    
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    result = c.fetchone()
    conn.close()
    
    if result:
        messagebox.showinfo("Login Successful", "Welcome, " + username + "!")
        open_main_app_page(result[0])  # Pass the user_id to the main app page
        root.withdraw()  # Hide the root window
        # Clear the entry fields
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

def open_task_list(user_id):
    task_list_window = tk.Toplevel(root)
    task_list_window.title("Task List")

    tree = ttk.Treeview(task_list_window, columns=("Title", "Start Date", "End Date", "Priority", "Description"), show="headings")
    tree.heading("Title", text="Title")
    tree.heading("Start Date", text="Start Date")
    tree.heading("End Date", text="End Date")
    tree.heading("Priority", text="Priority")
    tree.heading("Description", text="Description")
    tree.pack(expand=True, fill="both")

    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE user_id=?", (user_id,))
    tasks = c.fetchall()
    conn.close()

    if tasks:
        for task in tasks:
            tree.insert("", "end", values=task[1:])  # Exclude the ID from the displayed task info
    else:
        messagebox.showinfo("No Tasks Found", "No tasks found for this user.")

def open_main_app_page(user_id):
    main_app_window = tk.Toplevel(root)
    main_app_window.title("To-Do List App")

    # Labels
    tk.Label(main_app_window, text="Title of the Task:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    tk.Label(main_app_window, text="Start Date:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    tk.Label(main_app_window, text="End Date:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    tk.Label(main_app_window, text="Priority Level:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    tk.Label(main_app_window, text="Description:").grid(row=4, column=0, padx=10, pady=5, sticky="e")

    # Entry Fields
    title_entry = tk.Entry(main_app_window)
    title_entry.grid(row=0, column=1, padx=10, pady=5)
    start_date_entry = tk.Entry(main_app_window)
    start_date_entry.grid(row=1, column=1, padx=10, pady=5)
    end_date_entry = tk.Entry(main_app_window)
    end_date_entry.grid(row=2, column=1, padx=10, pady=5)

    # Priority Radio Buttons
    priority_var = tk.StringVar(value="Urgent")
    tk.Radiobutton(main_app_window, text="Urgent", variable=priority_var, value="Urgent").grid(row=3, column=1, padx=10, pady=5, sticky="w")
    tk.Radiobutton(main_app_window, text="High", variable=priority_var, value="High").grid(row=3, column=1, padx=10, pady=5, sticky="w")
    tk.Radiobutton(main_app_window, text="Medium", variable=priority_var, value="Medium").grid(row=3, column=1, padx=10, pady=5)
    tk.Radiobutton(main_app_window, text="Low", variable=priority_var, value="Low").grid(row=3, column=1, padx=10, pady=5, sticky="e")

    description_entry = tk.Entry(main_app_window)
    description_entry.grid(row=4, column=1, padx=10, pady=5)

    # Add to List Button
    add_button = tk.Button(main_app_window, text="Add to List", command=lambda: add_task(user_id, title_entry.get(), start_date_entry.get(), end_date_entry.get(), priority_var.get(), description_entry.get()))
    add_button.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="we")

    # Logout Button
    logout_button = tk.Button(main_app_window, text="Logout", command=lambda: logout(main_app_window))
    logout_button.grid(row=6, column=0, columnspan=2, padx=10, pady=5, sticky="we")

    # Show Tasks Button
    show_tasks_button = tk.Button(main_app_window, text="Show Tasks", command=lambda: open_task_list(user_id))
    show_tasks_button.grid(row=7, column=0, columnspan=2, padx=10, pady=5, sticky="we")

def add_task(user_id, title, start_date, end_date, priority, description):
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("INSERT INTO tasks (title, start_date, end_date, priority, description, user_id) VALUES (?, ?, ?, ?, ?, ?)", (title, start_date, end_date, priority, description, user_id))
    conn.commit()
    conn.close()
    messagebox.showinfo("Task Added", "Task has been added to the list.")

def signup():
    global signup_window
    signup_window = tk.Toplevel(root)
    signup_window.title("Sign Up")

    # Labels
    tk.Label(signup_window, text="First Name:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    tk.Label(signup_window, text="Last Name:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    tk.Label(signup_window, text="Email Address:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    tk.Label(signup_window, text="Age:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    tk.Label(signup_window, text="Sex:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
    tk.Label(signup_window, text="Username:").grid(row=5, column=0, padx=10, pady=5, sticky="e")
    tk.Label(signup_window, text="Password:").grid(row=6, column=0, padx=10, pady=5, sticky="e")

    # Entry Fields
    global first_name_entry, last_name_entry, email_entry, age_entry, sex_var, username_entry, password_entry
    first_name_entry = tk.Entry(signup_window)
    first_name_entry.grid(row=0, column=1, padx=10, pady=5)
    last_name_entry = tk.Entry(signup_window)
    last_name_entry.grid(row=1, column=1, padx=10, pady=5)
    email_entry = tk.Entry(signup_window)
    email_entry.grid(row=2, column=1, padx=10, pady=5)
    age_entry = tk.Entry(signup_window)
    age_entry.grid(row=3, column=1, padx=10, pady=5)
    
    # Sex Radio Buttons
    sex_var = tk.StringVar()
    sex_var.set("Male")
    tk.Radiobutton(signup_window, text="Male", variable=sex_var, value="Male").grid(row=4, column=1, padx=10, pady=5, sticky="w")
    tk.Radiobutton(signup_window, text="Female", variable=sex_var, value="Female").grid(row=4, column=1, padx=10, pady=5, sticky="e")
    
    username_entry = tk.Entry(signup_window)
    username_entry.grid(row=5, column=1, padx=10, pady=5)
    password_entry = tk.Entry(signup_window, show="*")
    password_entry.grid(row=6, column=1, padx=10, pady=5)

    # Signup Button
    signup_button = tk.Button(signup_window, text="Sign Up", command=validate_signup)
    signup_button.grid(row=7, column=0, columnspan=2, padx=10, pady=5, sticky="we")

def validate_signup():
    first_name = first_name_entry.get()
    last_name = last_name_entry.get()
    email = email_entry.get()
    age = age_entry.get()
    sex = sex_var.get()
    username = username_entry.get()
    password = password_entry.get()

    if not age.isdigit():
        messagebox.showerror("Invalid Age", "Age must be a number.")
        return
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        messagebox.showerror("Invalid Email", "Please enter a valid email address.")
        return
    
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, first_name, last_name, email, age, sex) VALUES (?, ?, ?, ?, ?, ?, ?)", (username, password, first_name, last_name, email, age, sex))
        conn.commit()
        messagebox.showinfo("Sign Up Successful", "Account created successfully!")
        signup_window.destroy()
    except sqlite3.IntegrityError:
        messagebox.showerror("Sign Up Failed", "Username already exists!")
    conn.close()

def logout(main_app_window):
    main_app_window.destroy()
    root.deiconify()  # Show the root window (login page)

root = tk.Tk()
root.title("To-Do List App")
create_table()

# Login Page
tk.Label(root, text="Username:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
tk.Label(root, text="Password:").grid(row=1, column=0, padx=10, pady=5, sticky="e")

username_entry = tk.Entry(root)
username_entry.grid(row=0, column=1, padx=10, pady=5)
password_entry = tk.Entry(root, show="*")
password_entry.grid(row=1, column=1, padx=10, pady=5)

login_button = tk.Button(root, text="Login", command=login)
login_button.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="we")

signup_button = tk.Button(root, text="Go to Signup Page", command=signup)
signup_button.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="we")

root.mainloop()
