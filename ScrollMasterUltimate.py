import sys
import os
import threading
import ctypes
import winreg
import tkinter as tk
from tkinter import ttk, messagebox
from pynput import mouse
import pyautogui
import pystray
from PIL import Image, ImageDraw

# ===================== 配置 =====================
CONFIG = {
    "scroll_speed": 12,
    "horizontal_speed": 8,
    "auto_startup": True
}

is_mid_pressed = False
start_x = 0
start_y = 0
tray_icon = None
root = None
# ==================================================

def hide_console():
    if sys.platform == "win32":
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)

def set_autostart(enable):
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        name = "ScrollMasterUltimate"
        path = os.path.abspath(sys.argv[0])
        if enable:
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, path)
        else:
            try:
                winreg.DeleteValue(key, name)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        CONFIG["auto_startup"] = enable
    except:
        pass

def on_click(x, y, button, pressed):
    global is_mid_pressed, start_x, start_y
    if button == mouse.Button.middle:
        is_mid_pressed = pressed
        if pressed:
            start_x, start_y = x, y

def on_move(x, y):
    if not is_mid_pressed:
        return
    dx = x - start_x
    dy = y - start_y
    if abs(dy) > 2:
        pyautogui.scroll(-dy // CONFIG["scroll_speed"])
    if abs(dx) > 2:
        pyautogui.hscroll(dx // CONFIG["horizontal_speed"])

def create_icon_image():
    img = Image.new('RGB', (64, 64), color=(30, 30, 30))
    d = ImageDraw.Draw(img)
    d.ellipse([16, 16, 48, 48], fill=(80, 180, 255))
    return img

def quit_app(icon=None, item=None):
    if tray_icon:
        tray_icon.stop()
    os._exit(0)

def show_window(icon=None, item=None):
    if root:
        root.deiconify()

def setup_tray():
    global tray_icon
    menu = (
        pystray.MenuItem("打开设置", show_window),
        pystray.MenuItem("退出", quit_app),
    )
    tray_icon = pystray.Icon(
        "ScrollMasterUltimate",
        create_icon_image(),
        "鼠标中键自由滚动",
        menu
    )
    tray_icon.run()

def save_settings():
    try:
        v_speed = int(vertical_speed_var.get())
        h_speed = int(horizontal_speed_var.get())
        auto = auto_start_var.get()
        CONFIG["scroll_speed"] = v_speed
        CONFIG["horizontal_speed"] = h_speed
        set_autostart(auto)
        messagebox.showinfo("保存", "设置已保存！")
    except:
        messagebox.showerror("错误", "请输入数字")

def minimize_to_tray():
    root.withdraw()

def create_gui():
    global root, vertical_speed_var, horizontal_speed_var, auto_start_var
    root = tk.Tk()
    root.title("ScrollMaster Ultimate - 中键自由滚动")
    root.geometry("350x220")
    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", minimize_to_tray)

    ttk.Label(root, text="垂直滚动速度（越小越快）", font=("微软雅黑", 10)).pack(pady=5)
    vertical_speed_var = tk.StringVar(value=str(CONFIG["scroll_speed"]))
    ttk.Entry(root, textvariable=vertical_speed_var, width=10).pack()

    ttk.Label(root, text="水平滚动速度（越小越快）", font=("微软雅黑", 10)).pack(pady=5)
    horizontal_speed_var = tk.StringVar(value=str(CONFIG["horizontal_speed"]))
    ttk.Entry(root, textvariable=horizontal_speed_var, width=10).pack()

    auto_start_var = tk.BooleanVar(value=CONFIG["auto_startup"])
    ttk.Checkbutton(root, text="开机自启", variable=auto_start_var).pack(pady=5)

    ttk.Button(root, text="保存设置", command=save_settings).pack(pady=8)
    ttk.Label(root, text="关闭窗口将最小化到托盘", foreground="gray").pack()

    root.mainloop()

def main():
    hide_console()
    pyautogui.FAILSAFE = False
    set_autostart(CONFIG["auto_startup"])

    threading.Thread(target=setup_tray, daemon=True).start()
    threading.Thread(target=lambda: mouse.Listener(on_click=on_click, on_move=on_move).start(), daemon=True).start()

    create_gui()

if __name__ == "__main__":
    main()
