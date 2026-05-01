# ── SYSTEM LOGIC (CORE + API)

import tkinter as tk
from tkinter import ttk
from collections import deque

#process_api (JSON-backed)
from process_api import (
    memory_manager,
    spawn_process,
    kill_process,
    finish_process,
    clear_all,
    get_all, update_process
)

# scheduler
queue = deque()
auto_running = False


# ── SCHEDULER LOGIC
def run_step():
    quantum = 2
    if queue:
        p = queue.popleft()
        update_process(p.pid, state="Running")
        update_ui()

        def step():
            current = next(proc for proc in get_all() if proc.pid == p.pid)

            if current.remaining_time > quantum:
                update_process(
                    p.pid,
                    state="Ready",
                    remaining_time=current.remaining_time - quantum
                )
                queue.append(p)
            else:
                finish_process(p.pid)

            update_ui()

        root.after(300, step)
        return p
    return None


def auto_scheduler():
    global auto_running
    if auto_running:
        return
    auto_running = True

    def loop():
        global auto_running
        if queue:
            run_step()
            root.after(1000, loop)
        else:
            auto_running = False

    loop()


def clear_system():
    global auto_running, queue
    clear_all()
    queue.clear()
    auto_running = False


# ── GUI LAYER ─────────────────────────────────────────────────

root = tk.Tk()
root.title("OS Process Scheduler")
root.geometry("850x650")
root.configure(bg="#f5f7fb")

# ── MEMORY UI
top = tk.Frame(root, bg="#f5f7fb")
top.pack(pady=10)

tk.Label(top, text="Memory Map",
         bg="#f5f7fb", fg="#3b82f6",
         font=("Segoe UI", 12, "bold")).pack()

free_label = tk.Label(top, text="Free: 512 / 512",
                      bg="#f5f7fb", fg="#10b981")
free_label.pack()

mem_canvas = tk.Canvas(top, width=600, height=35, bg="white")
mem_canvas.pack(pady=5)

# ── TABLE
table_frame = tk.Frame(root)
table_frame.pack(expand=True, fill="both", padx=10)

tree = ttk.Treeview(
    table_frame,
    columns=("PID", "Name", "State", "Remaining"),
    show="headings"
)
for col in ("PID", "Name", "State", "Remaining"):
    tree.heading(col, text=col)
    tree.column(col, anchor="center")
tree.pack(expand=True, fill="both")

tree.tag_configure("Running", background="#dcfce7")
tree.tag_configure("Ready", background="#fef3c7")
tree.tag_configure("Finished", background="#e5e7eb")

# ── CONTROLS
bottom = tk.Frame(root)
bottom.pack(pady=10)

name_entry = tk.Entry(bottom)
name_entry.insert(0, "Process Name")
name_entry.pack(side="left", padx=5)


# ── UI UPDATE
def update_ui():
    process_list = get_all()
    memory_manager.rebuild_from_processes(process_list)
    for row in tree.get_children():
        tree.delete(row)

    for p in process_list:
        tree.insert("", "end",
                    values=(p.pid, p.name, p.state, p.remaining_time),
                    tags=(p.state,))

    memory_manager.draw_memory_map(mem_canvas, width=600, height=35)
    free_label.config(
        text=f"Free: {memory_manager.get_free_memory()} / {memory_manager.total_memory}"
    )


# ── AUTO REFRESH
def auto_refresh():
    update_ui()
    root.after(1500, auto_refresh)


# ── GUI ACTIONS
def ui_add():
    name = name_entry.get() or "Process"
    p = spawn_process(name, 6, 32)
    if p:
        queue.append(p)
    update_ui()


def ui_delete():
    selected = tree.selection()
    if selected:
        pid = int(tree.item(selected)["values"][0])
        kill_process(pid)
        for p in list(queue):
            if p.pid == pid:
                queue.remove(p)
        update_ui()


def ui_run():
    # Ready processes
    if not queue:
        for p in get_all():
            if p.state == "Ready":
                queue.append(p)
    run_step()


def ui_auto():
    if not queue:
        for p in get_all():
            if p.state == "Ready":
                queue.append(p)
    auto_scheduler()


def ui_clear():
    clear_system()
    update_ui()


# ── BUTTONS
tk.Button(bottom, text="Add", bg="#10b981", fg="white",
          command=ui_add).pack(side="left", padx=5)

tk.Button(bottom, text="Run", bg="#3b82f6", fg="white",
          command=ui_run).pack(side="left", padx=5)

tk.Button(bottom, text="Auto", bg="#f59e0b", fg="white",
          command=ui_auto).pack(side="left", padx=5)

tk.Button(bottom, text="Clear", bg="#ef4444", fg="white",
          command=ui_clear).pack(side="left", padx=5)

tk.Button(bottom, text="End", bg="#8b5cf6", fg="white",
          command=ui_delete).pack(side="left", padx=5)

# ── START
auto_refresh()
root.mainloop()
