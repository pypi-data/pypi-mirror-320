import os
import argparse
from typing import TextIO, Optional
import configparser
import re

def read_config_file(config, file_paths):
    for file_path in file_paths:
        try:
            config.read(os.path.expanduser(file_path))
            return config.get('settings', 'exclude').replace(" ", "").split(",")
        except FileNotFoundError:
            continue
        except configparser.NoSectionError:
            continue
    return []

config = configparser.ConfigParser()
config_file_paths = ['~/Scripts/gendia_config.ini', '~/gendia_config.ini']
exclude = read_config_file(config, config_file_paths)

maxdepth: int = None
currdepth: int = 0
matchpattern: str = ""
notmatchpattern: str = ""

# print(exclude)

# ANSI escape codes for coloring
COLOR_BLUE = '\033[94m'  # Blue for directories
COLOR_GREEN = '\033[92m'  # Green for Python files
COLOR_YELLOW = '\033[93m'  # Yellow for compiled Python files
COLOR_RESET = '\033[0m'  # Reset to default color
COLOR_ORANGE = '\033[33m'  # Orange for JavaScript files
COLOR_RED = '\033[31m'  # Red for C files
COLOR_LIGHT_BLUE = '\033[36m'  # Light blue for C++ files
COLOR_PURPLE = '\033[35m'  # Purple for Java files
COLOR_PINK = '\033[95m'  # Pink for Ruby files
COLOR_WHITE = '\033[97m'  # White for text files
COLOR_GRAY = '\033[90m'  # Gray for other files
COLOR_MAGENTA = '\033[95m'  # Magenta for image files
COLOR_CYAN = '\033[96m'  # Cyan for audio files
COLOR_LIGHT_GREEN = '\033[92m'  # Light green for video files
COLOR_LIGHT_YELLOW = '\033[93m'  # Light yellow for compressed files
COLOR_LIGHT_RED = '\033[91m'  # Light red for executable files
COLOR_LIGHT_PURPLE = '\033[95m'  # Light purple for library directories
UNDERLINE = '\033[4m'  # Underline for symbolic links

def get_color(entry: str) -> str:
    """Returns color based on file type."""
    if os.path.isdir(entry):
        return COLOR_BLUE
    elif entry.endswith('.md'):
        return COLOR_GRAY
    elif entry.endswith('.py'):
        return COLOR_GREEN
    elif entry.endswith('.pyc'):
        return COLOR_YELLOW
    elif entry.endswith('.js'):
        return COLOR_ORANGE
    elif entry.endswith('.c'):
        return COLOR_RED
    elif entry.endswith('.cpp'):
        return COLOR_LIGHT_BLUE
    elif entry.endswith('.java'):
        return COLOR_PURPLE
    elif entry.endswith('.rb'):
        return COLOR_PINK
    elif entry.endswith('.txt'):
        return COLOR_WHITE
    elif entry.endswith('.jpg') or entry.endswith('.png') or entry.endswith('.gif'):
        return COLOR_MAGENTA
    elif entry.endswith('.mp3') or entry.endswith('.wav'):
        return COLOR_CYAN
    elif entry.endswith('.mp4') or entry.endswith('.avi') or entry.endswith('.mkv'):
        return COLOR_LIGHT_GREEN
    elif entry.endswith('.zip') or entry.endswith('.tar') or entry.endswith('.gz'):
        return COLOR_LIGHT_YELLOW
    elif entry.endswith('.exe'):
        return COLOR_LIGHT_RED
    elif os.path.islink(entry):
        return UNDERLINE
    else:
        return COLOR_RESET

