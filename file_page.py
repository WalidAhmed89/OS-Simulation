import tkinter as tk
from tkinter import messagebox
import json
import os
from process_api import spawn_process, finish_process, update_state

FILES_JSON = "files.json"

# ── بنحفظ الـ files في JSON عشان تفضل موجودة بعد الـ logout
def _load_files():
    if not os.path.exists(FILES_JSON):
        return {}
    try:
        with open(FILES_JSON, "r") as f:
            return json.load(f)
    except:
        return {}

def _save_files(files):
    with open(FILES_JSON, "w") as f:
        json.dump(files, f, indent=2)

file_window_instance = None

# ── بنحمّل الـ files مرة واحدة لما الملف يتعمل import
# ── وبتفضل في الـ memory طول ما البرنامج شغال
files = _load_files()


def open_file_page(role="ADMIN", login_window=None):
    global file_window_instance, files

    if file_window_instance is not None:
        try:
            file_window_instance.lift()
            file_window_instance.focus_force()
            return
        except:
            file_window_instance = None

    BG         = "#f5f7fb"
    FG         = "#1f2937"
    ACCENT     = "#3b82f6"
    SUCCESS    = "#10b981"
    DANGER     = "#ef4444"
    TITLE_BLUE = "#2563eb"
    FONT_TITLE = ("Segoe UI", 14, "bold")
    FONT_MAIN  = ("Courier", 10)

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

    def fade_in(a=0):
        if a < 1:
            file_window.attributes("-alpha", a)
            file_window.after(15, lambda: fade_in(a + 0.05))
    fade_in()

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

    # ── helper: spawn → Running → Finished ──
    def run_proc(name):
        p = spawn_process(name, burst_time=2, memory_size=8)
        if p:
            update_state(p.pid, "Running")
            file_window.after(2000, lambda: finish_process(p.pid))

    # ── HEADER ──
    header = tk.Frame(file_window, bg=BG)
    header.pack(fill="x", pady=10)
    tk.Frame(header, bg=BG).pack(side="left", expand=True)
    tk.Label(header, text="File System", font=("Segoe UI",16,"bold"),
             bg=BG, fg=TITLE_BLUE).pack(side="left")
    tk.Frame(header, bg=BG).pack(side="left", expand=True)
    # ── بنعرض الـ role الحقيقي
    tk.Label(header, text=role, font=("Segoe UI",10,"bold"),
             bg=BG, fg=SUCCESS).place(relx=0.95, rely=0.5, anchor="e")

    # ── MAIN ──
    main = tk.Frame(file_window, bg=BG)
    main.pack(fill="both", expand=True, padx=20)

    # ── LEFT ──
    left = tk.Frame(main, bg=BG)
    left.pack(side="left", fill="both", expand=True)
    tk.Label(left, text="Explorer", font=("Segoe UI",12,"bold"),
             bg=BG, fg=TITLE_BLUE).pack(anchor="w")

    listbox = tk.Listbox(left, bg="white", fg=FG, font=FONT_MAIN,
                         selectbackground=ACCENT, bd=0, highlightthickness=0)
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
            messagebox.showerror("Error", "Enter file name", parent=file_window); return
        if name in files:
            messagebox.showerror("Error", "File exists!", parent=file_window); return
        files[name] = {"content": ""}
        update_list()
        _save_files(files)
        run_proc("fs_create")
        # ── Dialog بعد الـ create + بنفضي الـ entry
        messagebox.showinfo("Success", f"File '{name}' was created", parent=file_window)
        entry_name.delete(0, tk.END)

    def delete_file():
        sel = listbox.curselection()
        if sel:
            files.pop(listbox.get(sel[0]), None)
            update_list()
            _save_files(files)
            run_proc("fs_delete")

    def read_file():
        sel = listbox.curselection()
        if sel:
            name = listbox.get(sel[0])
            messagebox.showinfo("Content", files[name]["content"] or "(empty)")
            run_proc("fs_read")

    def write_file():
        sel = listbox.curselection()
        if sel:
            name = listbox.get(sel[0])
            files[name]["content"] += entry_content.get() + "\n"
            entry_content.delete(0, tk.END)
            _save_files(files)
            run_proc("fs_write")

    # ── Buttons مع permissions ──
    def make_btn(text, color, cmd, disabled=False):
        btn = tk.Button(btns, text=text, command=cmd, bg=BG, fg=color,
                        font=("Segoe UI",10,"bold"), bd=0, cursor="hand2")
        btn.pack(side="left", expand=True, fill="x", padx=5)
        if disabled:
            btn.config(state="disabled", fg="#94a3b8", cursor="arrow")

    # ADMIN  → كل حاجة
    # USER   → مش يمسح
    # GUEST  → يقرأ بس
    make_btn("➕ Create", SUCCESS, create_file, disabled=(role == "GUEST"))
    make_btn("✏️ Write",  ACCENT,  write_file,  disabled=(role == "GUEST"))
    make_btn("👁 Read",   "#8b5cf6", read_file)
    make_btn("🗑 Delete", DANGER,  delete_file, disabled=(role in ["USER","GUEST"]))

    # ── TERMINAL ──
    right = tk.Frame(main, bg=BG)
    right.pack(side="right", fill="both", expand=True, padx=(20,0))
    tk.Label(right, text="Terminal", font=("Segoe UI",12,"bold"),
             bg=BG, fg=TITLE_BLUE).pack(anchor="w")

    output = tk.Text(right, bg="#0b1220", fg="#10b981",
                     font=("Courier",10), bd=0, insertbackground="#10b981")
    output.pack(fill="both", expand=True, pady=10)

    # ── بنعمل tag للـ output المحمي عشان نمنع تعديله
    output.tag_config("protected", foreground="#10b981")

    def write(text):
        output.insert(tk.END, text, "protected")
        # ── بعد ما نكتب نحدد الـ protected region
        output.mark_set("protected_end", tk.END)
        output.see(tk.END)

    def get_input_start():
        """بترجع الـ index بتاع أول حرف بعد آخر prompt"""
        content = output.get("1.0", tk.END)
        last = content.rfind("root@os:~#")
        if last == -1:
            return tk.END
        # نحول الـ character index لـ tkinter index
        line = content[:last].count("\n") + 1
        col  = len("root@os:~#")
        return f"{line}.{col}"

    def run_command(cmd):
        cmd = cmd.strip()
        write("\n")

        if cmd == "help":
            write("help | clear | ls | cat <n> | touch <n> | rm <n> | echo text > <n>\n")

        elif cmd == "clear":
            output.config(state="normal")
            output.delete("1.0", tk.END)
            write("root@os:~# ")
            return

        elif cmd == "ls":
            write((" ".join(files.keys()) or "(empty)") + "\n")
            run_proc("fs_ls")

        elif cmd.startswith("touch "):
            if role == "GUEST":
                write("Permission denied\n")
            else:
                name = cmd[6:]
                if name in files:
                    write("File already exists\n")
                else:
                    files[name] = {"content": ""}
                    update_list()
                    write(f"{name} created\n")
                    _save_files(files)
                    run_proc("fs_create")

        elif cmd.startswith("cat "):
            name = cmd[4:]
            write(files.get(name, {}).get("content", "File not found") + "\n")
            run_proc("fs_read")

        elif cmd.startswith("rm "):
            if role in ["USER", "GUEST"]:
                write("Permission denied\n")
            else:
                name = cmd[3:]
                if name in files:
                    del files[name]
                    update_list()
                    write("Deleted\n")
                    _save_files(files)
                    run_proc("fs_delete")
                else:
                    write("File not found\n")

        elif cmd.startswith("echo "):
            # ── echo text > filename  (زي صحبك بالظبط)
            if role == "GUEST":
                write("Permission denied\n")
            else:
                parts = cmd.split()
                if ">" not in parts:
                    write("Usage: echo text > filename\n")
                else:
                    idx      = parts.index(">")
                    text     = " ".join(parts[1:idx])
                    filename = parts[idx + 1] if idx + 1 < len(parts) else ""
                    if not filename:
                        write("Usage: echo text > filename\n")
                    elif filename not in files:
                        write("File not found\n")
                    else:
                        files[filename]["content"] += text + "\n"
                        _save_files(files)
                        write(f"Written to {filename}\n")
                        run_proc("fs_write")

        else:
            write("Unknown command\n")

        write("root@os:~# ")

    output.insert(tk.END, "System Ready.\nroot@os:~# ", "protected")
    output.mark_set("protected_end", tk.END)

    def on_key(event):
        if event.keysym == "Return":
            cmd = output.get("end-2l linestart", "end-1c")
            cmd = cmd.split("root@os:~#")[-1]
            run_command(cmd)
            return "break"

        # ── نمنع الـ backspace و delete لو وصل للـ protected area
        if event.keysym in ("BackSpace", "Delete"):
            try:
                input_start = get_input_start()
                cursor      = output.index(tk.INSERT)
                # لو الـ cursor على أو قبل نهاية الـ prompt نمنع الحذف
                if output.compare(cursor, "<=", input_start):
                    return "break"
            except:
                pass

        # ── نمنع أي كتابة لو الـ cursor في منطقة محمية
        if event.char and event.keysym not in ("Return", "BackSpace", "Delete"):
            try:
                input_start = get_input_start()
                cursor      = output.index(tk.INSERT)
                if output.compare(cursor, "<", input_start):
                    output.mark_set(tk.INSERT, tk.END)
            except:
                pass

    output.bind("<Key>", on_key)
    output.bind("<Return>", on_key)
    # ── نمنع الـ click من نقل الـ cursor لمنطقة محمية
    def on_click(event):
        output.after(1, lambda: None)  # نسمح بالـ click عادي للـ select
    output.bind("<Button-1>", on_click)

    update_list()