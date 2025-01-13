from simple_term_menu import TerminalMenu

class SimpleTUI:
    """TUI parts using library simple_term_menu"""
    def __init__(self):
        pass

    def choose_menu(self, menu_title, choices):
        """ Dynamic function to display content of a list and returnes which was selected."""
        menu_options = choices
        menu = TerminalMenu(
            menu_entries = menu_options,
            title = menu_title,
            menu_cursor = "> ",
            menu_cursor_style = ("fg_gray", "bold"),
            menu_highlight_style = ("bg_gray", "fg_black"),
            cycle_cursor = True,
            clear_screen = False
        )
        menu.show()
        return menu.chosen_menu_entry

    def multi_select_menu(self, menu_title, choices):
        """ Dynamic function to display content of a list and returnes which was selected."""
        menu_options = choices
        menu = TerminalMenu(
            menu_entries = menu_options,
            title = menu_title,
            multi_select=True,
            show_multi_select_hint=True,
            menu_cursor_style = ("fg_gray", "bold"),
            menu_highlight_style = ("bg_gray", "fg_black"),
            cycle_cursor = True,
            clear_screen = False
        )
        menu.show()
        choisen_values = menu.chosen_menu_entries

        if choisen_values == None:
            print("Exiting...")
            exit()
        else:
            return menu.chosen_menu_entries

    def yes_no_menu(self, message): # oh
            menu_options = ["[y] yes", "[n] no"]
            menu = TerminalMenu(
                menu_entries = menu_options,
                title = f"{message}",
                menu_cursor = "> ",
                menu_cursor_style = ("fg_red", "bold"),
                menu_highlight_style = ("bg_gray", "fg_black"),
                cycle_cursor = True,
                clear_screen = False
            )
            menu_entry_index = menu.show()
            if menu_entry_index == 0:
                return True
            elif menu_entry_index == 1:
                return False
