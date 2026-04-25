import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import subprocess
import sys

# Login process
from process_api import spawn_process, finish_process

BG_COLOR     = "#f5f7fb"
CARD_COLOR   = "#ffffff"
BORDER_COLOR = "#e2e8f0"
FG_COLOR     = "#1f2937"
SUB_COLOR    = "#64748b"
ACCENT       = "#3b82f6"
ACCENT_HOT   = "#2563eb"
INPUT_BG     = "#f8fafc"
INPUT_BORDER = "#cbd5e1"
INPUT_FOCUS  = "#3b82f6"
ERROR_COLOR  = "#ef4444"

FONT_LABEL  = ("Courier", 10)
FONT_INPUT  = ("Segoe UI", 11)
FONT_BTN    = ("Georgia", 12, "bold")

W, H = 850, 650

users = {
    "admin": {"password": "123", "role": "ADMIN"},
    "user":  {"password": "123", "role": "USER"},
    "guest": {"password": "123", "role": "GUEST"},
}


class LoginScreen:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Frosted — Login")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)
        self.root.attributes("-alpha", 0.0)

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")

        self.canvas = tk.Canvas(self.root, width=W, height=H,
                                bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack()

        self._draw_card()
        self._build_widgets()
        self._fade_in()

    # ───────── CARD ─────────
    def _draw_card(self):
        cx, cy = W // 2, H // 2
        cw, ch = 360, 430
        x0, y0 = cx - cw // 2, cy - ch // 2
        x1, y1 = cx + cw // 2, cy + ch // 2
        r = 18

        self.canvas.create_rectangle(x0+8, y0+10, x1+8, y1+10,
                                     fill="#e2e8f0", outline="")

        self.canvas.create_rectangle(x0+r, y0, x1-r, y1,
                                     fill=CARD_COLOR, outline="")
        self.canvas.create_rectangle(x0, y0+r, x1, y1-r,
                                     fill=CARD_COLOR, outline="")

        for ox, oy in [(x0, y0), (x1-2*r, y0),
                       (x0, y1-2*r), (x1-2*r, y1-2*r)]:
            self.canvas.create_oval(ox, oy, ox+2*r, oy+2*r,
                                    fill=CARD_COLOR, outline="")

        self.canvas.create_rectangle(x0, y0, x1, y1,
                                     outline=BORDER_COLOR)

    # ───────── UI ─────────
    def _build_widgets(self):
        cx = W // 2

        container = tk.Frame(self.root, bg=CARD_COLOR)
        self.canvas.create_window(cx, H//2 + 10, window=container)

        # ── LOGO ──
        self.logo_canvas = tk.Canvas(container, width=90, height=90,
                                     bg=CARD_COLOR, highlightthickness=0)
        self.logo_canvas.pack(pady=(0, 15))

        try:
            img = Image.open("logoo.png").convert("RGBA")
            img = img.resize((70, 70), Image.Resampling.LANCZOS)

            mask = Image.new("L", (70, 70), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, 70, 70), fill=255)
            img.putalpha(mask)

            self.logo_img = ImageTk.PhotoImage(img)

            self.logo_canvas.create_oval(10, 10, 80, 80,
                                          fill="#e2e8f0", outline="")
            self.logo_canvas.create_image(45, 45, image=self.logo_img)

        except:
            self.logo_canvas.create_text(
                45, 45,
                text="F",
                font=("Georgia", 28, "bold"),
                fill=ACCENT
            )

        # USERNAME
        tk.Label(container, text="USERNAME",
                 font=FONT_LABEL, bg=CARD_COLOR,
                 fg=SUB_COLOR).pack(anchor="w")

        self.entry_user = self._make_entry(container)
        self.entry_user.pack(fill="x", pady=(4, 14))

        # PASSWORD
        tk.Label(container, text="PASSWORD",
                 font=FONT_LABEL, bg=CARD_COLOR,
                 fg=SUB_COLOR).pack(anchor="w")

        self.entry_pass = self._make_entry(container, show="•")
        self.entry_pass.pack(fill="x", pady=(4, 22))

        # BUTTON
        tk.Button(
            container,
            text="SIGN IN",
            font=FONT_BTN,
            bg=ACCENT,
            fg="white",
            activebackground=ACCENT_HOT,
            relief="flat",
            cursor="hand2",
            command=self.login
        ).pack(fill="x", ipady=10)

        # ERROR
        self.lbl_error = tk.Label(container, text="",
                                   font=FONT_LABEL,
                                   bg=CARD_COLOR,
                                   fg=ERROR_COLOR)
        self.lbl_error.pack(pady=10)

        self.entry_user.bind("<Return>", lambda e: self.entry_pass.focus())
        self.entry_pass.bind("<Return>", self.login)

        self.entry_user.focus()

    def _make_entry(self, parent, show=None):
        return tk.Entry(
            parent,
            font=FONT_INPUT,
            bg=INPUT_BG,
            fg=FG_COLOR,
            insertbackground=FG_COLOR,
            relief="flat",
            highlightthickness=1,
            highlightbackground=INPUT_BORDER,
            highlightcolor=INPUT_FOCUS,
            show=show or ""
        )

    # ───────── LOGIN ─────────
    def login(self, event=None):
        u = self.entry_user.get()
        p = self.entry_pass.get()

        if u in users and users[u]["password"] == p:

            login_proc = spawn_process("Login", burst_time=2, memory_size=16)


            def on_finish():
                if login_proc:
                    finish_process(login_proc.pid)
                self._fade_out()

            self.root.after(2000, on_finish)
        else:
            self.lbl_error.config(text="Invalid username or password")
            self.root.after(2000, lambda: self.lbl_error.config(text=""))

    # ───────── ANIMATION ─────────
    def _fade_in(self, a=0.0):
        a += 0.05
        self.root.attributes("-alpha", min(a, 1.0))
        if a < 1:
            self.root.after(20, lambda: self._fade_in(a))

    def _fade_out(self, a=1.0):
        if a > 0:
            a -= 0.06
            self.root.attributes("-alpha", max(a, 0.0))
            self.root.after(15, lambda: self._fade_out(a))
        else:
            self.root.withdraw()
            subprocess.Popen([sys.executable, "home.py"])

    def run(self):
        self._fade_in()
        self.root.mainloop()


if __name__ == "__main__":
    LoginScreen().run()