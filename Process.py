from collections import deque
import tkinter as tk
from tkinter import ttk
from Memory import MemoryManager

memory_manager = MemoryManager(total_memory=512)

# ── Theme ─────────────────────────────
BG = "#f5f7fb"
CARD = "#ffffff"
BORDER = "#e2e8f0"
FG = "#1f2937"
ACCENT = "#3b82f6"
GREEN = "#10b981"
ORANGE = "#f59e0b"
RED = "#ef4444"
PURPLE = "#8b5cf6"

# ── Process ───────────────────────────
class Process:
    def __init__(self, pid, burst_time, memory_size=32):
        self.pid = pid
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.state = "Ready"
        self.memory_size = memory_size


process_list = []
queue = deque()
pid_counter = 1
auto_running = False

# ── ROOT ─────────────────────────────
root = tk.Tk()
root.title("OS Process Scheduler")
root.geometry("850x650")
root.configure(bg=BG)

# ── TOP: MEMORY MAP ─────────────────────────────
memory_frame = tk.Frame(root, bg=BG)
memory_frame.pack(pady=10, fill="x")

tk.Label(
    memory_frame,
    text="Memory Map",
    bg=BG,
    fg=ACCENT,
    font=("Segoe UI", 12, "bold")
).pack()

free_label = tk.Label(
    memory_frame,
    text="Free: 512 / 512",
    bg=BG,
    fg=GREEN,
    font=("Segoe UI", 10)
)
free_label.pack()

mem_canvas = tk.Canvas(
    memory_frame,
    width=600,
    height=35,
    bg="white",
    highlightthickness=1,
    highlightbackground=BORDER
)
mem_canvas.pack(pady=5)

# ── MIDDLE: TABLE ─────────────────────────────
table_frame = tk.Frame(root, bg=BG)
table_frame.pack(expand=True, fill="both", padx=15)

style = ttk.Style()
style.theme_use("default")

style.configure(
    "Treeview",
    background="white",
    foreground=FG,
    rowheight=28,
    fieldbackground="white",
    bordercolor=BORDER
)

style.configure(
    "Treeview.Heading",
    background=BG,
    foreground=ACCENT,
    font=("Segoe UI", 10, "bold")
)

tree = ttk.Treeview(
    table_frame,
    columns=("PID", "State", "Remaining"),
    show="headings"
)

tree.heading("PID", text="PID")
tree.heading("State", text="State")
tree.heading("Remaining", text="Remaining")

tree.column("PID", anchor="center", width=100)
tree.column("State", anchor="center", width=200)
tree.column("Remaining", anchor="center", width=200)

tree.pack(expand=True, fill="both")

tree.tag_configure("Running", background="#dcfce7")
tree.tag_configure("Ready", background="#fef3c7")
tree.tag_configure("Finished", background="#e5e7eb")

# ── BOTTOM: BUTTONS ─────────────────────────────
bottom = tk.Frame(root, bg=BG)
bottom.pack(pady=15)

def make_btn(text, color, cmd):
    return tk.Button(
        bottom,
        text=text,
        command=cmd,
        bg=color,
        fg="white",
        font=("Segoe UI", 10, "bold"),
        bd=0,
        cursor="hand2",
        width=12
    )

# ── FUNCTIONS ─────────────────────────────
def update_table():
    for row in tree.get_children():
        tree.delete(row)

    for p in process_list:
        tree.insert("", "end",
                    values=(p.pid, p.state, p.remaining_time),
                    tags=(p.state,))

    memory_manager.draw_memory_map(mem_canvas, width=600, height=35)
    free_label.config(
        text=f"Free: {memory_manager.get_free_memory()} / {memory_manager.total_memory}"
    )


def add_process():
    global pid_counter

    p = Process(pid_counter, 6, memory_size=32)

    address = memory_manager.allocate(p.pid, p.memory_size)
    if address is None:
        return

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

        def continue_exec():
            if process.remaining_time > quantum:
                process.remaining_time -= quantum
                process.state = "Ready"
                queue.append(process)
            else:
                process.remaining_time = 0
                process.state = "Finished"
                memory_manager.deallocate(process.pid)

            update_table()

        root.after(250, continue_exec)


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
    for p in process_list:
        memory_manager.deallocate(p.pid)

    process_list.clear()
    queue.clear()
    pid_counter = 1
    auto_running = False
    update_table()


def delete_process():
    selected = tree.selection()
    if selected:
        item = tree.item(selected)
        pid = item["values"][0]

        memory_manager.deallocate(pid)

        global process_list, queue
        process_list = [p for p in process_list if p.pid != pid]
        queue = deque([p for p in queue if p.pid != pid])

        update_table()

# ── BUTTONS ─────────────────────────────
make_btn("Add", GREEN, add_process).pack(side="left", padx=5)
make_btn("Run", ACCENT, run_scheduler).pack(side="left", padx=5)
make_btn("Auto", ORANGE, auto_run).pack(side="left", padx=5)
make_btn("Clear", RED, clear_all).pack(side="left", padx=5)
make_btn("End", PURPLE, delete_process).pack(side="left", padx=5)

root.mainloop()