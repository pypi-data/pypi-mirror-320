# main.py

import os
import curses
import subprocess
import sys

script_dir = os.path.dirname(os.path.realpath(__file__))
CATEGORY_DIR = os.path.join(script_dir, 'categories')


def create_category_directory():
    """Create the categories directory if it doesn't exist."""
    if not os.path.exists(CATEGORY_DIR):
        os.makedirs(CATEGORY_DIR)


def add_category(category_name):
    """Add a category by creating a file with the category name."""
    file_path = os.path.join(CATEGORY_DIR, f"{category_name}.txt")
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write("")  # Optional: add initial content
    return category_name


def remove_category(category_name):
    """Remove a category by deleting the file with the category name."""
    file_path = os.path.join(CATEGORY_DIR, f"{category_name}.txt")
    if os.path.exists(file_path):
        os.remove(file_path)
        return category_name
    return category_name


def get_categories():
    """Retrieve the list of categories from the directory."""
    return [f[:-4] for f in os.listdir(CATEGORY_DIR) if f.endswith('.txt')]


def add_line(filename, new_line):
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(new_line + '\n')  # Append new line with a newline character


def remove_line(filename, line_number):
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Check if the line number is valid
    if 0 <= line_number <= len(lines):
        del lines[line_number]

    # Write back to the file without leaving any blank spaces
    with open(filename, 'w', encoding='utf-8') as file:
        file.writelines(lines)


