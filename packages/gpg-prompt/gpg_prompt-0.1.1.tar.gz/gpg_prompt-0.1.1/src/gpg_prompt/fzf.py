#!/usr/bin/env python
#This is a cli fzf version of the rofi_gpg script
#copyright (c) 2025 Ubuntpunk

import sys
import json
import subprocess
import webbrowser
import urllib.parse
import os

RED = '\033[91m'
GREEN = '\033[92m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

def colorize(text, color_code):
    """Apply color code to text if output is a tty."""
    if os.isatty(sys.stdout.fileno()):
        return f"{color_code}{text}{RESET}"
    return text

def check_fzf_installed():
    """Check if fzf is available in the system."""
    try:
        subprocess.run(['which', 'fzf'], capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def get_package_manager_instructions():
    """Return installation instructions for various package managers."""
    instructions = f"""
    {colorize("FZF is not installed. Please install it using one of the following methods:", RED + BOLD)}

    {colorize("For Debian/Ubuntu:", BLUE)}
    sudo apt update && sudo apt install fzf

    {colorize("For Arch Linux:", BLUE)}
    sudo pacman -S fzf

    {colorize("For Fedora:", BLUE)}
    sudo dnf install fzf

    {colorize("For macOS:", BLUE)}
    brew install fzf

    {colorize("Alternative methods:", GREEN)}
    1. Using Git:
    git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf
    ~/.fzf/install

    2. Using Python pip:
    pip install fzf

    {colorize("Please install fzf and try again.", RED + BOLD)}
"""
    return instructions

def load_gpg_commands(file_path):
    """Load GPG commands from a JSON file."""
    package_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(package_dir, 'db', 'commands.json')     
    with open(full_path, 'r') as file:
        return json.load(file)

def format_commands_for_fzf(commands):
    """Format commands for fzf."""
    formatted_commands = []
    for command in commands:
        formatted_commands.append(f"{command['command']} | {command['name']} | {urllib.parse.unquote(command['description'])} | {urllib.parse.unquote(command['link'])}")
    return formatted_commands

def execute_fzf(commands):
    """Execute fzf and return the selected command."""
    if not check_fzf_installed():
        print(get_package_manager_instructions())
        sys.exit(1)
    process = subprocess.Popen(['fzf', '--height', '40%', '--layout=reverse', '--border'],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   universal_newlines=True)
        
    output, _ = process.communicate('\n'.join(commands))
    return output.strip() if output else None
 
def open_gpg_command_url(selected_command):
    """Open the URL associated with the selected command."""
    if not selected_command:
        return
    print(f"Processing selected command: {selected_command}")  # Debug print
    parts = selected_command.split(" | ")
    print(f"Split parts: {parts}")  # Debug print
    if len(parts) != 4:
        print("Invalid command format")
        return
    description = parts[3]
    print(f"description: {description}")  # Debug print
    
    # Construct the path to the gpg.md file
    package_dir = os.path.dirname(os.path.abspath(__file__))
    gpg_md_path = os.path.join(package_dir, 'assets', 'gpg.md')
    
    # Construct the URL to open the gpg.md file with the manual_description as a fragment
    url = f"file://{gpg_md_path}#:{description}"
    print(f"Opening URL: {url}")  # Debug print
    #subprocess.run(['vim', f'{gpg_md_path}#:{description}'])
    subprocess.run(['xdg-open', url])

def main():
    gpg_commands = load_gpg_commands('commands.json')
    formatted_commands = format_commands_for_fzf(gpg_commands)
    selected_command_fzf = execute_fzf(formatted_commands)
    if selected_command_fzf:
        open_gpg_command_url(selected_command_fzf)
    else:
        print("No command selected from fzf")

if __name__ == "__main__":
    main()
