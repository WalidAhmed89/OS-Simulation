import tkinter as tk
from tkinter import messagebox
from process_api import spawn_process, finish_process, update_state
import filesystem_core as fs

file_window_instance = None


def open_file_page(role="ADMIN", login_window=None):
    global file_window_instance

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
    tk.Label(header, text=role, font=("Segoe UI",10,"bold"),
             bg=BG, fg=SUCCESS).place(relx=0.95, rely=0.5, anchor="e")

    # ── MAIN ──
    main = tk.Frame(file_window, bg=BG)
    main.pack(fill="both", expand=True, padx=20)


    #  LEFT — Explorer (Tree View)
    left = tk.Frame(main, bg=BG)
    left.pack(side="left", fill="both", expand=True)

    tk.Label(left, text="Explorer", font=("Segoe UI",12,"bold"),
             bg=BG, fg=TITLE_BLUE).pack(anchor="w")

    # ── Tree canvas & scrollbar
    tree_frame = tk.Frame(left, bg="white", highlightthickness=1,
                          highlightbackground="#e2e8f0")
    tree_frame.pack(fill="both", expand=True, pady=5)

    tree_canvas = tk.Canvas(tree_frame, bg="white", highlightthickness=0)
    scrollbar   = tk.Scrollbar(tree_frame, orient="vertical",
                               command=tree_canvas.yview)
    tree_canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree_canvas.pack(side="left", fill="both", expand=True)

    tree_inner = tk.Frame(tree_canvas, bg="white")
    tree_canvas.create_window((0,0), window=tree_inner, anchor="nw")

    def on_frame_configure(e):
        tree_canvas.configure(scrollregion=tree_canvas.bbox("all"))
    tree_inner.bind("<Configure>", on_frame_configure)

    # ── expanded folders state
    expanded = set()
    selected_path = [None]

    def refresh_tree():
        for w in tree_inner.winfo_children():
            w.destroy()

        data    = fs._load()
        tree_db = data["tree"]

        def render_dir(parent_path, depth):
            children = fs._children(tree_db, parent_path)
            for child in children:
                node     = tree_db[child]
                name     = fs._basename(child)
                is_dir   = node["type"] == "dir"
                indent   = depth * 16
                is_exp   = child in expanded

                row = tk.Frame(tree_inner, bg="white", cursor="hand2")
                row.pack(fill="x")

                # ── highlight if selected
                bg = "#dbeafe" if child == selected_path[0] else "white"
                row.config(bg=bg)

                # ── indent spacer
                tk.Label(row, width=indent//8 + 1, bg=bg).pack(side="left")

                if is_dir:
                    arrow = "▼" if is_exp else "▶"
                    tk.Label(row, text=arrow, font=("Segoe UI",9),
                             bg=bg, fg="#64748b").pack(side="left")
                    tk.Label(row, text="📁 " + name, font=FONT_MAIN,
                             bg=bg, fg=FG).pack(side="left", pady=1)
                else:
                    tk.Label(row, text="   ", bg=bg).pack(side="left")
                    tk.Label(row, text="📄 " + name, font=FONT_MAIN,
                             bg=bg, fg=FG).pack(side="left", pady=1)

                # ── click handler
                def on_click(e, path=child, is_directory=is_dir):
                    selected_path[0] = path

                    if is_directory:
                        if path in expanded:
                            expanded.discard(path)
                        else:
                            expanded.add(path)

                    refresh_tree()

                    return "break"

                row.bind("<Button-1>", on_click)
                for w in row.winfo_children():
                    w.bind("<Button-1>", on_click)


                if is_dir and is_exp:
                    render_dir(child, depth + 1)

        render_dir(fs.FS_ROOT, 0)

    refresh_tree()

    # ── inputs
    tk.Label(left, text="📄 File Name", bg=BG, fg=FG).pack(anchor="w")
    entry_name = tk.Entry(left, font=FONT_MAIN, bg="white", fg=FG, bd=0,
                          highlightthickness=1, highlightbackground="#e2e8f0")
    entry_name.pack(fill="x", pady=3)

    tk.Label(left, text="✏️ Content", bg=BG, fg=FG).pack(anchor="w")
    entry_content = tk.Entry(left, font=FONT_MAIN, bg="white", fg=FG, bd=0,
                             highlightthickness=1, highlightbackground="#e2e8f0")
    entry_content.pack(fill="x", pady=3)

    btns = tk.Frame(left, bg=BG)
    btns.pack(fill="x", pady=5)

    # ── FILE LOGIC ──

    def get_target_dir():
        path = selected_path[0]

        if not path:
            return fs.FS_ROOT

        data = fs._load()
        node = data["tree"].get(path)

        if node and node["type"] == "dir":
            return path
        else:
            return "/".join(path.split("/")[:-1])

    def clear_selection(event):
        widget = event.widget

        if str(widget).startswith(str(tree_inner)):
            return

        selected_path[0] = None
        refresh_tree()

    tree_canvas.bind("<Button-1>", clear_selection)

    def create_file():
        name = entry_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Enter file name", parent=file_window)
            return

        target_dir = get_target_dir()

        old_cwd = fs.get_cwd()
        fs.cd(target_dir)

        ok, msg = fs.touch(name)

        fs.cd(old_cwd)

        if not ok:
            messagebox.showerror("Error", msg, parent=file_window)
            return

        expanded.add(target_dir)

        refresh_tree()
        run_proc("fs_create")
        messagebox.showinfo("Success", f"File '{name}' was created", parent=file_window)
        entry_name.delete(0, tk.END)

    def create_folder():
        name = entry_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Enter folder name", parent=file_window)
            return

        target_dir = get_target_dir()

        old_cwd = fs.get_cwd()
        fs.cd(target_dir)

        ok, msg = fs.mkdir(name)

        fs.cd(old_cwd)

        if not ok:
            messagebox.showerror("Error", msg, parent=file_window)
            return

        expanded.add(target_dir)

        refresh_tree()
        run_proc("fs_mkdir")
        messagebox.showinfo("Success", f"Folder '{name}' was created", parent=file_window)
        entry_name.delete(0, tk.END)

    def delete_selected():
        path = selected_path[0]
        if not path:
            messagebox.showerror("Error", "Select a file or folder", parent=file_window)
            return

        ok, msg, needs_confirm = fs.rm(path, "-r")

        if ok and not needs_confirm:
            selected_path[0] = None
            refresh_tree()
            run_proc("fs_delete")
        else:
            messagebox.showerror("Error", msg, parent=file_window)

    def read_selected():
        path = selected_path[0]
        if not path:
            messagebox.showerror("Error", "Select a file", parent=file_window)
            return

        ok, content = fs.cat(path)

        if ok:
            messagebox.showinfo("Content", content, parent=file_window)
            run_proc("fs_read")
        else:
            messagebox.showerror("Error", content, parent=file_window)

    def write_selected():
        path = selected_path[0]
        if not path:
            messagebox.showerror("Error", "Select a file", parent=file_window)
            return

        content = entry_content.get()

        ok, msg = fs.write_file(path, content, append=True)

        if ok:
            entry_content.delete(0, tk.END)
            run_proc("fs_write")
        else:
            messagebox.showerror("Error", msg, parent=file_window)

    def make_btn(text, color, cmd, disabled=False):
        btn = tk.Button(btns, text=text, command=cmd, bg=BG, fg=color,
                        font=("Segoe UI", 9, "bold"), bd=0, cursor="hand2")
        btn.pack(side="left", expand=True, fill="x", padx=2)
        if disabled:
            btn.config(state="disabled", fg="#94a3b8", cursor="arrow")

    make_btn("📁 Folder", "#f59e0b", create_folder, disabled=(role=="GUEST"))
    make_btn("➕ File",   SUCCESS,   create_file,   disabled=(role=="GUEST"))
    make_btn("✏️ Write",  ACCENT,    write_selected, disabled=(role=="GUEST"))
    make_btn("👁 Read",   "#8b5cf6", read_selected)
    make_btn("🗑 Delete", DANGER,    delete_selected, disabled=(role in ["USER","GUEST"]))


    #  RIGHT — Terminal
    right = tk.Frame(main, bg=BG)
    right.pack(side="right", fill="both", expand=True, padx=(20,0))
    tk.Label(right, text="Terminal", font=("Segoe UI",12,"bold"),
             bg=BG, fg=TITLE_BLUE).pack(anchor="w")

    output = tk.Text(right, bg="#0b1220", fg="#10b981",
                     font=("Courier",10), bd=0, insertbackground="#10b981")
    output.pack(fill="both", expand=True, pady=10)
    output.tag_config("protected", foreground="#10b981")

    def write(text):
        output.insert(tk.END, text, "protected")
        output.mark_set("protected_end", tk.END)
        output.see(tk.END)

    def get_prompt():
        cwd = fs.get_cwd()
        display = cwd.replace(fs.FS_ROOT, "~")
        return f"root@os:{display}# "

    def get_input_start():
        content = output.get("1.0", tk.END)
        for prompt_end in ["# "]:
            last = content.rfind(prompt_end)
            if last != -1:
                pos   = last + len(prompt_end)
                line  = content[:pos].count("\n") + 1
                col   = len(content[:pos].split("\n")[-1])
                return f"{line}.{col}"
        return tk.END

    # ── pending rm -i confirmation
    pending_rm = [None]

    def run_command(raw):
        nonlocal pending_rm
        cmd = raw.strip()
        write("\n")

        # confirmation pending
        if pending_rm[0]:
            path = pending_rm[0]
            pending_rm[0] = None
            if cmd.lower() == "y":
                msg = fs.rm_confirmed(path)
                write((msg or "removed") + "\n")
                refresh_tree()
                run_proc("fs_delete")
            else:
                write("Cancelled\n")
            write(get_prompt())
            return

        parts = cmd.split()
        if not parts:
            write(get_prompt()); return

        c = parts[0]

        # ── help
        if c == "help":
            write("Commands: ls, ls -a, ls -l, pwd, cd, mkdir, mkdir -p,\n"
                  "          touch, stat, rm, rm -r, rm -i, rm -v, rmdir,\n"
                  "          cat, echo text > file, clear\n")

        # ── clear
        elif c == "clear":
            output.delete("1.0", tk.END)
            write(get_prompt()); return

        # ── pwd
        elif c == "pwd":
            write(fs.pwd() + "\n")
            run_proc("fs_pwd")

        # ── cd
        elif c == "cd":
            target = parts[1] if len(parts) > 1 else "~"
            ok, msg = fs.cd(target)
            if not ok: write(msg + "\n")
            refresh_tree()

        # ── ls / ls -a / ls -l / ls -la
        elif c == "ls":
            flags = " ".join(parts[1:])
            write(fs.ls(flags) + "\n")
            run_proc("fs_ls")

        # ── mkdir / mkdir -p
        elif c == "mkdir":
            if role == "GUEST":
                write("Permission denied\n")
            elif len(parts) < 2:
                write("Usage: mkdir [-p] <name>\n")
            elif parts[1] == "-p" and len(parts) > 2:
                ok, msg = fs.mkdir(parts[2], parents=True)
                if not ok: write(msg + "\n")
                else: refresh_tree(); run_proc("fs_mkdir")
            else:
                ok, msg = fs.mkdir(parts[-1])
                if not ok: write(msg + "\n")
                else: refresh_tree(); run_proc("fs_mkdir")

        # ── touch flags
        elif c == "touch":
            if role == "GUEST":
                write("Permission denied\n")
            elif len(parts) < 2:
                write("Usage: touch [-a|-m|-c|-d date|-r ref] <file>\n")
            else:
                flag     = None
                date_str = None
                ref_file = None
                fname    = parts[-1]

                if "-a" in parts: flag = "-a"
                elif "-m" in parts: flag = "-m"
                elif "-c" in parts: flag = "-c"
                elif "-d" in parts:
                    flag = "-d"
                    idx  = parts.index("-d")
                    date_str = parts[idx+1] if idx+1 < len(parts)-1 else None
                elif "-r" in parts:
                    flag = "-r"
                    idx  = parts.index("-r")
                    ref_file = parts[idx+1] if idx+1 < len(parts)-1 else None

                ok, msg = fs.touch(fname, flag=flag,
                                   ref_file=ref_file, date_str=date_str)
                if not ok: write(msg + "\n")
                else: refresh_tree(); run_proc("fs_touch")

        # ── stat
        elif c == "stat":
            if len(parts) < 2:
                write("Usage: stat <file>\n")
            else:
                ok, msg = fs.stat(parts[1])
                write(msg + "\n")
                run_proc("fs_stat")

        # ── rm و flags
        elif c == "rm":
            if role in ["USER", "GUEST"]:
                write("Permission denied\n")
            elif len(parts) < 2:
                write("Usage: rm [-r|-i|-v|-iv|-rv] <name>\n")
            else:
                flags = " ".join(parts[1:-1])
                name  = parts[-1]
                ok, msg, needs_confirm = fs.rm(name, flags)
                if needs_confirm:
                    write(msg + " ")
                    pending_rm[0] = fs._resolve(fs.get_cwd(), name)
                    write(get_prompt()); return
                elif ok:
                    if msg: write(msg + "\n")
                    refresh_tree(); run_proc("fs_delete")
                else:
                    write(msg + "\n")

        # ── rmdir
        elif c == "rmdir":
            if role in ["USER", "GUEST"]:
                write("Permission denied\n")
            elif len(parts) < 2:
                write("Usage: rmdir <dir>\n")
            else:
                ok, msg = fs.rmdir(parts[1])
                if not ok: write(msg + "\n")
                else: refresh_tree(); run_proc("fs_rmdir")

        # ── cat
        elif c == "cat":
            if len(parts) < 2:
                write("Usage: cat <file>\n")
            else:
                ok, content = fs.cat(parts[1])
                write(content + "\n")
                run_proc("fs_read")

        # ── echo text > file
        elif c == "echo":
            if role == "GUEST":
                write("Permission denied\n")
            elif ">" not in parts:
                write("Usage: echo <text> > <file>\n")
            else:
                idx      = parts.index(">")
                text     = " ".join(parts[1:idx])
                filename = parts[idx+1] if idx+1 < len(parts) else ""
                if not filename:
                    write("Usage: echo <text> > <file>\n")
                else:
                    ok, msg = fs.write_file(filename, text, append=True)
                    if ok:
                        write(f"Written to {filename}\n")
                        run_proc("fs_write")
                    else:
                        write(msg + "\n")

        else:
            write(f"{c}: command not found\n")

        write(get_prompt())

    # ── initial prompt
    output.insert(tk.END, f"System Ready.\n{get_prompt()}", "protected")
    output.mark_set("protected_end", tk.END)

    def on_key(event):
        if event.keysym == "Return":
            prompt   = get_prompt()
            last_line = output.get("end-1l linestart", "end-1c")
            cmd = last_line.split(prompt)[-1] if prompt in last_line else ""
            run_command(cmd)
            return "break"

        if event.keysym in ("BackSpace", "Delete"):
            try:
                if output.compare(output.index(tk.INSERT), "<=", get_input_start()):
                    return "break"
            except:
                pass

        if event.char and event.keysym not in ("Return","BackSpace","Delete"):
            try:
                if output.compare(output.index(tk.INSERT), "<", get_input_start()):
                    output.mark_set(tk.INSERT, tk.END)
            except:
                pass

    output.bind("<Key>", on_key)
    output.bind("<Return>", on_key)