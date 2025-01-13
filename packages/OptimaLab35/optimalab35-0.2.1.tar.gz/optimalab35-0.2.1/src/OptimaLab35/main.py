import os
from argparse import ArgumentParser
from OptimaLab35 import gui, __version__

# Try importing TUI only if simple-term-menu is installed
try:
    from OptimaLab35 import tui
    simple_term_menu_installed = True
except ImportError:
    simple_term_menu_installed = False

# Check if PySide is installed
def check_pyside_installed():
    try:
        import PySide6  # Replace with PySide2 if using that version
        return True
    except ImportError:
        return False

def start_gui():
    gui.main()

def start_tui():
    if simple_term_menu_installed:
        tui.main()
    else:
        print("Error: simple-term-menu is not installed. Please install it to use the TUI mode.")
        exit(1)

def main():
    parser = ArgumentParser(description="Start the Optima35 application.")
    parser.add_argument("--tui", action="store_true", help="Start in terminal UI mode.")
    args = parser.parse_args()

    if args.tui:
        print("Starting TUI...")
        start_tui()
        return

    # Check OS and start GUI if on Windows
    if os.name == "nt":
        print("Detected Windows. Starting GUI...")
        start_gui()
    else:
        # Non-Windows: Check if PySide is installed
        if check_pyside_installed():
            print("PySide detected. Starting GUI...")
            start_gui()
        else:
            print("PySide is not installed. Falling back to TUI...")
            start_tui()

if __name__ == "__main__":
    main()
