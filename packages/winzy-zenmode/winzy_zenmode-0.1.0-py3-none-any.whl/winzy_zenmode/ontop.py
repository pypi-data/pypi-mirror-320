import ctypes
import time
from ctypes import wintypes
import argparse
from datetime import datetime, timedelta


def parse_time(time_str):
    """Convert time string with units (s/m/h) to seconds"""
    unit = time_str[-1].lower()
    value = float(time_str[:-1])

    if unit == "s":
        return value
    elif unit == "m":
        return value * 60
    elif unit == "h":
        return value * 3600
    else:
        raise ValueError("Time must end with s, m, or h (e.g., 30s, 5m, 1h)")


def list_open_windows():
    """
    Lists all open window titles on the system and allows the user to select one.

    Returns:
    - str: The title of the selected window.
    """
    user32 = ctypes.windll.user32
    titles = []

    def enum_window_proc(hwnd, lParam):
        # Callback function to list window titles
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buffer = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buffer, length + 1)
                titles.append(buffer.value)
        return True

    # Set up callback function type
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    enum_windows = user32.EnumWindows
    enum_windows(EnumWindowsProc(enum_window_proc), 0)

    # Display the list of windows to the user
    if not titles:
        raise RuntimeError("No open windows found.")

    print("\nList of open windows:")
    for idx, title in enumerate(titles, start=1):
        print(f"{idx}: {title}")

    # Let the user choose a window
    choice = input("\nEnter the number of the window you want to keep on top: ")
    choice = [int(c) - 1 for c in choice.split(" ")]
    return [titles[i] for i in choice]


def minimize_other_windows(target_hwnd):
    user32 = ctypes.windll.user32

    def enum_window_proc(hwnd, lParam):
        if hwnd != target_hwnd and user32.IsWindowVisible(hwnd):
            user32.ShowWindow(hwnd, 6)  # 6 is SW_MINIMIZE
        return True

    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    enum_windows = user32.EnumWindows
    enum_windows(EnumWindowsProc(enum_window_proc), 0)


def keep_window_on_top(window_title=None, duration="1m"):
    """
    Keeps a specified window on top for a specified duration. If no title is provided,
    lists open windows for the user to choose.

    Parameters:
    - window_title (str): Title of the target window. If None, prompts user to select.
    - duration (str): Duration to keep the window on top.

    """
    user32 = ctypes.windll.user32

    # If no title is provided, list open windows for the user to select
    if not window_title:
        titles = list_open_windows()

    # Convert duration to seconds
    duration_in_seconds = parse_time(duration)

    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=duration_in_seconds)

    print(f"Starting ontop at {start_time.strftime('%H:%M:%S')}")
    print(f"You can only use '{window_title}' until {end_time.strftime('%H:%M:%S')}")
    print("Press Ctrl+C to stop\n")

    # Define necessary ctypes
    FindWindow = user32.FindWindowW
    GetForegroundWindow = user32.GetForegroundWindow
    ShowWindow = user32.ShowWindow

    SW_MIMIMIZE = 6

    # Locate the window

    hwnd = [FindWindow(None, window_title) for window_title in titles]
    if not hwnd:
        raise ValueError(f"Window with title '{window_title}' not found.")

    # Keep the window on top for the specified duration
    end_time = time.time() + duration_in_seconds
    try:
        while time.time() < end_time:
            thiswin = GetForegroundWindow()
            if thiswin not in hwnd:  # If not the active window
                ShowWindow(thiswin, SW_MIMIMIZE)
            time.sleep(1)  # Check every 100ms to avoid high CPU usage
    except KeyboardInterrupt:
        print("\nOperation canceled by user.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Keep a window on top for a specified duration."
    )
    parser.add_argument(
        "-d",
        "--duration",
        type=str,
        default="1m",
        help="Duration to keep the window on top 1m, 30s, 1h ",
    )
    args = parser.parse_args()
    try:
        keep_window_on_top(duration=args.duration)
    except ValueError as e:
        print(str(e))
