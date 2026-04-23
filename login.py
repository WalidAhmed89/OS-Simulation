import tkinter as tk
from tkinter import messagebox
from file_page import open_file_page  

# --- Style Settings ---
BG_COLOR = "#0f172a"
FG_COLOR = "#f8fafc"
ACCENT_COLOR = "#3b82f6"
HOVER_COLOR = "#2563eb"
PULSE_COLOR = "#6ea8fe"
INPUT_BG = "#1e293b"
INPUT_FG = "#f8fafc"
FOCUS_BG = "#334155"
FONT_MAIN = ("Segoe UI", 12)
FONT_TITLE = ("Segoe UI", 24, "bold")

users = {
    "admin": {"password": "123", "role": "ADMIN"},
    "user": {"password": "123", "role": "USER"},
    "guest": {"password": "123", "role": "GUEST"}
}

def login(event=None):
    username = entry_user.get()
    password = entry_pass.get()

    if username in users and users[username]["password"] == password:
        role = users[username]["role"]
        
        # Success Animation (Fade out and shrink)
        def final_fade_out(window, alpha=1.0, rely=0.5):
            if alpha > 0.0:
                alpha -= 0.05
                rely -= 0.01 # fly up
                frame.place(relx=0.5, rely=rely, anchor=tk.CENTER)
                window.attributes('-alpha', alpha)
                window.after(15, lambda: final_fade_out(window, alpha, rely))
            else:
                window.withdraw()
                open_file_page(role, window)
                
        final_fade_out(root)
    else:
        # Shake animation on error
        def shake(window, count=0):
            if count < 10:
                x = root.winfo_x()
                y = root.winfo_y()
                dx = 5 if count % 2 == 0 else -5
                window.geometry(f"+{x+dx}+{y}")
                window.after(30, lambda: shake(window, count+1))
        shake(root)
        
        lbl_title.config(fg="#ef4444", text="Invalid Login")
        root.after(1500, lambda: lbl_title.config(fg=FG_COLOR, text="Welcome Back"))


root = tk.Tk()
root.title("OS Simulator - Login")
root.geometry("400x500")
root.configure(bg=BG_COLOR)
root.attributes('-alpha', 0.0)

root.eval('tk::PlaceWindow . center')

frame = tk.Frame(root, bg=BG_COLOR)
# Start lower for slide up animation
frame.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

lbl_title = tk.Label(frame, text="", font=FONT_TITLE, bg=BG_COLOR, fg=FG_COLOR)
lbl_title.pack(pady=(0, 30))

tk.Label(frame, text="Username", font=FONT_MAIN, bg=BG_COLOR, fg="#94a3b8").pack(anchor="w")
entry_user = tk.Entry(frame, font=FONT_MAIN, bg=INPUT_BG, fg=INPUT_FG, insertbackground=INPUT_FG, relief="flat", highlightthickness=1, highlightbackground="#334155")
entry_user.pack(fill="x", pady=(5, 15), ipady=8, ipadx=10)

tk.Label(frame, text="Password", font=FONT_MAIN, bg=BG_COLOR, fg="#94a3b8").pack(anchor="w")
entry_pass = tk.Entry(frame, font=FONT_MAIN, bg=INPUT_BG, fg=INPUT_FG, insertbackground=INPUT_FG, relief="flat", show="*", highlightthickness=1, highlightbackground="#334155")
entry_pass.pack(fill="x", pady=(5, 30), ipady=8, ipadx=10)

btn_login = tk.Button(frame, text="LOGIN", font=("Segoe UI", 12, "bold"), bg=ACCENT_COLOR, fg="white", relief="flat", activebackground=HOVER_COLOR, activeforeground="white", command=login, cursor="hand2")
btn_login.pack(fill="x", ipady=10)

entry_pass.bind("<Return>", login)
entry_user.bind("<Return>", lambda e: entry_pass.focus())

# --- Focus Animations (Border Glow) ---
def on_focus_in(e):
    e.widget.config(highlightbackground=PULSE_COLOR, bg=FOCUS_BG)

def on_focus_out(e):
    e.widget.config(highlightbackground="#334155", bg=INPUT_BG)

entry_user.bind("<FocusIn>", on_focus_in)
entry_user.bind("<FocusOut>", on_focus_out)
entry_pass.bind("<FocusIn>", on_focus_in)
entry_pass.bind("<FocusOut>", on_focus_out)

# --- Button Pulse Animation ---
btn_hovered = False

def pulse_button(intensity=0, increasing=True):
    if not btn_hovered:
        colors = ["#2563eb", "#2d6ef0", "#3376f4", "#3b82f6", "#498df8", "#5a98f9", "#6aa6fb"]
        btn_login.config(bg=colors[intensity])
        
        if increasing:
            intensity += 1
            if intensity >= len(colors)-1:
                increasing = False
        else:
            intensity -= 1
            if intensity <= 0:
                increasing = True
    
    root.after(80, lambda: pulse_button(intensity, increasing))

def on_enter(e):
    global btn_hovered
    btn_hovered = True
    e.widget['background'] = HOVER_COLOR

def on_leave(e):
    global btn_hovered
    btn_hovered = False
    e.widget['background'] = ACCENT_COLOR

btn_login.bind("<Enter>", on_enter)
btn_login.bind("<Leave>", on_leave)

# --- Start Animations ---
def slide_up(rely=0.6):
    if rely > 0.5:
        rely -= 0.005
        frame.place(relx=0.5, rely=rely, anchor=tk.CENTER)
        root.after(15, lambda: slide_up(rely))

def type_title(text="Welcome Back", idx=0):
    if idx <= len(text):
        lbl_title.config(text=text[:idx])
        root.after(70, lambda: type_title(text, idx+1))

def fade_in(alpha=0.0):
    if alpha < 1.0:
        alpha += 0.05
        root.attributes('-alpha', alpha)
        root.after(15, lambda: fade_in(alpha))

fade_in()
slide_up()
type_title()
pulse_button()

# Start with focus on username
entry_user.focus()

root.mainloop()