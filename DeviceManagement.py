import time
import threading
import tkinter as tk


class IODevice:
    def __init__(self, name):
        self.name = name
        self.status = "Available"

    def send_request(self, task_name, duration):
        if self.status == "Busy":
            print(f"{self.name} is currently Busy. Try again later.")
            return

        thread = threading.Thread(target=self.process_task, args=(task_name, duration))
        thread.start()

    def process_task(self, task_name, duration):
        self.status = "Busy"
        print(f"{self.name} started task: {task_name}")

        time.sleep(duration)

        print(f"{self.name} finished task: {task_name}")
        self.status = "Available"

    def get_status(self):
        return f"{self.name}: {self.status}"


# Devices
keyboard = IODevice("Keyboard")
printer = IODevice("Printer")


# GUI
root = tk.Tk()
root.title("Device Manager")
root.geometry("400x250")
root.configure(bg="#1e1e1e")


# Labels
keyboard_label = tk.Label(root, text=keyboard.get_status(),
                          fg="white", bg="#1e1e1e", font=("Arial", 12))
keyboard_label.pack(pady=10)

printer_label = tk.Label(root, text=printer.get_status(),
                         fg="white", bg="#1e1e1e", font=("Arial", 12))
printer_label.pack(pady=10)


# Buttons
def send_keyboard():
    keyboard.send_request("Typing Input", 3)


def send_printer():
    printer.send_request("Print Document", 5)


keyboard_btn = tk.Button(root, text="Use Keyboard",
                         command=send_keyboard,
                         bg="#4CAF50", fg="white", width=20)
keyboard_btn.pack(pady=5)

printer_btn = tk.Button(root, text="Use Printer",
                        command=send_printer,
                        bg="#2196F3", fg="white", width=20)
printer_btn.pack(pady=5)


# تحديث الحالة كل ثانية
def update_status():
    keyboard_label.config(text=keyboard.get_status())
    printer_label.config(text=printer.get_status())
    root.after(1000, update_status)


update_status()

root.mainloop()