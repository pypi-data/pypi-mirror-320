import time
import threading
import win32gui
import win32con
import keyboard


def find_chrome_window():

    def enum_handler(hwnd, results):
        title = win32gui.GetWindowText(hwnd)
        if "Chrome" in title:
            results.append(hwnd)

    windows = []
    win32gui.EnumWindows(enum_handler, windows)
    return windows[0] if windows else None


def toggle_chrome_window():
    hwnd = find_chrome_window()
    if hwnd is None:
        print("Окно Chrome не найдено!")
        return

    if win32gui.IsWindowVisible(hwnd):
        print("Скрываем окно Chrome")
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
    else:
        print("Показываем окно Chrome")
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)


def runner():
    print("Скрытый раннер запущен. Нажмите CTRL+Пробел для переключения окна Chrome.")
    keyboard.add_hotkey("ctrl+space", toggle_chrome_window)
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Остановка фонового процесса.")


def main():
    thread = threading.Thread(target=runner, daemon=True)
    thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Завершаем работу main().")
