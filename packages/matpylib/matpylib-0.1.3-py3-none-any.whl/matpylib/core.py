import time
import threading
import win32gui
import win32con
import keyboard

# Флаг для остановки фонового процесса
_stop_flag = False

def find_chrome_window():
    """
    Ищет окно, заголовок которого содержит 'Chrome'.
    Поиск производится по всем окнам, независимо от видимости.
    """
    def enum_handler(hwnd, results):
        title = win32gui.GetWindowText(hwnd)
        if "Chrome" in title:
            results.append(hwnd)
    windows = []
    win32gui.EnumWindows(enum_handler, windows)
    return windows[0] if windows else None

def toggle_chrome_window():
    """
    Переключает видимость окна Chrome:
      - Если окно видно, скрывает его;
      - Если окно скрыто, показывает и восстанавливает его.
    """
    hwnd = find_chrome_window()
    if hwnd is None:
        return

    if win32gui.IsWindowVisible(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
    else:
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

def stop_runner():
    """
    Устанавливает флаг остановки фонового процесса.
    После этого бесконечный цикл в runner завершится.
    """
    global _stop_flag
    _stop_flag = True
    # Удаляем все зарегистрированные горячие клавиши
    keyboard.unhook_all_hotkeys()

def runner():
    """
    Фоновый процесс.
    Горячая клавиша CTRL+Пробел переключает видимость окна Chrome.
    Горячая клавиша CTRL+ALT+Пробел отключает (останавливает) данный процесс.
    """
    # Регистрируем горячие клавиши без вывода информации в консоль
    keyboard.add_hotkey("ctrl+space", toggle_chrome_window)
    keyboard.add_hotkey("ctrl+alt+space", stop_runner)
    while not _stop_flag:
        time.sleep(0.1)

def main():
    """
    Основная точка входа для команды matpylibrun.
    Фоновый runner запускается в отдельном демоне, основной поток остается активен.
    """
    thread = threading.Thread(target=runner, daemon=True)
    thread.start()
    while not _stop_flag:
        time.sleep(1)
