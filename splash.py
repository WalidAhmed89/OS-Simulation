import os
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class SplashScreen:
    def __init__(self):
        self.splash = tk.Tk()
        self.splash.overrideredirect(True)

        self.bg_color = "#f5f7fb"
        self.splash.configure(bg=self.bg_color)
        self.splash.attributes("-alpha", 0.0)

        self.WIDTH = 850
        self.HEIGHT = 650

        screen_w = self.splash.winfo_screenwidth()
        screen_h = self.splash.winfo_screenheight()
        x = (screen_w - self.WIDTH) // 2
        y = (screen_h - self.HEIGHT) // 2
        self.splash.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}")

        self.canvas = tk.Canvas(
            self.splash,
            width=self.WIDTH,
            height=self.HEIGHT,
            bg=self.bg_color,
            highlightthickness=0,
        )
        self.canvas.pack()

        self._load_logo()
        self._draw_text()
        self._draw_progress_bar()
        self._draw_version()

        self.fade_in()

    def _draw_background(self):
        pass

    def _draw_glow(self):
        pass

    def _load_logo(self):
        cx, cy = self.WIDTH // 2, self.HEIGHT // 2 - 40

        self.canvas.create_oval(
            cx - 88, cy - 88,
            cx + 88, cy + 88,
            fill="#e2e8f0",
            outline=""
        )

        self.canvas.create_oval(
            cx - 80, cy - 80,
            cx + 80, cy + 80,
            fill="#f5f7fb",
            outline=""
        )

        try:
            img = Image.open("logoo.png").convert("RGBA")
            img = img.resize((110, 110), Image.Resampling.LANCZOS)

            mask = Image.new("L", (110, 110), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, 110, 110), fill=255)
            img.putalpha(mask)

            self.logo_img = ImageTk.PhotoImage(img)
            self.canvas.create_image(cx, cy, image=self.logo_img)

        except Exception:
            self.canvas.create_text(
                cx, cy,
                text="✦",
                font=("Georgia", 48),
                fill="#3b82f6"
            )

    def _draw_text(self):
        cx = self.WIDTH // 2
        baseline_y = self.HEIGHT // 2 + 60

        # shadow
        self.canvas.create_text(
            cx + 1, baseline_y + 1,
            text="Frosted",
            font=("Georgia", 30, "bold"),
            fill="#cbd5e1",
            anchor="center"
        )

        # main text
        self.canvas.create_text(
            cx, baseline_y,
            text="Frosted",
            font=("Georgia", 30, "bold"),
            fill="#1f2937",
            anchor="center"
        )

        # subtitle
        self.canvas.create_text(
            cx, baseline_y + 36,
            text="A C L E A R   V I S I O N",
            font=("Courier", 10),
            fill="#64748b",
            anchor="center"
        )

    def _draw_progress_bar(self):
        bar_y = self.HEIGHT - 80
        bar_w = 360
        bar_h = 7

        bx = (self.WIDTH - bar_w) // 2

        # background
        self.canvas.create_rectangle(
            bx, bar_y, bx + bar_w, bar_y + bar_h,
            fill="#e2e8f0",
            outline=""
        )

        # progress
        self.prog_bar = self.canvas.create_rectangle(
            bx, bar_y, bx, bar_y + bar_h,
            fill="#3b82f6",
            outline=""
        )

        # glow
        self.prog_glow = self.canvas.create_rectangle(
            bx, bar_y - 2, bx, bar_y + bar_h + 2,
            fill="#93c5fd",
            outline=""
        )

        self.bar_x = bx
        self.bar_max_w = bar_w
        self.bar_y = bar_y
        self.bar_h = bar_h

        # status text
        self.status_text = self.canvas.create_text(
            self.WIDTH // 2,
            bar_y + 28,
            text="Initializing…",
            font=("Courier", 11, "bold"),
            fill="#475569"
        )

    def _draw_version(self):
        self.canvas.create_text(
            self.WIDTH - 16, self.HEIGHT - 12,
            text="v1.0.0",
            font=("Courier", 8),
            fill="#94a3b8",
            anchor="se"
        )

    # ───────── ANIMATION ─────────

    def fade_in(self, alpha=0.0):
        alpha += 0.05
        self.splash.attributes("-alpha", min(alpha, 1.0))
        if alpha < 1.0:
            self.splash.after(25, lambda: self.fade_in(alpha))
        else:
            self.animate_progress()

    def animate_progress(self):
        messages = [
            "Loading resources…",
            "Preparing interface…",
            "Almost ready…",
            "Welcome."
        ]

        def step(value=0):
            if value > 100:
                self.splash.after(300, self.fade_out)
                return

            bx = self.bar_x
            filled = int(self.bar_max_w * value / 100)

            self.canvas.coords(
                self.prog_bar,
                bx, self.bar_y,
                bx + filled, self.bar_y + self.bar_h
            )

            self.canvas.coords(
                self.prog_glow,
                bx + filled - 3, self.bar_y - 2,
                bx + filled, self.bar_y + self.bar_h + 2
            )

            msg_index = min(int(value / 26), len(messages) - 1)
            self.canvas.itemconfig(
                self.status_text,
                text=messages[msg_index]
            )

            self.splash.after(20, lambda: step(value + 1))

        step()

    def fade_out(self, alpha=1.0):
        alpha -= 0.06
        self.splash.attributes("-alpha", max(alpha, 0.0))

        if alpha > 0:
            self.splash.after(20, lambda: self.fade_out(alpha))
        else:
            self.splash.destroy()
            subprocess.Popen([sys.executable, os.path.join(BASE_DIR, "login.py")])

    def run(self):
        self.splash.mainloop()


if __name__ == "__main__":
    SplashScreen().run()