def read_file_to_array(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:  # Open the file in read mode
            lines = file.readlines()  # Read all lines into a list
        # Strip newline characters from each line
        return [line.strip() for line in lines]
    except FileNotFoundError as e:
        print(f"The file {file_path} was not found: {e}")
        return None


def execute_command(option):
    stdscr = curses.initscr()

    # Example command execution based on the selected option.
    stdscr.addstr(f"You selected: {option}\n")
    commands = read_file_to_array(os.path.join(CATEGORY_DIR, f"{option}.txt"))
    display_menu(stdscr, commands, run_command, None)
    stdscr.refresh()
    stdscr.getch()  # Wait for a key press to allow the user to see the message


def display_output(stdscr, output):
    """Display command output in the curses window."""
    stdscr.clear()  # Clear the screen
    for line in output:
        stdscr(line + '\n')
        # stdscr.addstr(line + '\n')  # Add each line followed by a newline
    stdscr.refresh()  # Refresh to show the updated content
    stdscr.getch()  # Wait for a key press


def display_menu1(stdscr, options, selected):
    stdscr.clear()  # Clear the screen
    stdscr.addstr(
        "Select a command category (Use arrow keys and press Enter):\n\n")

    for idx, option in enumerate(options):
        if idx == selected:
            # Highlight selected option
            stdscr.addstr(f"> {option}\n", curses.A_REVERSE)
        else:
            stdscr.addstr(f"  {option}\n")

    stdscr.refresh()  # Refresh the screen to show changes


def display_menu(stdscr, options, execute_function, types):
    """
    Display a menu using curses, allowing the user to navigate with arrow keys
    and execute a command based on the selected option.

    :param stdscr: The window object from curses.
    :param options: A list of options to display in the menu.
    :param execute_function: A function to execute when an option is selected.
    """
    selected = 0  # Track the currently selected option
    num_options = len(options)

    while True:
        stdscr.clear()  # Clear the screen for redrawing the menu
        stdscr.addstr(
            "Select an option (Use arrow keys and press Enter): \n\n")
        for idx, option in enumerate(options):
            if idx == selected:
                # Highlight selected option
                stdscr.addstr(f"> {option}\n", curses.A_REVERSE)
            else:
                stdscr.addstr(f"  {option}\n")

        stdscr.refresh()  # Refresh to show the updated menu

        key = stdscr.getch()  # Wait for user input

        if key == curses.KEY_UP:  # Move up in the menu
            selected = (selected - 1) % num_options
        elif key == curses.KEY_DOWN:  # Move down in the menu
            selected = (selected + 1) % num_options
        elif key in [curses.KEY_ENTER, 10, 13]:  # Enter key
            if types[0] == 'remove':
                # Capture the output of the command
                output = execute_function(options[selected])
                return output
            elif types[0] == 'remove_command':
                execute_function(types[1], selected)
                stdscr.refresh()
            elif types[0] == 'add_command':
                execute_function(types[1], types[2])
                stdscr.refresh()
            elif types[0] == 'run_command':
                if selected < len(options) - 3:
                    # Run the command and wait for it to complete
                    run_command(options[selected])
                elif selected == len(options) - 3:  # Add Category option
                    stdscr.addstr("\nEnter the command to add: ")
                    stdscr.refresh()
                    curses.echo()  # Enable echoing of user input
                    new_command = stdscr.getstr().decode(
                        'utf-8').strip()  # Get the new command to add
                    if new_command:
                        add_line(types[1], new_command)
                        stdscr.addstr(f"\\Command added\n: '{new_command}'\n")
                    stdscr.refresh()
                # Remove Category option (second last)
                elif selected == len(options) - 2:
                    stdscr.addstr("\nSelect a command to remove:\n")
                    stdscr.refresh()
                    curses.noecho()  # Disable echoing for the category selection
                    cat = display_menu(
                        stdscr, options[:-3], remove_line, ['remove_command', types[1]])
                    stdscr.addstr(f"\nCategory '{cat}' removed!\n")
                    selected = selected - 1
                    stdscr.refresh()
                elif selected == len(options) - 1:  # Exit option
                    stdscr.addstr("\nExiting...\n")
                    stdscr.refresh()
            return


def run_command(command):
    try:
        curses.endwin()
        print("\n")
        os.system(command)
        print("\n")
        # Pause for user to see output
        os.system("read -p 'Press Enter to exit.'")
        sys.exit()
    except subprocess.CalledProcessError as e:
        print(f"Command '{command}' failed with exit code {e.returncode}")
        print("Error Output:")
        print(e.stderr)
#


def main(stdscr):
    create_category_directory()  # Ensure the category directory exists
    menu_options = ["Add Category", "Remove Category", "Exit"]  # Menu options
    command_option = ["Add Command", "Remove Command", "Back"]
    selected = 0

    while True:
        # Fetch categories to display in the menu
        categories = get_categories()
        options = categories + menu_options  # Update menu options

        display_menu1(stdscr, options, selected)

        key = stdscr.getch()  # Wait for user input

        if key == curses.KEY_UP:
            selected = (selected - 1) % len(options)  # Move up in the menu
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(options)  # Move down in the menu
        elif key == curses.KEY_ENTER or key in [10, 13]:  # Enter key
            if selected < len(options) - 3:
                option = options[selected]
                path = os.path.join(CATEGORY_DIR, f"{option}.txt")
                commands = read_file_to_array(path)
                commands += command_option
                display_menu(
                    stdscr, commands, run_command, [
                        'run_command', path])
                stdscr.refresh()
            elif selected == len(options) - 3:  # Add Category option
                stdscr.addstr("\nEnter the name of the new category: ")
                stdscr.refresh()
                curses.echo()  # Enable echoing of user input
                category_name = stdscr.getstr().decode('utf-8').strip()  # Get the category name
                if category_name:
                    add_category(category_name)  # Add the category
                    stdscr.addstr(f"\nCategory '{category_name}' added!\n")
                stdscr.refresh()
            # Remove Category option (second last)
            elif selected == len(options) - 2:
                stdscr.addstr("\nSelect a category to remove:\n")
                stdscr.refresh()
                curses.noecho()  # Disable echoing for the category selection
                cat = display_menu(
                    stdscr, options[:-3], remove_category, ['remove'])
                stdscr.addstr(f"\nCategory '{cat}' removed!\n")
                selected = selected - 1
                stdscr.refresh()
            elif selected == len(options) - 1:  # Exit option
                stdscr.addstr("\nExiting...\n")
                stdscr.refresh()  # Refresh to show the exit message
                return  # Exit the main function, terminating the program


def start():
    curses.wrapper(main)
