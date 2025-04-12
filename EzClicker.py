import tkinter as tk
from tkinter import ttk
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Listener as KeyboardListener
import threading
import time

# === Global Variables ===
clicking = False
cps = 10
click_button = Button.left
hotkey = None
hotkey_str = "None"
click_count = 0
start_time = 0
overlay_window = None
mouse_controller = MouseController()

# === Overlay ===
def create_overlay():
    global overlay_window
    overlay_window = tk.Toplevel()
    overlay_window.overrideredirect(True)
    overlay_window.attributes('-topmost', True)
    overlay_window.attributes('-alpha', 0.85)
    overlay_window.configure(bg='black')
    overlay_window.geometry("180x80+20+20")

    overlay_window.status_label = tk.Label(overlay_window, text="OFF", fg="red", bg="black", font=("Segoe UI", 14, "bold"))
    overlay_window.status_label.pack(pady=(5, 0))

    overlay_window.cps_label = tk.Label(overlay_window, text="CPS: 0", fg="white", bg="black", font=("Segoe UI", 12))
    overlay_window.cps_label.pack()

    overlay_window.hotkey_label = tk.Label(overlay_window, text="", fg="gray", bg="black", font=("Segoe UI", 10))
    overlay_window.hotkey_label.pack(pady=(0, 5))

    overlay_window.withdraw()

def update_overlay():
    if overlay_window:
        overlay_window.status_label.config(text="ON" if clicking else "OFF", fg="lime" if clicking else "red")
        elapsed = time.time() - start_time if start_time > 0 else 1
        current_cps = round(click_count / elapsed, 1) if elapsed > 0 else 0
        overlay_window.cps_label.config(text=f"CPS: {current_cps:.1f}")
        overlay_window.hotkey_label.config(text=f"Hotkey: {hotkey_str}")
        overlay_window.deiconify()
        overlay_window.after(500, update_overlay)

# === Clicker Logic ===
def click_loop():
    global click_count, start_time
    while True:
        if clicking:
            click_count += 1
            mouse_controller.click(click_button)
            time.sleep(1 / cps)
        else:
            time.sleep(0.1)

# === Hotkey Listener ===
def on_key_press(key):
    global clicking, start_time, click_count
    if key == hotkey:
        clicking = not clicking
        if clicking:
            click_count = 0
            start_time = time.time()
        update_overlay()

def on_mouse_click(x, y, button, pressed):
    if pressed and button == hotkey:
        on_key_press(button)

def start_hotkey_listener():
    keyboard_listener = KeyboardListener(on_press=on_key_press)
    mouse_listener = mouse.Listener(on_click=on_mouse_click)
    keyboard_listener.daemon = True
    mouse_listener.daemon = True
    keyboard_listener.start()
    mouse_listener.start()

# === GUI ===
def readable_key(key):
    if isinstance(key, Key):
        return str(key).replace("Key.", "").capitalize()
    elif isinstance(key, Button):
        return {
            Button.left: "Mouse Left",
            Button.right: "Mouse Right",
            Button.middle: "Mouse Middle",
            Button.x_button1: "Mouse Side 1",
            Button.x_button2: "Mouse Side 2"
        }.get(key, str(key))
    else:
        return str(key).replace("'", "").upper()

def select_hotkey():
    status_label.config(text="Press a keyboard or mouse button...", foreground="orange")
    key_label.config(text="Hotkey: ...")
    window.update()

    listener_stopped = False  # Flag per evitare doppie assegnazioni

    def assign_hotkey(k):
        nonlocal listener_stopped
        if listener_stopped:
            return
        listener_stopped = True

        global hotkey, hotkey_str
        hotkey = k
        hotkey_str = readable_key(k)
        key_label.config(text=f"Hotkey: {hotkey_str}")
        status_label.config(text="Hotkey successfully set!", foreground="lime")

        # Ferma entrambi i listener
        k_listener.stop()
        m_listener.stop()

    def on_key(k):
        assign_hotkey(k)

    def on_click(x, y, button, pressed):
        if pressed:
            assign_hotkey(button)

    k_listener = KeyboardListener(on_press=on_key)
    m_listener = mouse.Listener(on_click=on_click)
    k_listener.start()
    m_listener.start()


# === UI Setup ===
window = tk.Tk()
window.title("EzClicker by @Luxy")
window.geometry("360x300")
window.configure(bg="#1e1e1e")

style = ttk.Style()
style.theme_use('default')
style.configure("TLabel", background="#1e1e1e", foreground="white", font=("Segoe UI", 11))
style.configure("TButton", background="#333", foreground="white", font=("Segoe UI", 11))
style.configure("TScale", background="#1e1e1e", troughcolor="#444", sliderlength=20)

# Title
ttk.Label(window, text="EzClicker by @Luxy", font=("Segoe UI", 16, "bold")).pack(pady=(15, 5))

# CPS Slider
frame_slider = tk.Frame(window, bg="#1e1e1e")
frame_slider.pack(pady=10)

ttk.Label(frame_slider, text="Clicks per second:").pack(side="left", padx=(0, 8))
cps_var = tk.StringVar(value="10")
cps_slider = ttk.Scale(frame_slider, from_=1, to=50, orient='horizontal', variable=cps_var,
                       command=lambda val: cps_val_label.config(text=f"{int(float(val))}"))
cps_slider.set(cps)
cps_slider.pack(side="left")
cps_val_label = ttk.Label(frame_slider, text=str(cps))
cps_val_label.pack(side="left", padx=5)

# Click Button Choice
ttk.Label(window, text="Click Button:").pack(pady=(10, 3))
click_button_var = tk.StringVar(value="left")
click_button_dropdown = ttk.Combobox(window, textvariable=click_button_var, values=["left", "right"], state="readonly", font=("Segoe UI", 11))
click_button_dropdown.pack()

def update_click_button(*args):
    global click_button
    click_button = Button.left if click_button_var.get() == "left" else Button.right

click_button_var.trace("w", update_click_button)

# Hotkey Selector
ttk.Button(window, text="Set Activation Hotkey", command=select_hotkey).pack(pady=(15, 5))
key_label = ttk.Label(window, text=f"Hotkey: {hotkey_str}")
key_label.pack()

# Status
status_label = ttk.Label(window, text="Ready", foreground="white")
status_label.pack(pady=10)

# Update Loop
def update_cps():
    global cps
    cps = int(float(cps_slider.get()))
    window.after(100, update_cps)

update_cps()
create_overlay()
threading.Thread(target=click_loop, daemon=True).start()
start_hotkey_listener()

window.mainloop()
