import tkinter as tk
from tkinter import messagebox

# --- Style Settings ---
BG_COLOR = "#0f172a"
PANEL_BG = "#1e293b"
FG_COLOR = "#f8fafc"
TXT_COLOR = "#94a3b8"
ACCENT_COLOR = "#3b82f6"
HOVER_COLOR = "#2563eb"
DANGER_COLOR = "#ef4444"
DANGER_HOVER = "#dc2626"
INPUT_BG = "#0f172a"
INPUT_FG = "#f8fafc"
FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_MAIN = ("Segoe UI", 11)
FONT_MONO = ("Consolas", 10)

files = {}

def open_file_page(role, login_window=None):
    file_window = tk.Toplevel()
    file_window.title("OS Simulator - File System")
    file_window.geometry("850x650")
    file_window.configure(bg=BG_COLOR)
    file_window.attributes('-alpha', 0.0)

    # --- Animations ---
    def fade_in(alpha=0.0):
        if alpha < 1.0:
            alpha += 0.05
            file_window.attributes('-alpha', alpha)
            file_window.after(15, lambda: fade_in(alpha))
            
    fade_in()

    def fade_out(callback, alpha=1.0):
        if alpha > 0.0:
            alpha -= 0.05
            file_window.attributes('-alpha', alpha)
            file_window.after(15, lambda: fade_out(callback, alpha))
        else:
            callback()

    def shutdown():
        def on_fade_out():
            file_window.destroy()
            if login_window:
                login_window.attributes('-alpha', 0.0)
                login_window.deiconify()
                # Fade in login window again
                def login_fade_in(al=0.0):
                    if al < 1.0:
                        al += 0.05
                        login_window.attributes('-alpha', al)
                        login_window.after(15, lambda: login_fade_in(al))
                login_fade_in()
        fade_out(on_fade_out)

    # Hover animations for buttons
    def on_enter(e, color):
        if e.widget['state'] != 'disabled':
            e.widget['background'] = color

    def on_leave(e, color):
        if e.widget['state'] != 'disabled':
            e.widget['background'] = color

    def style_button(btn, bg_color, hover_color):
        btn.configure(bg=bg_color, fg="white", relief="flat", activebackground=hover_color, 
                      activeforeground="white", font=("Segoe UI", 10, "bold"), cursor="hand2")
        btn.bind("<Enter>", lambda e: on_enter(e, hover_color))
        btn.bind("<Leave>", lambda e: on_leave(e, bg_color))

    # --- Layout ---
    header_frame = tk.Frame(file_window, bg=PANEL_BG)
    header_frame.pack(fill="x", pady=(0, 10))

    tk.Label(header_frame, text="File Management System", font=FONT_TITLE, bg=PANEL_BG, fg=FG_COLOR).pack(side="left", padx=20, pady=15)
    tk.Label(header_frame, text=f"Role: {role}", font=("Segoe UI", 12, "bold"), bg=PANEL_BG, fg="#10b981").pack(side="right", padx=20, pady=15)

    main_frame = tk.Frame(file_window, bg=BG_COLOR)
    main_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Split into Two Panels
    left_panel = tk.Frame(main_frame, bg=PANEL_BG, padx=20, pady=20)
    left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

    right_panel = tk.Frame(main_frame, bg=PANEL_BG, padx=20, pady=20)
    right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))

    # ================= LEFT PANEL =================
    tk.Label(left_panel, text="Files Explorer", font=FONT_TITLE, bg=PANEL_BG, fg=FG_COLOR).pack(anchor="w", pady=(0, 10))
    
    listbox = tk.Listbox(left_panel, height=8, bg=INPUT_BG, fg=INPUT_FG, font=FONT_MAIN, relief="flat", 
                         highlightthickness=1, highlightbackground="#334155", selectbackground=ACCENT_COLOR, 
                         selectforeground="white")
    listbox.pack(pady=5, fill="both", expand=True)

    input_frame = tk.Frame(left_panel, bg=PANEL_BG)
    input_frame.pack(fill="x", pady=10)

    tk.Label(input_frame, text="File Name:", font=FONT_MAIN, bg=PANEL_BG, fg=TXT_COLOR).grid(row=0, column=0, sticky="w", pady=5)
    entry_name = tk.Entry(input_frame, font=FONT_MAIN, bg=INPUT_BG, fg=INPUT_FG, insertbackground=INPUT_FG, relief="flat", highlightthickness=1, highlightbackground="#334155")
    entry_name.grid(row=0, column=1, sticky="ew", padx=10, pady=5, ipady=4)

    tk.Label(input_frame, text="Content:", font=FONT_MAIN, bg=PANEL_BG, fg=TXT_COLOR).grid(row=1, column=0, sticky="w", pady=5)
    entry_content = tk.Entry(input_frame, font=FONT_MAIN, bg=INPUT_BG, fg=INPUT_FG, insertbackground=INPUT_FG, relief="flat", highlightthickness=1, highlightbackground="#334155")
    entry_content.grid(row=1, column=1, sticky="ew", padx=10, pady=5, ipady=4)
    input_frame.columnconfigure(1, weight=1)

    # Action Buttons
    btn_frame = tk.Frame(left_panel, bg=PANEL_BG)
    btn_frame.pack(fill="x", pady=(10, 0))

    btn_create = tk.Button(btn_frame, text="Create", command=lambda: create_file())
    style_button(btn_create, "#10b981", "#059669")
    btn_create.pack(side="left", expand=True, fill="x", padx=2, ipady=4)

    btn_write = tk.Button(btn_frame, text="Write", command=lambda: write_file())
    style_button(btn_write, ACCENT_COLOR, HOVER_COLOR)
    btn_write.pack(side="left", expand=True, fill="x", padx=2, ipady=4)

    btn_read = tk.Button(btn_frame, text="Read", command=lambda: read_file())
    style_button(btn_read, "#8b5cf6", "#7c3aed")
    btn_read.pack(side="left", expand=True, fill="x", padx=2, ipady=4)

    btn_delete = tk.Button(btn_frame, text="Delete", command=lambda: delete_file())
    style_button(btn_delete, DANGER_COLOR, DANGER_HOVER)
    btn_delete.pack(side="left", expand=True, fill="x", padx=2, ipady=4)

    # ================= RIGHT PANEL =================
    tk.Label(right_panel, text="Terminal (CLI) 🔥", font=FONT_TITLE, bg=PANEL_BG, fg=FG_COLOR).pack(anchor="w", pady=(0, 10))

    output_box = tk.Text(right_panel, height=15, bg="#000000", fg="#10b981", font=FONT_MONO, relief="flat", 
                         highlightthickness=1, highlightbackground="#334155", state="disabled", wrap="word", 
                         cursor="arrow", padx=5, pady=5)
    output_box.pack(pady=5, fill="both", expand=True)

    cli_input_frame = tk.Frame(right_panel, bg=PANEL_BG)
    cli_input_frame.pack(fill="x", pady=(5, 0))
    
    tk.Label(cli_input_frame, text="root@os:~#", font=FONT_MONO, bg=PANEL_BG, fg="#10b981").pack(side="left")
    entry_command = tk.Entry(cli_input_frame, font=FONT_MONO, bg=INPUT_BG, fg=INPUT_FG, insertbackground=INPUT_FG, relief="flat", highlightthickness=1, highlightbackground="#334155")
    entry_command.pack(side="left", fill="x", expand=True, padx=(5, 0), ipady=5)

    # ================= BOTTOM PANEL =================
    bottom_frame = tk.Frame(file_window, bg=BG_COLOR)
    bottom_frame.pack(fill="x", padx=20, pady=(0, 20))

    btn_shutdown = tk.Button(bottom_frame, text="⏻ Shutdown / Logout", command=shutdown)
    style_button(btn_shutdown, DANGER_COLOR, DANGER_HOVER)
    btn_shutdown.pack(side="right", ipadx=10, ipady=5)

    def output(text):
        output_box.config(state="normal")
        output_box.insert(tk.END, text + "\n")
        output_box.see(tk.END)
        output_box.config(state="disabled")

    output("System Initialized.\nWelcome to OS CLI.\n")

    # ================= Core Functions =================
    def create_file():
        name = entry_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Enter file name", parent=file_window)
            return
        
        if name in files:
            messagebox.showerror("Error", "File already exists!", parent=file_window)
            return

        files[name] = {"name": name, "content": ""}
        update_list()
        entry_name.delete(0, tk.END)
        messagebox.showinfo("Success", f"{name} created!", parent=file_window)

    def delete_file():
        selected = listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "Select file to delete", parent=file_window)
            return
        
        name = listbox.get(selected[0])
        del files[name]
        update_list()
        messagebox.showinfo("Success", f"{name} deleted!", parent=file_window)

    def read_file():
        selected = listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "Select file to read", parent=file_window)
            return
        
        name = listbox.get(selected[0])
        content = files[name]["content"]
        
        display_text = content if content else "(empty)"
        messagebox.showinfo(f"Content of {name}", display_text, parent=file_window)

    def write_file():
        selected = listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "Select file to write", parent=file_window)
            return
        
        name = listbox.get(selected[0])
        content = entry_content.get()

        files[name]["content"] += content + "\n"
        entry_content.delete(0, tk.END)
        messagebox.showinfo("Success", f"Written to {name}", parent=file_window)

    def update_list():
        listbox.delete(0, tk.END)
        for name in files:
            listbox.insert(tk.END, name)

    update_list()

    # ================= CLI Functions =================
    def cmd_ls(parts):
        output("\n".join(files.keys()) if files else "No files")

    def cmd_touch(parts):
        if role == "GUEST":
            output("Permission denied.")
            return
        if len(parts) < 2:
            output("Usage: touch filename")
            return
        
        name = parts[1]
        if name in files:
            output("File already exists")
        else:
            files[name] = {"name": name, "content": ""}
            update_list()
            output(f"{name} created")

    def cmd_rm(parts):
        if role in ["USER", "GUEST"]:
            output("Permission denied.")
            return
        if len(parts) < 2:
            output("Usage: rm filename")
            return
        
        name = parts[1]
        if name in files:
            del files[name]
            update_list()
            output(f"{name} deleted")
        else:
            output("File not found")

    def cmd_cat(parts):
        if len(parts) < 2:
            output("Usage: cat filename")
            return
        
        name = parts[1]
        if name in files:
            content = files[name]["content"]
            output(content if content else "(empty)")
        else:
            output("File not found")

    def cmd_echo(parts):
        if role == "GUEST":
            output("Permission denied.")
            return
        if ">" not in parts:
            output("Usage: echo text > filename")
            return
        
        idx = parts.index(">")
        content = " ".join(parts[1:idx])
        filename = parts[idx + 1]

        if filename in files:
            files[filename]["content"] += content + "\n"
            output(f"Written to {filename}")
        else:
            output("File not found")

    def cmd_clear(parts):
        output_box.config(state="normal")
        output_box.delete("1.0", tk.END)
        output_box.config(state="disabled")

    commands = {
        "ls": cmd_ls,
        "touch": cmd_touch,
        "rm": cmd_rm,
        "cat": cmd_cat,
        "echo": cmd_echo,
        "clear": cmd_clear
    }

    def execute_command():
        command = entry_command.get().strip()
        entry_command.delete(0, tk.END)

        if not command:
            return

        output(f"root@os:~# {command}")
        
        parts = command.split()
        cmd = parts[0].lower()

        if cmd in commands:
            commands[cmd](parts)
        else:
            output("Unknown command. Available commands: ls, touch, rm, cat, echo, clear")
            
        output("") 

    entry_command.bind("<Return>", lambda event: execute_command())

    # ================= Permissions =================
    if role == "USER":
        btn_delete.config(state="disabled", bg="#475569", cursor="arrow")
        btn_delete.unbind("<Enter>")
        btn_delete.unbind("<Leave>")
    elif role == "GUEST":
        btn_create.config(state="disabled", bg="#475569", cursor="arrow")
        btn_delete.config(state="disabled", bg="#475569", cursor="arrow")
        btn_write.config(state="disabled", bg="#475569", cursor="arrow")
        for btn in [btn_create, btn_delete, btn_write]:
            btn.unbind("<Enter>")
            btn.unbind("<Leave>")