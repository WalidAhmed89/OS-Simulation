from collections import deque
import tkinter as tk
from tkinter import ttk


class Process:
    def __init__(self, pid, burst_time):
        self.pid = pid
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.state = "Ready"


process_list = []
queue = deque()
pid_counter = 1
auto_running = False

# GUI
root = tk.Tk()
root.title("OS Process Scheduler")

# Center window
window_width = 700
window_height = 450
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

root.configure(bg="#1e1e1e")

# Frames
top_frame = tk.Frame(root, bg="#1e1e1e")
top_frame.pack(pady=10)

table_frame = tk.Frame(root, bg="#1e1e1e")
table_frame.pack(expand=True)

# Table Style
style = ttk.Style()
style.theme_use("default")

style.configure("Treeview",
                background="#2b2b2b",
                foreground="white",
                rowheight=25,
                fieldbackground="#2b2b2b")

style.configure("Treeview.Heading",
                background="#444",
                foreground="white",
                font=("Arial", 10, "bold"))

# Table
tree = ttk.Treeview(table_frame,
                    columns=("PID", "State", "Remaining"),
                    show="headings")

tree.heading("PID", text="PID")
tree.heading("State", text="State")
tree.heading("Remaining", text="Remaining Time")

tree.column("PID", anchor="center")
tree.column("State", anchor="center")
tree.column("Remaining", anchor="center")

tree.pack(expand=True)

# Colors
tree.tag_configure("Running", background="#00ff88")
tree.tag_configure("Ready", background="#ffaa00")
tree.tag_configure("Finished", background="#888888")


# Functions

def update_table():
    for row in tree.get_children():
        tree.delete(row)

    for p in process_list:
        tree.insert("", "end",
                    values=(p.pid, p.state, p.remaining_time),
                    tags=(p.state,))


def add_process():
    global pid_counter

    p = Process(pid_counter, 6)
    process_list.append(p)
    queue.append(p)

    pid_counter += 1
    update_table()


def run_scheduler():
    quantum = 2

    if queue:
        process = queue.popleft()
        process.state = "Running"
        update_table()

        def continue_execution():
            if process.remaining_time > quantum:
                process.remaining_time -= quantum
                process.state = "Ready"
                queue.append(process)
            else:
                process.remaining_time = 0
                process.state = "Finished"

            update_table()

        root.after(500, continue_execution)


def auto_run():
    global auto_running
    if auto_running:
        return

    auto_running = True

    def run():
        global auto_running
        if queue:
            run_scheduler()
            root.after(1000, run)
        else:
            auto_running = False

    run()


def clear_all():
    global pid_counter, auto_running
    process_list.clear()
    queue.clear()
    pid_counter = 1
    auto_running = False
    update_table()


def delete_process():
    selected = tree.selection()
    if selected:
        item = tree.item(selected)
        pid = item['values'][0]

        global process_list, queue

        process_list = [p for p in process_list if p.pid != pid]
        queue = deque([p for p in queue if p.pid != pid])

        update_table()


# Buttons

add_btn = tk.Button(top_frame, text="Add Process", command=add_process,
                    bg="#4CAF50", fg="white", width=12)

run_btn = tk.Button(top_frame, text="Run Step", command=run_scheduler,
                    bg="#2196F3", fg="white", width=12)

auto_btn = tk.Button(top_frame, text="Auto Run", command=auto_run,
                     bg="#FF9800", fg="white", width=12)

clear_btn = tk.Button(top_frame, text="Clear", command=clear_all,
                      bg="#f44336", fg="white", width=12)

delete_btn = tk.Button(top_frame, text="End Task", command=delete_process,
                       bg="#9C27B0", fg="white", width=12)

add_btn.grid(row=0, column=0, padx=5)
run_btn.grid(row=0, column=1, padx=5)
auto_btn.grid(row=0, column=2, padx=5)
clear_btn.grid(row=0, column=3, padx=5)
delete_btn.grid(row=0, column=4, padx=5)

root.mainloop()
