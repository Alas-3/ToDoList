import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import re
from tkcalendar import DateEntry
from ttkthemes import ThemedStyle


def open_fullscreen_window(window):
    window.attributes('-fullscreen', True)

def create_table():
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT, first_name TEXT, last_name TEXT, email TEXT, age INTEGER, sex TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, start_date TEXT, end_date TEXT, priority TEXT, description TEXT, status TEXT, user_id INTEGER, FOREIGN KEY(user_id) REFERENCES users(rowid))''')
    conn.commit()
    conn.close()

def login(username_entry, password_entry):
    username = username_entry.get()
    password = password_entry.get()

    if username == "admin" and password == "password":
        messagebox.showinfo("Login Successful", "Welcome, Admin!")
        open_admin_dashboard()
        root.withdraw()  # Hide the root window
        # Clear the entry fields
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
    else:
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

def open_admin_dashboard():
    def logout_admin():
        admin_dashboard_window.destroy()  # Close the admin dashboard window
        root.deiconify()  # Show the login page

    def delete_user():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("No User Selected", "Please select a user.")
            return

        # Get the username to display in the confirmation message
        username = tree.item(selected_item, "values")[0]

        # Ask for confirmation
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the user '{username}'?")

        if confirm:
            conn = sqlite3.connect('todo.db')
            c = conn.cursor()
            c.execute("DELETE FROM users WHERE username=?", (username,))
            conn.commit()
            conn.close()

            # Remove the user from the treeview
            tree.delete(selected_item)

            messagebox.showinfo("User Deleted", f"User '{username}' has been deleted successfully.")

    admin_dashboard_window = tk.Toplevel(root)
    admin_dashboard_window.title("Admin Dashboard")
    admin_dashboard_window.attributes('-fullscreen', True)  # Set to fullscreen

    # Create a Treeview widget with only the defined columns displayed
    tree = ttk.Treeview(admin_dashboard_window, columns=("Username", "First Name", "Last Name", "Email", "Age", "Sex"), show="headings")
    tree.heading("Username", text="Username")
    tree.heading("First Name", text="First Name")
    tree.heading("Last Name", text="Last Name")
    tree.heading("Email", text="Email")
    tree.heading("Age", text="Age")
    tree.heading("Sex", text="Sex")
    tree.pack(expand=True, fill="both")

    # Fetch users from the database
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    conn.close()

    # Insert user information into the Treeview
    if users:
        for user in users:
            # Insert user information with correct column order
            tree.insert("", "end", values=(user[0], user[2], user[3], user[4], user[5], user[6]))
    else:
        messagebox.showinfo("No Users Found", "No users found in the database.")

    
    # Frame to contain the buttons
    button_frame = tk.Frame(admin_dashboard_window)
    button_frame.pack(pady=20)

    # Delete User Button
    delete_user_button = tk.Button(button_frame, text="Delete User", command=delete_user, font=("Helvetica", 12))
    delete_user_button.pack(side="left", padx=15)

    # Logout Button
    logout_button = tk.Button(button_frame, text="Logout", command=logout_admin, font=("Helvetica", 12))
    logout_button.pack(side="left", padx=15)

def open_task_list(user_id):
    def mark_as_completed():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("No Task Selected", "Please select a task.")
            return
        
        selected_task_id = tree.item(selected_item, "values")[0]
        
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute("UPDATE tasks SET status='Completed' WHERE id=?", (selected_task_id,))
        conn.commit()
        
        # Update the Treeview display
        tree.item(selected_item, values=(tree.item(selected_item, "values")[:-1] + ('Completed',)))
        
        conn.close()
        
        messagebox.showinfo("Task Status Updated", "Task has been marked as Completed.")

        # Refresh the treeview
        refresh_treeview()

    def delete_task():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("No Task Selected", "Please select a task.")
            return

        # Get the task title to display in the confirmation message
        task_title = tree.item(selected_item, "values")[1]

        # Ask for confirmation
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete this task '{task_title}'?")

        if confirm:
            selected_task_id = tree.item(selected_item, "values")[0]

            conn = sqlite3.connect('todo.db')
            c = conn.cursor()
            c.execute("DELETE FROM tasks WHERE id=?", (selected_task_id,))
            conn.commit()
            conn.close()

            # Remove the task from the treeview
            tree.delete(selected_item)

            messagebox.showinfo("Task Deleted", "Task has been deleted successfully.")

    def undo_completion():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("No Task Selected", "Please select a task.")
            return
        
        selected_task_id = tree.item(selected_item, "values")[0]
        
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute("UPDATE tasks SET status='Not Completed' WHERE id=?", (selected_task_id,))
        conn.commit()
        
        # Update the Treeview display
        tree.item(selected_item, values=(tree.item(selected_item, "values")[:-1] + ('Not Completed',)))
        
        conn.close()
        
        messagebox.showinfo("Task Status Updated", "Task completion has been undone.")

        # Refresh the treeview
        refresh_treeview()

    def refresh_treeview():
        # Clear existing items from the treeview
        for item in tree.get_children():
            tree.delete(item)

        # Fetch tasks from the database again and insert them into the treeview
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute("SELECT * FROM tasks WHERE user_id=?", (user_id,))
        tasks = c.fetchall()
        conn.close()

        if tasks:
            for task in tasks:
                tree.insert("", "end", values=task)  # Include the ID in the displayed task info
        else:
            messagebox.showinfo("No Tasks Found", "No tasks found for this user.")

    def back_to_main_app():
        task_list_window.destroy()  # Close the task list window
        open_main_app_page(user_id)  # Open the main app window again


    def sort_tasks(event=None):
        # Fetch tasks from the database again
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute("SELECT * FROM tasks WHERE user_id=?", (user_id,))
        tasks = c.fetchall()
        conn.close()

        sort_option = sort_var.get()
        if sort_option == "Priority":
            sorted_tasks = sorted(tasks, key=lambda x: ("Urgent", "High", "Medium", "Low").index(x[4]))
        elif sort_option == "End Date":
            sorted_tasks = sorted(tasks, key=lambda x: x[3])
        elif sort_option == "Status":
            sorted_tasks = sorted(tasks, key=lambda x: ("Not Completed", "Completed").index(x[6]))
        else:  # Default sorting
            sorted_tasks = tasks
        
        # Clear existing items from the treeview
        for item in tree.get_children():
            tree.delete(item)

        # Insert sorted tasks into the treeview
        if sorted_tasks:
            for task in sorted_tasks:
                tree.insert("", "end", values=task)  # Include the ID in the displayed task info
        else:
            messagebox.showinfo("No Tasks Found", "No tasks found for this user.")

    def display_full_description(event):
        selected_item = tree.selection()
        if not selected_item:
            return
        selected_task_id = tree.item(selected_item, "values")[0]

        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute("SELECT description FROM tasks WHERE id=?", (selected_task_id,))
        description = c.fetchone()[0]
        conn.close()

        messagebox.showinfo("Task Description", description)

    def on_double_click(event):
        display_full_description(event)


    task_list_window = tk.Toplevel(root)
    task_list_window.title("Task List")
    task_list_window.attributes('-fullscreen', True)  # Set to fullscreen

    # Center the task list content
    task_list_frame = tk.Frame(task_list_window)
    task_list_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    tree = ttk.Treeview(task_list_window, columns=("ID", "Title", "Start Date", "End Date", "Priority", "Description", "Status"), show="headings")
    tree.heading("ID", text="ID")  # New column for task ID
    tree.heading("Title", text="Title")
    tree.heading("Start Date", text="Start Date")
    tree.heading("End Date", text="End Date")
    tree.heading("Priority", text="Priority")
    tree.heading("Description", text="Description")
    tree.heading("Status", text="Status")

    tree.bind("<Double-1>", on_double_click)  # Double-click event binding

    tree.pack(expand=True, fill="both")

    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE user_id=?", (user_id,))
    tasks = c.fetchall()
    conn.close()

    if tasks:
        for task in tasks:
            tree.insert("", "end", values=task)  # Include the ID in the displayed task info
    else:
        messagebox.showinfo("No Tasks Found", "No tasks found for this user.")
    
    # Sort Option Dropdown
    sort_var = tk.StringVar()
    sort_var.set("Default")
    sort_option_menu = ttk.OptionMenu(task_list_window, sort_var, "Default", "Default", "Priority", "End Date", "Status", command=sort_tasks)
    sort_option_menu.pack(side="left", padx=10, pady=10)

    # Align buttons horizontally with space between them
    button_frame = tk.Frame(task_list_window)
    button_frame.pack(pady=20)

    # Back Button
    back_button = tk.Button(button_frame, text="Back", command=back_to_main_app, font=("Helvetica", 12))
    back_button.pack(side="left", padx=15)

    # Delete Task Button
    delete_task_button = tk.Button(button_frame, text="Delete Task", command=delete_task, font=("Helvetica", 12))
    delete_task_button.pack(side="left", padx=15)

    # Undo Completion Button
    undo_completion_button = tk.Button(button_frame, text="Undo Completion", command=undo_completion, font=("Helvetica", 12))
    undo_completion_button.pack(side="left", padx=15)

    # Mark as Completed Button
    mark_completed_button = tk.Button(button_frame, text="Mark as Completed", command=mark_as_completed, font=("Helvetica", 12))
    mark_completed_button.pack(side="left", padx=15)
    

def open_main_app_page(user_id):
    def add_task(user_id, title, start_date, end_date, priority, description, title_entry, start_date_entry, end_date_entry, description_entry):
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute("INSERT INTO tasks (title, start_date, end_date, priority, description, status, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)", (title, start_date, end_date, priority, description, "Not Completed", user_id))
        conn.commit()
        conn.close()
        messagebox.showinfo("Task Added", "Task has been added to the list.")

        # Clear entry fields after adding the task
        title_entry.delete(0, tk.END)
        start_date_entry.delete(0, tk.END)
        end_date_entry.delete(0, tk.END)
        description_entry.delete(0, tk.END)

    def show_tasks_and_close_main_app(main_app_window, user_id):
        main_app_window.destroy()  # Close the main app window
        open_task_list(user_id)  # Open the task list window

    main_app_window = tk.Toplevel(root)
    main_app_window.title("To-Do List App")
    main_app_window.attributes('-fullscreen', True)  # Set to fullscreen

    # Center the main app content
    main_app_frame = tk.Frame(main_app_window)
    main_app_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    # Labels
    tk.Label(main_app_frame, text="Title of the Task:", font=("Helvetica", 16)).grid(row=0, column=0, padx=10, pady=5, sticky="e")
    tk.Label(main_app_frame, text="Start Date:", font=("Helvetica", 16)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
    tk.Label(main_app_frame, text="End Date:", font=("Helvetica", 16)).grid(row=2, column=0, padx=10, pady=5, sticky="e")
    tk.Label(main_app_frame, text="Priority Level:", font=("Helvetica", 16)).grid(row=3, column=0, padx=10, pady=5, sticky="e")
    tk.Label(main_app_frame, text="Description:", font=("Helvetica", 16)).grid(row=4, column=0, padx=10, pady=5, sticky="e")

    # Entry Fields
    title_entry = tk.Entry(main_app_frame, font=("Helvetica", 14))
    title_entry.grid(row=0, column=1, padx=10, pady=5)

    # Start Date and End Date Entry Fields using DateEntry widget
    start_date_entry = DateEntry(main_app_frame, date_pattern='yyyy-mm-dd', font=("Helvetica", 14))
    start_date_entry.grid(row=1, column=1, padx=10, pady=5)

    end_date_entry = DateEntry(main_app_frame, date_pattern='yyyy-mm-dd', font=("Helvetica", 14))
    end_date_entry.grid(row=2, column=1, padx=10, pady=5)

    # Priority Radio Buttons
    priority_var = tk.StringVar(value="Urgent")
    tk.Radiobutton(main_app_frame, text="Urgent", variable=priority_var, value="Urgent", font=("Helvetica", 14)).grid(row=3, column=1, padx=(10, 0), pady=5, sticky="w")
    tk.Radiobutton(main_app_frame, text="High", variable=priority_var, value="High", font=("Helvetica", 14)).grid(row=3, column=1, padx=(10, 0), pady=5, sticky="w")
    tk.Radiobutton(main_app_frame, text="Medium", variable=priority_var, value="Medium", font=("Helvetica", 14)).grid(row=3, column=1, padx=(10, 0), pady=5)
    tk.Radiobutton(main_app_frame, text="Low", variable=priority_var, value="Low", font=("Helvetica", 14)).grid(row=3, column=1, padx=(10, 0), pady=5, sticky="e")

    description_entry = tk.Entry(main_app_frame, font=("Helvetica", 14))
    description_entry.grid(row=4, column=1, padx=10, pady=5)

    # Add to List Button
    add_button = tk.Button(main_app_frame, text="Add to List", command=lambda: add_task(user_id, title_entry.get(), start_date_entry.get(), end_date_entry.get(), priority_var.get(), description_entry.get(), title_entry, start_date_entry, end_date_entry, description_entry), font=("Helvetica", 16))
    add_button.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="we")

    # Show Tasks Button
    show_tasks_button = tk.Button(main_app_frame, text="Show Tasks", command=lambda: show_tasks_and_close_main_app(main_app_window, user_id), font=("Helvetica", 16))
    show_tasks_button.grid(row=6, column=0, columnspan=2, padx=10, pady=5, sticky="we")

    # Logout Button
    logout_button = tk.Button(main_app_frame, text="Logout", command=lambda: logout(main_app_window), font=("Helvetica", 16))
    logout_button.grid(row=7, column=0, columnspan=2, padx=10, pady=5, sticky="we")



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

    # Back to Login Button
    back_to_login_button = tk.Button(signup_window, text="Back to Login", command=lambda: back_to_login(signup_window))
    back_to_login_button.grid(row=8, column=0, columnspan=2, padx=10, pady=5, sticky="we")

    # Hide the login window (root)
    root.withdraw()

def back_to_login(window):
    window.destroy()
    root.deiconify()  # Show the root window (login page)

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
        # Clear the entry fields
        first_name_entry.delete(0, tk.END)
        last_name_entry.delete(0, tk.END)
        email_entry.delete(0, tk.END)
        age_entry.delete(0, tk.END)
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
    except sqlite3.IntegrityError:
        messagebox.showerror("Sign Up Failed", "Username already exists!")
    conn.close()

def close_root():
    root.destroy()

def logout(main_app_window):
    main_app_window.destroy()
    root.deiconify()  # Show the root window (login page)

# Create the main window (root)
root = tk.Tk()
root.title("WELCOME")

# Apply a themed style
style = ThemedStyle(root)
style.theme_use('adapta')

# Create database table if not exists
create_table()

# Get the screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# PanedWindow for signup and login sections
paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL)
paned_window.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # Center the PanedWindow
paned_window_width = 650  # Set the width of the PanedWindow
paned_window_height = 350  # Set the height of the PanedWindow
paned_window_x = (screen_width - paned_window_width) / 2
paned_window_y = (screen_height - paned_window_height) / 2
paned_window.config(width=paned_window_width, height=paned_window_height)
paned_window.grid_propagate(False)  # Disable resizing

# Signup Section
signup_frame = tk.Frame(paned_window)
paned_window.add(signup_frame)
tk.Label(signup_frame, text="Sign Up", font=("Helvetica", 16)).grid(row=0, column=0, columnspan=2, pady=10)
tk.Label(signup_frame, text="First Name:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
tk.Label(signup_frame, text="Last Name:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
tk.Label(signup_frame, text="Email Address:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
tk.Label(signup_frame, text="Age:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
tk.Label(signup_frame, text="Sex:").grid(row=5, column=0, padx=10, pady=5, sticky="e")
tk.Label(signup_frame, text="Username:").grid(row=6, column=0, padx=10, pady=5, sticky="e")
tk.Label(signup_frame, text="Password:").grid(row=7, column=0, padx=10, pady=5, sticky="e")

first_name_entry = tk.Entry(signup_frame)
first_name_entry.grid(row=1, column=1, padx=10, pady=5)
last_name_entry = tk.Entry(signup_frame)
last_name_entry.grid(row=2, column=1, padx=10, pady=5)
email_entry = tk.Entry(signup_frame)
email_entry.grid(row=3, column=1, padx=10, pady=5)
age_entry = tk.Entry(signup_frame)
age_entry.grid(row=4, column=1, padx=10, pady=5)

sex_var = tk.StringVar(value="Male")
tk.Radiobutton(signup_frame, text="Male", variable=sex_var, value="Male").grid(row=5, column=1, padx=10, pady=5, sticky="w")
tk.Radiobutton(signup_frame, text="Female", variable=sex_var, value="Female").grid(row=5, column=1, padx=10, pady=5, sticky="e")

username_entry = tk.Entry(signup_frame)
username_entry.grid(row=6, column=1, padx=10, pady=5)
password_entry = tk.Entry(signup_frame, show="*")
password_entry.grid(row=7, column=1, padx=10, pady=5)

signup_button = tk.Button(signup_frame, text="Sign Up", command=validate_signup)
signup_button.grid(row=8, column=0, columnspan=2, padx=10, pady=5, sticky="we")

# Vertical line between login and signup parts
vertical_line = tk.Canvas(paned_window, width=5, height=paned_window_height, bg="white", highlightthickness=0)
paned_window.add(vertical_line)

# Login Section
login_frame = tk.Frame(paned_window)
paned_window.add(login_frame)
tk.Label(login_frame, text="Login", font=("Helvetica", 16)).grid(row=0, column=0, columnspan=2, pady=10)
tk.Label(login_frame, text="Username:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
tk.Label(login_frame, text="Password:").grid(row=2, column=0, padx=10, pady=5, sticky="e")

username_entry_login = tk.Entry(login_frame, width=30)
username_entry_login.grid(row=1, column=1, padx=10, pady=5)
password_entry_login = tk.Entry(login_frame, show="*", width=30)
password_entry_login.grid(row=2, column=1, padx=10, pady=5)

login_button = tk.Button(login_frame, text="Login", command=lambda: login(username_entry_login, password_entry_login))
login_button.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="we")

# Draw vertical line
vertical_line.create_line(2, 0, 2, paned_window_height, fill="gray")

# Adjusting font sizes and padding for the input fields
font_size = 14
padding = 5
for entry in (first_name_entry, last_name_entry, email_entry, age_entry, username_entry, password_entry):
    entry.config(font=("Helvetica", font_size))
    entry.grid(padx=padding, pady=padding, sticky="we")

for button in (signup_button, login_button):
    button.config(font=("Helvetica", font_size))

open_fullscreen_window(root)
root.mainloop()