def print_tree(directory: str, prefix: str = '', output: Optional[TextIO] = None, hidden: bool = False, directories_only: bool = False) -> None:
    global currdepth
    global maxdepth
    global exclude
    global matchpattern
    
    if currdepth == maxdepth:
        return
    
    currdepth += 1
    
    try:
        # List all entries in the directory
        entries = os.listdir(directory)
        
        # Filter entries based on pattern
        if matchpattern:
            entries = [entry for entry in entries if re.search(matchpattern, entry)]
            
        # Filter entries based on not pattern
        if notmatchpattern:
            entries = [entry for entry in entries if not re.search(notmatchpattern, entry)]
        
        # Filter entries based on directories_only
        if directories_only:
            entries = [entry for entry in entries if os.path.isdir(os.path.join(directory, entry))]
        
        # Filter entries based on hidden
        if not hidden:
            entries = [entry for entry in entries if not entry.startswith('.')]
        
        # Filter entries based on exclude
        if exclude:
            entries = [entry for entry in entries if entry not in exclude]
        
        # Sort the entries
        entries = sorted(entries, key=lambda s: (not os.path.isdir(os.path.join(directory, s)), s.lower()))
        
    except PermissionError:
        print(f"\033[31mPermission denied to access {directory}\033[0m")
        return

    for index, entry in enumerate(entries):
        path = os.path.join(directory, entry)
        is_last = index == len(entries) - 1
        color = get_color(path) if output is None else ''
        reset = COLOR_RESET if output is None else ''

        # Print the current item with the appropriate prefix
        line = f"{prefix}└── {color}{entry}{reset}" if is_last else f"{prefix}├── {color}{entry}{reset}"
        if output:
            output.write(line + '\n')
        else:
            print(line)

        # Recursively print the contents of directories
        if os.path.isdir(path):
            new_prefix = f"{prefix}    " if is_last else f"{prefix}│   "
            print_tree(path, new_prefix, output, hidden, directories_only)

    currdepth -= 1

def main() -> None:
    global exclude
    global maxdepth
    global matchpattern
    global notmatchpattern
    
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Display a color-coded tree-like directory structure")
    parser.add_argument('directory', type=str, nargs='?', default='.', help='The directory to display (default: current directory)')
    parser.add_argument('-o', '--output', type=str, help='The output file to write the diagram to')
    parser.add_argument("--hidden", action="store_true", help="Exclude hidden files and directories")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.5.4")
    parser.add_argument("--exclude", type=str, help="Exclude files and directories that match the given pattern")
    parser.add_argument("--depth", type=int, help="Limit the depth of the tree diagram")
    parser.add_argument("-d", action="store_true", help="Show directories only")
    parser.add_argument("-P", type=str, help="Show only files matching the pattern")
    parser.add_argument("-l", type=str, help="Do not show files matching the pattern")
    parser.add_argument("--ignore-config", action="store_true", help="Ignore the configuration file")
    args = parser.parse_args()
    
    try:
        exclude.extend(args.exclude.replace(" ", "").split(","))
    except AttributeError:
        exclude.extend([])
        
    maxdepth = args.depth
    matchpattern = args.P
    notmatchpattern = args.l
    
    if args.ignore_config:
        exclude = []

    # Get the absolute path of the directory
    directory = os.path.abspath(args.directory)
    if os.path.isdir(directory):
        try:
            if args.output:
                try:
                    with open(args.output, 'w+') as output_file:
                        output_file.write(directory + '\n')
                        print_tree(directory, output=output_file, hidden=args.hidden, directories_only=args.d)
                    print(f"\033[32mDirectory structure written to {args.output}\033[0m")
                except IsADirectoryError:
                    print(f"\033[31m{args.output} is a directory, please provide a valid file name\033[0m")
                except PermissionError:
                    print(f"\033[31mPermission denied to write to {args.output}\033[0m")
            else:
                print(f"\033[1m{directory}\033[0m")
                print_tree(directory=directory, hidden=args.hidden, directories_only=args.d)
        except KeyboardInterrupt:
            print("\033[31m\nProgram terminated\033[0m")
    else:
        print(f"\033[31m{directory} is not a valid directory\033[0m")

if __name__ == '__main__':
    main()