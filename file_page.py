import tkinter as tk
from tkinter import messagebox

# ── Global Storage ──
files = {}
file_window_instance = None


def open_file_page(login_window=None):
    global files, file_window_instance

    # ── Prevent duplicate window ──
    if file_window_instance is not None:
        try:
            file_window_instance.lift()
            file_window_instance.focus_force()
            return
        except:
            file_window_instance = None

    # ── Theme ──
    BG = "#f5f7fb"
    FG = "#1f2937"
    ACCENT = "#3b82f6"
    SUCCESS = "#10b981"
    DANGER = "#ef4444"
    TITLE_BLUE = "#2563eb"

    FONT_TITLE = ("Segoe UI", 14, "bold")
    FONT_MAIN = ("Courier", 10)

    file_window = tk.Toplevel()
    file_window_instance = file_window

    file_window.title("Frosted OS - File System")
    file_window.geometry("850x650")
    file_window.configure(bg=BG)
    file_window.attributes("-alpha", 0.0)

    if login_window:
        try:
            login_window.withdraw()
        except:
            pass

    # ── Fade in ──
    def fade_in(a=0):
        if a < 1:
            file_window.attributes("-alpha", a)
            file_window.after(15, lambda: fade_in(a + 0.05))

    fade_in()

    # ── CLOSE ──
    def close_window():
        global file_window_instance
        file_window_instance = None

        if login_window:
            try:
                login_window.deiconify()
            except:
                pass

        file_window.destroy()

    file_window.protocol("WM_DELETE_WINDOW", close_window)

    # ── HEADER ──
    header = tk.Frame(file_window, bg=BG)
    header.pack(fill="x", pady=10)

    tk.Frame(header, bg=BG).pack(side="left", expand=True)

    tk.Label(
        header,
        text="File System",
        font=("Segoe UI", 16, "bold"),
        bg=BG,
        fg=TITLE_BLUE
    ).pack(side="left")

    tk.Frame(header, bg=BG).pack(side="left", expand=True)

    tk.Label(
        header,
        text="ADMIN",
        font=("Segoe UI", 10, "bold"),
        bg=BG,
        fg=SUCCESS
    ).place(relx=0.95, rely=0.5, anchor="e")

    # ── MAIN ──
    main = tk.Frame(file_window, bg=BG)
    main.pack(fill="both", expand=True, padx=20)

    # ── LEFT ──
    left = tk.Frame(main, bg=BG)
    left.pack(side="left", fill="both", expand=True)

    tk.Label(
        left,
        text="Explorer",
        font=("Segoe UI", 12, "bold"),
        bg=BG,
        fg=TITLE_BLUE
    ).pack(anchor="w")

    listbox = tk.Listbox(
        left,
        bg="white",
        fg=FG,
        font=FONT_MAIN,
        selectbackground=ACCENT,
        bd=0,
        highlightthickness=0
    )
    listbox.pack(fill="both", expand=True, pady=10)

    tk.Label(left, text="📄 File Name", bg=BG, fg=FG).pack(anchor="w")
    entry_name = tk.Entry(left, font=FONT_MAIN, bg="white", fg=FG, bd=0)
    entry_name.pack(fill="x", pady=3)

    tk.Label(left, text="✏️ Content", bg=BG, fg=FG).pack(anchor="w")
    entry_content = tk.Entry(left, font=FONT_MAIN, bg="white", fg=FG, bd=0)
    entry_content.pack(fill="x", pady=3)

    btns = tk.Frame(left, bg=BG)
    btns.pack(fill="x", pady=10)

    # ── FILE LOGIC ──
    def update_list():
        listbox.delete(0, tk.END)
        for f in files:
            listbox.insert(tk.END, f)

    def create_file():
        name = entry_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Enter file name", parent=file_window)
            return
        if name in files:
            messagebox.showerror("Error", "File exists!", parent=file_window)
            return
        files[name] = {"content": ""}
        update_list()

    def delete_file():
        sel = listbox.curselection()
        if sel:
            files.pop(listbox.get(sel[0]), None)
            update_list()

    def read_file():
        sel = listbox.curselection()
        if sel:
            name = listbox.get(sel[0])
            messagebox.showinfo("Content", files[name]["content"] or "(empty)")

    def write_file():
        sel = listbox.curselection()
        if sel:
            name = listbox.get(sel[0])
            files[name]["content"] += entry_content.get() + "\n"
            entry_content.delete(0, tk.END)

    def make_btn(text, color, cmd):
        tk.Button(
            btns,
            text=text,
            command=cmd,
            bg=BG,
            fg=color,
            font=("Segoe UI", 10, "bold"),
            bd=0,
            cursor="hand2"
        ).pack(side="left", expand=True, fill="x", padx=5)

    make_btn("➕ Create", SUCCESS, create_file)
    make_btn("✏️ Write", ACCENT, write_file)
    make_btn("👁 Read", "#8b5cf6", read_file)
    make_btn("🗑 Delete", DANGER, delete_file)

    # ── TERMINAL ──
    right = tk.Frame(main, bg=BG)
    right.pack(side="right", fill="both", expand=True, padx=(20, 0))

    tk.Label(
        right,
        text="Terminal",
        font=("Segoe UI", 12, "bold"),
        bg=BG,
        fg=TITLE_BLUE
    ).pack(anchor="w")

    output = tk.Text(
        right,
        bg="#0b1220",
        fg="#10b981",
        font=("Courier", 10),
        bd=0,
        insertbackground="#10b981"
    )
    output.pack(fill="both", expand=True, pady=10)

    def write(text):
        output.insert(tk.END, text)
        output.see(tk.END)

    def run_command(cmd):
        cmd = cmd.strip()
        write("\n")

        if cmd == "help":
            write("help | clear | ls | cat | rm\n")

        elif cmd == "clear":
            output.delete("1.0", tk.END)

        elif cmd == "ls":
            write(" ".join(files.keys()) + "\n")

        elif cmd.startswith("cat "):
            name = cmd[4:]
            write(files.get(name, {}).get("content", "File not found") + "\n")

        elif cmd.startswith("rm "):
            name = cmd[3:]
            if name in files:
                del files[name]
                update_list()
                write("Deleted\n")
            else:
                write("File not found\n")

        else:
            write("Unknown command\n")

        write("root@os:~# ")

    output.insert(tk.END, "System Ready.\nroot@os:~# ")

    def on_key(event):
        if event.keysym == "Return":
            cmd = output.get("end-2l linestart", "end-1c")
            cmd = cmd.split("root@os:~#")[-1]
            run_command(cmd)
            return "break"

    output.bind("<Return>", on_key)

    update_list()

    # ── LOGOUT ──
    bottom = tk.Frame(file_window, bg=BG)
    bottom.pack(fill="x", pady=10)

    tk.Button(
        bottom,
        text="⏻ Logout",
        bg=BG,
        fg=DANGER,
        bd=0,
        font=("Segoe UI", 10, "bold"),
        command=close_window,
        cursor="hand2"
    ).pack(side="right")