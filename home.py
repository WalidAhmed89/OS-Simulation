import os
import sys
import tkinter as tk
import subprocess
import datetime
from PIL import Image, ImageTk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ROLE = sys.argv[1] if len(sys.argv) > 1 else "ADMIN"

BG      = "#f5f7fb"
CARD    = "#ffffff"
BORDER  = "#e2e8f0"
FG      = "#1f2937"
SUB     = "#64748b"
ACCENT  = "#3b82f6"
TASKBAR = "#ffffff"

FONT_LABEL = ("Georgia", 10, "bold")
FONT_SUB   = ("Courier", 7)

W, H = 850, 650

APPS = [
    {
        "id":    "terminal",
        "label": "Terminal",
        "sub":   "C O M M A N D   L I N E",
        "icon":  ">_",
        "color": "#10b981",
        "file":  "terminal"
    },
    {
        "id":    "tasks",
        "label": "Task Manager",
        "sub":   "P R O C E S S E S",
        "icon":  "≡",
        "color": "#3b82f6",
        "file":  "Process.py",
    },
    {
        "id":    "devices",
        "label": "Device Manager",
        "sub":   "H A R D W A R E",
        "icon":  "⊞",
        "color": "#a855f7",
        "file":  "DeviceManagement.py",
    },
]


_open_procs = []


class AppCard:
    CARD_W = 170
    CARD_H = 200

    def __init__(self, canvas, root, cx, cy, data, delay):
        self.canvas = canvas
        self.root   = root
        self.data   = data
        self.cx, self.cy = cx, cy
        self.tag    = data["id"]
        root.after(delay, self.create)

    def create(self):
        cx, cy = self.cx, self.cy
        w2, h2 = self.CARD_W//2, self.CARD_H//2
        x0, y0 = cx-w2, cy-h2
        x1, y1 = cx+w2, cy+h2

        # ── لو GUEST وهو app محظور نغير لونه لرمادي
        locked = ROLE == "GUEST" and self.data["id"] in ["tasks", "devices"]
        color  = "#94a3b8" if locked else self.data["color"]

        self.rect = self.canvas.create_rectangle(
            x0, y0, x1, y1, fill=CARD, outline=BORDER, width=1, tags=self.tag)

        self.canvas.create_text(cx, cy-35, text=self.data["icon"],
                                font=("Courier",20,"bold"), fill=color, tags=self.tag)
        self.canvas.create_text(cx, cy+15, text=self.data["label"],
                                font=FONT_LABEL, fill=FG if not locked else "#94a3b8", tags=self.tag)
        self.canvas.create_text(cx, cy+35, text=self.data["sub"],
                                font=FONT_SUB, fill=SUB, tags=self.tag)
        self.canvas.create_text(cx, cy+65,
                                text="LOCKED" if locked else "OPEN",
                                font=("Courier",8,"bold"), fill=color, tags=self.tag)

        if not locked:
            self.canvas.tag_bind(self.tag, "<Enter>", self.on_enter)
            self.canvas.tag_bind(self.tag, "<Leave>", self.on_leave)
            self.canvas.tag_bind(self.tag, "<Button-1>", self.on_click)

    def on_enter(self, e):
        self.canvas.itemconfig(self.rect, outline=self.data["color"], width=2)

    def on_leave(self, e):
        self.canvas.itemconfig(self.rect, outline=BORDER, width=1)

    def on_click(self, e):
        self.root.after(100, self.open_app)

    def open_app(self):
        try:
            if self.data["id"] == "terminal":
                from file_page import open_file_page
                open_file_page(role=ROLE, login_window=None)
            else:
                proc = subprocess.Popen([sys.executable,
                                         os.path.join(BASE_DIR, self.data["file"])])
                _open_procs.append(proc)
        except Exception as ex:
            print("Error opening app:", ex)


class FilePage:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Frosted OS")
        self.root.configure(bg=BG)
        self.root.geometry(f"{W}x{H}")
        self.root.attributes("-alpha", 0.0)

        self.root.protocol("WM_DELETE_WINDOW", self.logout)

        self.canvas = tk.Canvas(self.root, bg=BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.draw_taskbar()
        self.draw_header()
        self.spawn()
        self.update_clock()
        self.fade()

    def draw_taskbar(self):
        self.canvas.create_rectangle(0, H-40, W, H, fill=TASKBAR, outline=BORDER)
        try:
            img = Image.open("logoo.png").resize((20,20))
            self.logo = ImageTk.PhotoImage(img)
            self.canvas.create_image(20, H-20, image=self.logo)
        except:
            self.canvas.create_text(20, H-20, text="OS", fill=ACCENT)

        # ── نعرض الـ role في الـ taskbar
        self.canvas.create_text(W//2, H-20, text=f"Logged in as: {ROLE}",
                                fill=SUB, font=("Courier", 8))

        self.clock_id = self.canvas.create_text(
            60, H-20, text="", fill=SUB, anchor="w", font=("Courier",8))

        logout_btn = tk.Button(self.root, text="⏻ Logout", bg=TASKBAR,
                               fg="#ef4444", bd=0, font=("Segoe UI",9,"bold"),
                               cursor="hand2", command=self.logout)
        self.canvas.create_window(W-80, H-20, window=logout_btn)

    def draw_header(self):
        self.canvas.create_text(W//2, 45, text="Welcome to Frosted OS",
                                font=("Georgia",16,"bold"), fill=ACCENT)

    def spawn(self):
        start = W//2 - 170
        for i, app in enumerate(APPS):
            AppCard(self.canvas, self.root, start + i*180, H//2, app, i*120)

    def update_clock(self):
        now = datetime.datetime.now()
        self.canvas.itemconfig(self.clock_id, text=now.strftime("%I:%M:%S %p"))
        self.root.after(1000, self.update_clock)

    def fade(self, a=0.0):
        a += 0.05
        self.root.attributes("-alpha", min(a,1))
        if a < 1:
            self.root.after(20, lambda: self.fade(a))

    def logout(self):
        for proc in _open_procs:
            try:
                proc.terminate()
            except:
                pass
        _open_procs.clear()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    FilePage().run()