import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime

# Function to connect to the SQLite database
def connect_db():
    conn = sqlite3.connect('todo_list.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                task_name TEXT NOT NULL,
                due_date DATE,
                priority TEXT,
                notes TEXT,
                completed BOOLEAN DEFAULT 0
                )''')
    conn.commit()
    return conn

# Function to add a new task
def add_task(conn, listbox, entry_name, entry_due_date, priority_combo, entry_notes):
    task_name = entry_name.get()
    due_date = entry_due_date.get()
    priority = priority_combo.get()
    notes = entry_notes.get("1.0", tk.END)
    
    conn.execute("INSERT INTO tasks (task_name, due_date, priority, notes) VALUES (?, ?, ?, ?)",
                 (task_name, due_date, priority, notes))
    conn.commit()
    messagebox.showinfo("Success", "Task added successfully!")
    
    # Refresh listbox and clear input fields
    view_tasks(conn, listbox)
    entry_name.delete(0, tk.END)
    entry_due_date.set_date(datetime.today())
    priority_combo.set("Medium")
    entry_notes.delete("1.0", tk.END)

# Function to view all tasks
def view_tasks(conn, listbox):
    listbox.delete(0, tk.END)
    cursor = conn.execute("SELECT * FROM tasks")
    for row in cursor:
        status = "Completed" if row[5] else "Not Completed"
        listbox.insert(tk.END, f"{row[0]}. {row[1]} {' '*(40-len(row[1]))} | {status}")

# Function to delete a task
def delete_task(conn, listbox, task_id):
    conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    messagebox.showinfo("Success", "Task deleted successfully!")
    view_tasks(conn, listbox)

# Function to edit a task
def edit_task(conn, listbox, task_id, task_name=None, due_date=None, priority=None, notes=None):
    updates = []
    if task_name:
        updates.append(("task_name", task_name))
    if due_date:
        updates.append(("due_date", due_date))
    if priority:
        updates.append(("priority", priority))
    if notes:
        updates.append(("notes", notes))
    
    update_query = ", ".join([f"{field} = ?" for field, _ in updates])
    values = [value for _, value in updates]
    values.append(task_id)
    
    conn.execute(f"UPDATE tasks SET {update_query} WHERE id=?", tuple(values))
    conn.commit()
    messagebox.showinfo("Success", "Task updated successfully!")
    view_tasks(conn, listbox)

# Function to mark a task as completed
def mark_task_completed(conn, listbox, task_id, details_window):
    conn.execute("UPDATE tasks SET completed=1 WHERE id=?", (task_id,))
    conn.commit()
    messagebox.showinfo("Success", "Task marked as completed!")
    view_tasks(conn, listbox)
    details_window.destroy()

# Function to mark a task as incomplete (undo completion)
def mark_task_incomplete(conn, listbox, task_id, details_window):
    conn.execute("UPDATE tasks SET completed=0 WHERE id=?", (task_id,))
    conn.commit()
    messagebox.showinfo("Success", "Task marked as incomplete!")
    view_tasks(conn, listbox)
    details_window.destroy()

# Function to display task details in a new window
def open_task_details_window(conn, listbox):
    selected_task = listbox.curselection()
    if selected_task:
        task_id = int(listbox.get(selected_task[0]).split('.')[0])
        cursor = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
        row = cursor.fetchone()
        if row:
            details_window = tk.Toplevel()
            details_window.title("Task Details")
            frame = tk.Frame(details_window)
            frame.pack(padx=10, pady=10)

            tk.Label(frame, text="Task Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            tk.Label(frame, text="Due Date:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
            tk.Label(frame, text="Priority:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
            tk.Label(frame, text="Notes:").grid(row=3, column=0, padx=5, pady=5, sticky="w")

            entry_name = tk.Entry(frame, width=50)
            entry_name.grid(row=0, column=1, padx=5, pady=5)
            entry_name.insert(tk.END, row[1])

            entry_due_date = tk.Entry(frame, width=20)
            entry_due_date.grid(row=1, column=1, padx=5, pady=5)
            entry_due_date.insert(tk.END, row[2])

            priority_values = ["High", "Medium", "Low"]
            entry_priority = ttk.Combobox(frame, values=priority_values, width=17)
            entry_priority.grid(row=2, column=1, padx=5, pady=5)
            entry_priority.set(row[3])

            entry_notes = tk.Text(frame, width=50, height=5, wrap="word")  # Enable word wrapping
            entry_notes.grid(row=3, column=1, padx=5, pady=5)
            entry_notes.insert(tk.END, row[4])

            # Add vertical scrollbar for the notes text entry
            scrollbar = tk.Scrollbar(frame, command=entry_notes.yview)
            scrollbar.grid(row=3, column=2, sticky='ns')
            entry_notes.config(yscrollcommand=scrollbar.set)

            tk.Button(frame, text="Edit Task", command=lambda: edit_task(conn, listbox, task_id, entry_name.get(), entry_due_date.get(), entry_priority.get(), entry_notes.get("1.0", tk.END))).grid(row=4, column=0, columnspan=2, padx=5, pady=5)
            tk.Button(frame, text="Done", command=details_window.destroy).grid(row=5, column=0, columnspan=2, padx=5, pady=5)
            if not row[5]:  # If the task is not completed
                tk.Button(frame, text="Mark Task as Completed", command=lambda: mark_task_completed(conn, listbox, task_id, details_window)).grid(row=6, column=0, columnspan=2, padx=5, pady=5)
            else:
                tk.Button(frame, text="Undo Completion", command=lambda: mark_task_incomplete(conn, listbox, task_id, details_window)).grid(row=6, column=0, columnspan=2, padx=5, pady=5)

# Function to create and run the app
def run_app():
    conn = connect_db()
    root = tk.Tk()
    root.title("To-Do List App")

    style = ttk.Style()
    style.theme_use("clam")  # Choose a ttk theme

    frame = ttk.Frame(root)
    frame.pack(padx=10, pady=10)

    # Entry widgets
    entry_name = ttk.Entry(frame, width=50)
    entry_name.grid(row=0, column=1, padx=5, pady=5)

    entry_due_date = DateEntry(frame, width=20, date_pattern="yyyy-mm-dd")
    entry_due_date.grid(row=1, column=1, padx=5, pady=5)

    priority_values = ["High", "Medium", "Low"]  # List of priority options
    priority_combo = ttk.Combobox(frame, values=priority_values, width=17)
    priority_combo.grid(row=2, column=1, padx=5, pady=5)
    priority_combo.set("Medium")  # Set default value

    entry_notes = tk.Text(frame, width=50, height=5, wrap="word")  # Enable word wrapping
    entry_notes.grid(row=3, column=1, padx=5, pady=5)

    # Label widgets
    tk.Label(frame, text="Task Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    tk.Label(frame, text="Due Date:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    tk.Label(frame, text="Priority:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    tk.Label(frame, text="Notes:").grid(row=3, column=0, padx=5, pady=5, sticky="e")

    # Listbox widget
    listbox = tk.Listbox(frame, width=70, height=15)
    listbox.grid(row=6, column=0, columnspan=2, padx=5, pady=5)
    listbox.bind("<<ListboxSelect>>", lambda event: open_task_details_window(conn, listbox))

    # Scrollbar widget
    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
    scrollbar.config(command=listbox.yview)
    scrollbar.grid(row=6, column=2, sticky="ns")

    listbox.config(yscrollcommand=scrollbar.set)

    # Buttons
    ttk.Button(frame, text="Add Task", command=lambda: add_task(conn, listbox, entry_name, entry_due_date, priority_combo, entry_notes)).grid(row=4, column=0, columnspan=2, padx=5, pady=5)
    ttk.Button(frame, text="View All Tasks", command=lambda: view_tasks(conn, listbox)).grid(row=7, column=0, padx=5, pady=5)
    ttk.Button(frame, text="Filter", command=lambda: filter_tasks(conn, listbox)).grid(row=7, column=1, padx=5, pady=5)

    root.mainloop()

# Function to filter tasks
def filter_tasks(conn, listbox):
    # Create a filter window
    filter_window = tk.Toplevel()
    filter_window.title("Filter Tasks")
    frame = tk.Frame(filter_window)
    frame.pack(padx=10, pady=10)

    # Priority filter
    priority_filter = ttk.Combobox(frame, values=["All", "High", "Medium", "Low"])
    priority_filter.grid(row=0, column=0, padx=5, pady=5)
    priority_filter.set("All")

    # Completion status filter
    completion_filter = ttk.Combobox(frame, values=["All", "Completed", "Not Completed"])
    completion_filter.grid(row=0, column=1, padx=5, pady=5)
    completion_filter.set("All")

    # Apply filter button
    ttk.Button(frame, text="Apply Filter", command=lambda: apply_filter(conn, listbox, priority_filter.get(), completion_filter.get())).grid(row=1, column=0, columnspan=2, padx=5, pady=5)
    # Close button
    ttk.Button(frame, text="Close", command=filter_window.destroy).grid(row=2, column=0, columnspan=2, padx=5, pady=5)

# Function to apply the selected filter
def apply_filter(conn, listbox, priority_filter, completion_filter):
    listbox.delete(0, tk.END)
    if priority_filter != "All" and completion_filter != "All":
        cursor = conn.execute("SELECT * FROM tasks WHERE priority=? AND completed=?", (priority_filter, completion_filter == "Completed"))
    elif priority_filter != "All":
        cursor = conn.execute("SELECT * FROM tasks WHERE priority=?", (priority_filter,))
    elif completion_filter != "All":
        cursor = conn.execute("SELECT * FROM tasks WHERE completed=?", (completion_filter == "Completed",))
    else:
        cursor = conn.execute("SELECT * FROM tasks")
    for row in cursor:
        status = "Completed" if row[5] else "Not Completed"
        listbox.insert(tk.END, f"{row[0]}. {row[1]} {' '*(40-len(row[1]))} | {status}")

if __name__ == "__main__":
    run_app()
