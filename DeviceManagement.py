import time
import threading
import tkinter as tk

# ── Theme ─────────────────────────────
BG    = "#f5f7fb"
CARD  = "#ffffff"
BORDER= "#e2e8f0"
FG    = "#1f2937"
SUB   = "#64748b"
ACCENT= "#3b82f6"
GREEN = "#10b981"
RED   = "#ef4444"

W, H = 850, 650


# ───────────────────────── Device ─────────────────────────
class IODevice:
    def __init__(self, name, log_callback):
        self.name = name
        self.status = "Available"
        self.log = log_callback

    def send_request(self, task, duration):
        if self.status == "Busy":
            return

        threading.Thread(
            target=self.process,
            args=(task, duration),
            daemon=True
        ).start()

    def process(self, task, duration):
        self.status = "Busy"
        self.log(f"{self.name} started {task}")

        steps = 5
        for i in range(steps):
            time.sleep(duration / steps)
            self.log(f"{self.name} processing... {int((i+1)/steps*100)}%")

        self.log(f"{self.name} finished {task}")
        self.status = "Available"


# ───────────────────────── UI ─────────────────────────
class DeviceManagerUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Device Manager - Frosted OS")
        self.root.geometry(f"{W}x{H}")
        self.root.configure(bg=BG)

        # Header
        tk.Label(
            self.root,
            text="Device Manager",
            font=("Georgia", 18, "bold"),
            bg=BG,
            fg=ACCENT
        ).pack(pady=15)

        # Devices Frame
        self.devices_frame = tk.Frame(self.root, bg=BG)
        self.devices_frame.pack()

        # Log box
        self.log_box = tk.Listbox(
            self.root,
            height=10,
            bg="white",
            fg=FG,
            highlightthickness=1,
            highlightbackground=BORDER
        )
        self.log_box.pack(fill="both", padx=20, pady=10)

        # Devices (NOW SIDE BY SIDE)
        self.devices = {}
        self.create_device("Keyboard", "Typing Input", 3, 0, 0)
        self.create_device("Printer", "Print Document", 5, 0, 1)

        self.root.mainloop()

    # ───────────────────────── Log ─────────────────────────
    def add_log(self, text):
        self.log_box.insert(0, text)

    # ───────────────────────── Device Row ─────────────────────────
    def create_device(self, name, task, duration, row, col):
        frame = tk.Frame(
            self.devices_frame,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1,
            padx=20,
            pady=15
        )
        frame.grid(row=row, column=col, pady=10, padx=20, sticky="n")

        title = tk.Label(frame, text=name, font=("Georgia", 12, "bold"),
                         bg=CARD, fg=FG)
        title.grid(row=0, column=0, sticky="w")

        status = tk.Label(frame, text="Available",
                          font=("Courier", 10),
                          bg=CARD, fg=GREEN)
        status.grid(row=1, column=0, sticky="w")

        activity = tk.Label(frame, text="Idle",
                            font=("Courier", 10),
                            bg=CARD, fg=SUB)
        activity.grid(row=2, column=0, sticky="w", pady=5)

        btn = tk.Button(
            frame,
            text=f"Start {name}",
            bg=ACCENT,
            fg="white",
            relief="flat",
            cursor="hand2",
            command=lambda: self.run_device(name, task, duration)
        )
        btn.grid(row=0, column=1, rowspan=3, padx=20)

        self.devices[name] = {
            "status": status,
            "activity": activity,
            "task": task,
            "duration": duration
        }

    # ───────────────────────── Run Device ─────────────────────────
    def run_device(self, name, task, duration):
        device_ui = self.devices[name]

        device = IODevice(name, self.add_log)

        def update_ui():
            status = device.status
            device_ui["status"].config(
                text=status,
                fg=GREEN if status == "Available" else RED
            )

        def live_activity():
            device.status = "Busy"

            steps = [
                "Starting...",
                "Loading drivers...",
                "Processing...",
                "Working...",
                "Finalizing..."
            ]

            for i, step in enumerate(steps):
                device_ui["activity"].config(text=step)
                self.root.update()
                time.sleep(duration / len(steps))

            device_ui["activity"].config(text="Done ✔")
            self.add_log(f"{name} completed successfully")

            time.sleep(1)
            device_ui["activity"].config(text="Idle")

            device.status = "Available"
            update_ui()

        threading.Thread(target=live_activity, daemon=True).start()


# ───────────────────────── Run ─────────────────────────
if __name__ == "__main__":
    DeviceManagerUI()