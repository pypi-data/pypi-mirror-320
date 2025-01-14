import os
import time
import socket
from colorama import Fore, Style, init
import requests
import sys
import datetime
import base64
import keyboard



init()

def clear_screen() -> None:
    if os.name == 'posix':
        os.system('clear')
    elif os.name == 'nt':
        os.system('cls')
    else:
        raise NotImplementedError("Unsupported Operating System!")

def calculate_elapsed_time(start_time, end_time) -> dict:
    if not (isinstance(start_time, (int, float)) and isinstance(end_time, (int, float))):
        raise TypeError("Only time.time() or get_time() values are accepted!")

    time_difference = end_time - start_time
    seconds = int(time_difference)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    milliseconds = int((time_difference - int(time_difference)) * 1000)

    return {
        "Milliseconds": milliseconds,
        "Seconds": seconds if seconds > 0 else None,
        "Minutes": minutes if minutes > 0 else None,
        "Hours": hours if hours > 0 else None,
        "Days": days if days > 0 else None
    }

def get_time() -> float:
    return time.time()

def rainbow_text(TEXT, LOOP, Speed, section) -> None:
    def speed_control():
        if Speed not in ['Slow', 'Fast', None]:
            raise ValueError("Invalid speed value. Choose 'Slow', 'Fast', or None.")

    def section_control():
        if section not in ['Full', 'Half', 'Quarter', None]:
            raise ValueError("Invalid section value. Choose 'Full', 'Half', 'Quarter', or None.")

    speed_control()
    section_control()

    init(autoreset=True)
    if not isinstance(LOOP, int):
        print("LOOP must be an integer!")
        time.sleep(3)
        clear_screen()
        exit(1)

    colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]

    text_length = len(TEXT)

    if section in ['Full', None]:
        section_count1 = 238
        section_count2 = section_count1 - 2
    elif section == 'Half':
        section_count1 = 119
        section_count2 = section_count1 - 2
    elif section == 'Quarter':
        section_count1 = 59
        section_count2 = section_count1 - 2

    while True:
        if LOOP <= 0:
            break

        for i in range(1, section_count1 - text_length):
            for color in colors:
                if Speed in ['Slow']:
                    time.sleep(0.001)
                elif Speed == 'Fast':
                    pass
                elif Speed is None:
                    time.sleep(0.0001)
                print(" " * i + color + TEXT)

        for i in range(section_count2 - text_length, 0, -1):
            for color in colors:
                if Speed in ['Slow']:
                    time.sleep(0.001)
                elif Speed == 'Fast':
                    pass
                elif Speed is None:
                    time.sleep(0.0001)
                print(" " * i + color + TEXT)

def check_port(ip_address, port) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((ip_address, port))
    sock.close()

    return result == 0

def check_internet() -> bool:
    try:
        response = requests.get("http://www.google.com", timeout=2.5)
        return True
    except requests.ConnectionError:
        return False

def lprint(*text, end="\n", sep=" ", delay=0.10) -> None:
    text = map(str, text)
    combined_word = sep.join(text)
    word_len = len(combined_word)

    for char in combined_word:
        print(char, end="", flush=True)
        time.sleep(delay)

    print(end=end)


def linput(*text, end="", sep=" ", delay=0.10, autocorrect=False) -> str:
    lprint(*text, end=end, sep=sep, delay=delay)
    if autocorrect and os.name == 'nt':
        clear_autocorrect()
    return input()

def formatted_number(Numbers=0) -> str:
    if not isinstance(Numbers, (int, float, str)):
        raise TypeError("Value must be an integer, float, or a numeric string.")

    Numbers = str(float(Numbers)).replace('.', ',')
    integer_part, fractional_part = Numbers.split(',')

    formatted_integer_part = ".".join([
        integer_part[max(i - 3, 0):i]
        for i in range(len(integer_part), 0, -3)
    ][::-1])

    return f"{formatted_integer_part},{fractional_part}"

def reverse_formatted_number(Numbers=0) -> str:
    if not isinstance(Numbers, str):
        raise TypeError("Value must be a string.")
    return Numbers.replace(".", "").replace(",", ".")

def clear_autocorrect() -> None:
    if os.name == 'nt': # Windows
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    else: # Unix
        import termios
        termios.tcflush(sys.stdin, termios.TCIFLUSH)

def color_mixer(colors=None, return_type='ansi') -> str:
    init()
    rgb_colors = {
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "magenta": (255, 0, 255),
        "cyan": (0, 255, 255),
        "yellow": (255, 255, 0),
        "black": (0, 0, 0),
        "white": (255, 255, 255)
    }

    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(rgb_color):
        return '#{:02X}{:02X}{:02X}'.format(*rgb_color)

    def parse_color(color):
        if isinstance(color, tuple) and len(color) == 3:
            return color
        elif isinstance(color, str):
            if color.startswith('0x'):
                return hex_to_rgb(color[2:])
            elif color.startswith('#'):
                return hex_to_rgb(color)
            else:
                return rgb_colors.get(color.lower())
        elif isinstance(color, int):
            return hex_to_rgb(f'{color:06X}')
        return None

    def blend_multiple_colors(color_data):
        total_weight = 0
        blended_color = [0, 0, 0]

        if isinstance(color_data, dict):
            for color, weight in color_data.items():
                rgb = parse_color(color)
                if rgb:
                    for i in range(3):
                        blended_color[i] += rgb[i] * weight
                    total_weight += weight

        elif isinstance(color_data, list):
            num_colors = len(color_data)
            if num_colors == 0:
                return (0, 0, 0)
            for color in color_data:
                rgb = parse_color(color)
                if rgb:
                    for i in range(3):
                        blended_color[i] += rgb[i]
            total_weight = num_colors

        elif isinstance(color_data, tuple):
            return color_data

        if total_weight == 0:
            return (0, 0, 0)

        blended_color = tuple(int(c / total_weight) for c in blended_color)
        return blended_color

    def rgb_to_ansi(rgb_color):
        r, g, b = rgb_color
        return f"\033[38;2;{r};{g};{b}m"

    def combine_colors(color_data):
        blended_rgb = blend_multiple_colors(color_data)
        if return_type == 'ansi':
            return rgb_to_ansi(blended_rgb)
        elif return_type == 'rgb':
            return blended_rgb
        elif return_type == 'hex':
            return rgb_to_hex(blended_rgb)
        else:
            raise ValueError("Invalid return_type. Choose 'ansi', 'rgb', or 'hex'.")

    return combine_colors(colors)




def llinput(*prompt,
            sep=" ",
            end='\n',
            wend='',
            max_length=None,
            min_length=None,
            forceint=False,
            negativeint=False,
            forcestr=False,
            forceinput=False,
            startswith=("", False),
            forcestartswith=[],
            forceendswith=[],
            choices=([], False),
            blockedchars=r"",
            availablechars=r"",
            forceinputlen=0,
            autocorrect=False,
            inputcolor=None,
            promptcolor=None,
            endcolor=None,
            wendcolor=None,
            inputtype="world",
            custom_enter_check_func=None,
            custom_delete_ch_check_func=None,
            custom_press_key_check_func=None,
        ) -> str:





    underline = "\033[4m"
    reset = "\033[0m"

    prompt = sep.join(map(str, prompt))

    if autocorrect:
        clear_autocorrect()

    bool_values = [forcestr, forceint]
    true_count = bool_values.count(True)

    if true_count > 1:
        raise ValueError("forcestr, forceint cannot be used together.")

    type_settings = {
        "type": inputtype.split("-")[0],
        "lastkey": False,
        "clearend": False,
        "showend": False,
        "hidend": False,
        "hidend2": False,
        "underline": False,
        "endunderline": False,
        "endnormalline": False,
    }

    if len(inputtype.split("-")) > 1:
        x = inputtype.split("-")
        for i in type_settings:
            if i == "type":
                continue
            if i in x:
                type_settings[i] = True
            else:
                type_settings[i] = False

    Choices_VALUE = False

    cursor_pos = len(startswith[0])


    if any([promptcolor, inputcolor, wendcolor, endcolor]):
        inputcolor = color_mixer(inputcolor)
        promptcolor = color_mixer(promptcolor)
        endcolor = color_mixer(endcolor)
        wendcolor = color_mixer(wendcolor)


    sys.stdout.write(prompt)
    sys.stdout.flush()

    input_str = startswith[0]

    def update_display(endflag=False):

        if type_settings['type'] == "world":
            display_str = input_str

        elif type_settings['type'] == "password":
            if type_settings['lastkey'] and len(input_str) > 0:
                display_str = '*' * (len(input_str) - 1) + input_str[-1]
            else:
                display_str = '*' * len(input_str)
        elif type_settings['type'] == "password2":
            if type_settings['lastkey'] and len(input_str) > 0:
                display_str = ' ' * (len(input_str) - 1) + input_str[-1]
            else:
                display_str = ' ' * len(input_str)
        else:
            raise ValueError(
                f"\n\nInvalid input type. Allowed types: 'world', 'password', 'password2'\n\n"
                f"Example: llinput('Enter your password: ', inputtype='password-lastkey-clearend')\n\n"
                f"Allowed input type settings: {', '.join([item for item in type_settings if item != 'type'])}"
            )

        if type_settings["underline"]:
            display_str = underline + display_str + reset

        if endflag:


            if type_settings["showend"]:
                display_str = input_str

            elif type_settings["hidend"]:
                display_str = '*' * len(input_str)

            elif type_settings["hidend2"]:
                display_str = ' ' * len(input_str)

            if type_settings["endnormalline"]:
                display_str = input_str + reset

            elif type_settings["endunderline"]:
                display_str = underline + input_str + reset

            if type_settings["clearend"]:
                sys.stdout.write("\r" + " " * (len(prompt) + len(input_str) + len(wend) + 1) + "\r")
                display_str = ''

        if not endflag:
            if any([promptcolor, inputcolor, wendcolor, endcolor]):
                sys.stdout.write('\r' + promptcolor + prompt + Fore.RESET + inputcolor + display_str + Fore.RESET + wendcolor + wend + Fore.RESET + ' ' * (len(end) + 1))
                sys.stdout.write('\r' + promptcolor + prompt + Fore.RESET + inputcolor + display_str + Fore.RESET + wendcolor + wend + Fore.RESET)
                sys.stdout.write('\b' * (len(wend) + (len(input_str) - cursor_pos)))
                sys.stdout.flush()
            else:
                sys.stdout.write('\r' + prompt + display_str + wend + ' ' * (len(end) + 1))
                sys.stdout.write('\r' + prompt + display_str + wend)
                sys.stdout.write('\b' * (len(wend) + (len(input_str) - cursor_pos)))
                sys.stdout.flush()
        else:

            if any([promptcolor, inputcolor, wendcolor, endcolor]):
                sys.stdout.write('\r' + promptcolor + prompt + Fore.RESET + inputcolor + display_str + Fore.RESET + wendcolor + wend + Fore.RESET + endcolor + end + Fore.RESET)
            else:
                sys.stdout.write('\r' + prompt + display_str + wend + end)
            sys.stdout.flush()

    def getch():
        if os.name == "nt": # Windows
            import msvcrt
            first_char = msvcrt.getwch()
            if first_char in ('\x00', '\xe0'):
                second_char = msvcrt.getwch()
                key_combo = first_char + second_char


                if key_combo == '\xe0H':
                    return 'UP'
                elif key_combo == '\xe0P':
                    return 'DOWN'
                elif key_combo == '\xe0K':
                    return 'LEFT'
                elif key_combo == '\xe0M':
                    return 'RIGHT'

                return first_char
            return first_char

        else: # Unix
            import termios
            import tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
                if ch == '\x1b':
                    ch += sys.stdin.read(2)
                    if ch == '\x1b[A':
                        return 'UP'
                    elif ch == '\x1b[B':
                        return 'DOWN'
                    elif ch == '\x1b[D':
                        return 'LEFT'
                    elif ch == '\x1b[C':
                        return 'RIGHT'
                return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    update_display()

    while True:
        ch = getch()

        if availablechars:
            if ch not in availablechars and ch not in {'\r', '\n', "\b", "\x7f"}:
                continue

        if ch in blockedchars:
            continue

        if forcestartswith:
            if ch not in {'\r', '\n', "\b", "\x7f"}:
                if not any(input_str.startswith(fs) or (len(input_str) < len(fs) and ch == fs[len(input_str)]) for fs in forcestartswith):
                    continue


        if ch in {'\r', '\n'}:  # Enter key
            if choices[0]:
                if not choices[1]:
                    if input_str not in choices[0]:
                        continue
                else:
                    match = next((c for c in choices[0] if input_str.lower() == c.lower()), None)
                    if match:
                        Choices_VALUE = match
                    else:
                        continue

            if forceendswith and not any(input_str.endswith(f) for f in forceendswith):
                continue

            if forceinput and input_str == "":
                continue

            if forceinputlen > 0 and len(input_str) != forceinputlen:
                continue

            if min_length is not None and len(input_str) < min_length:
                continue

            if custom_enter_check_func:
                if callable(custom_enter_check_func):
                    if not custom_enter_check_func(input_str):
                        continue

            update_display(endflag=True)

            break

        elif ch in {'\b', '\x7f'}:  # Backspace key
            if cursor_pos > 0:
                if custom_delete_ch_check_func and callable(custom_delete_ch_check_func):
                    if not custom_delete_ch_check_func(input_str, (input_str[cursor_pos-1], cursor_pos-1)):
                        continue

                if startswith[1] and cursor_pos == len(startswith[0]):
                    pass
                else:
                    input_str = input_str[:cursor_pos-1] + input_str[cursor_pos:]
                    cursor_pos -= 1

        elif ch in {'UP', 'RIGHT', 'DOWN', 'LEFT'}:  # Escape sequences (arrow keys)
            if ch == 'RIGHT' and cursor_pos < len(input_str):
                cursor_pos += 1
                sys.stdout.write("\033[C")
                sys.stdout.flush()
            elif ch == 'LEFT' and cursor_pos > 0:
                cursor_pos -= 1
                sys.stdout.write("\033[D")
                sys.stdout.flush()
            continue

        else:
            if custom_press_key_check_func:
                if callable(custom_press_key_check_func):
                    if not custom_press_key_check_func(input_str, (ch, cursor_pos)):
                        continue

            if max_length is None or len(input_str) < max_length:
                if forceint:
                    if ch.isdigit():
                        input_str = input_str[:cursor_pos] + ch + input_str[cursor_pos:]
                        cursor_pos += 1
                elif negativeint and not forcestr:
                    if (ch == "-" and len(input_str) == 0) or (ch.isdigit() and input_str.startswith("-")):
                        input_str = input_str[:cursor_pos] + ch + input_str[cursor_pos:]
                        cursor_pos += 1
                elif forcestr:
                    if not ch.isdigit():
                        input_str = input_str[:cursor_pos] + ch + input_str[cursor_pos:]
                        cursor_pos += 1
                else:
                    input_str = input_str[:cursor_pos] + ch + input_str[cursor_pos:]
                    cursor_pos += 1

        update_display()

    return Choices_VALUE if Choices_VALUE else input_str




def get_directory_tree(startpath, depth=0, max_depth=float('inf'), prefix='', is_last=True, style='normal', custom_style=None, ingore_errors=False) -> str:
    if depth > max_depth:
        return ''

    tree_str = ''
    if depth == 0:
        tree_str += os.path.basename(startpath) + '\\\n'

    default_styles = {
        'normal': {'branch': ('├── ', '└── ', '|', '\\'), 'spacing': '    '},
        'bold': {'branch': ('┣━━ ', '┗━━ ', '┃', '\\'), 'spacing': '    '},
        'thin': {'branch': ('├─ ', '└─ ', '|', '\\'), 'spacing': '│  '},
        'compact': {'branch': ('', '', '|', '\\'), 'spacing': ''},
        'double': {'branch': ('╠══ ', '╚══ ', '║', '\\'), 'spacing': '    '},
        'dash': {'branch': ('|-- ', '`-- ', '|', '\\'), 'spacing': '    '},
        'star': {'branch': ('*-- ', '*-- ', '*', '\\'), 'spacing': '    '},
        'plus': {'branch': ('+-+ ', '+-+ ', '+', '\\'), 'spacing': '    '},
        'wave': {'branch': ('~-- ', '~-- ', '~', '\\'), 'spacing': '    '},
        'hash': {'branch': ('#-- ', '#-- ', '#', '\\'), 'spacing': '    '},
        'dot': {'branch': ('.-- ', '`-- ', '.', '\\'), 'spacing': '    '},
        'pipe': {'branch': ('|-- ', '|-- ', '|', '\\'), 'spacing': '    '},
        'slash': {'branch': ('/-- ', '/-- ', '/', '\\'), 'spacing': '    '},
        'backslash': {'branch': ('\\-- ', '\\-- ', '\\', '\\'), 'spacing': '    '},
        'equal': {'branch': ('=-- ', '=-- ', '=', '\\'), 'spacing': '    '},
        'colon': {'branch': (':-- ', ':-- ', ':', '\\'), 'spacing': '    '},
        'semicolon': {'branch': (';-- ', ';-- ', ';', '\\'), 'spacing': '    '},
        'exclamation': {'branch': ('!-- ', '!-- ', '!', '\\'), 'spacing': '    '},
        'question': {'branch': ('?-- ', '?-- ', '?', '\\'), 'spacing': '    '},
        'caret': {'branch': ('^-- ', '^-- ', '^', '\\'), 'spacing': '    '},
        'percent': {'branch': ('%-- ', '%-- ', '%', '\\'), 'spacing': '    '},
        'at': {'branch': ('@-- ', '@-- ', '@', '\\'), 'spacing': '    '},
        'tilde': {'branch': ('~-- ', '~-- ', '~', '\\'), 'spacing': '    '},
        'bracket': {'branch': ('[-- ', '[-- ', '[', '\\'), 'spacing': '    '},
        'brace': {'branch': ('{-- ', '{-- ', '{', '\\'), 'spacing': '    '},
        'paren': {'branch': ('(-- ', '(-- ', '(', '\\'), 'spacing': '    '},
        'angle': {'branch': ('<-- ', '<-- ', '<', '\\'), 'spacing': '    '},
        'quote': {'branch': ('"-- ', '"-- ', '"', '\\'), 'spacing': '    '},
        'apos': {'branch': ("'-- ", "'-- ", "'", '\\'), 'spacing': '    '},
        'underscore': {'branch': ('_-- ', '_-- ', '_', '\\'), 'spacing': '    '},
        'plusminus': {'branch': ('±-- ', '±-- ', '±', '\\'), 'spacing': '    '},
        'doubleangle': {'branch': ('«-- ', '«-- ', '«', '\\'), 'spacing': '    '},
        'box': {'branch': ('┏━ ', '┗━ ', '┃', '\\'), 'spacing': '    '},
        'arrow': {'branch': ('→-- ', '→-- ', '→', '\\'), 'spacing': '    '},
    }

    selected_style = custom_style if custom_style else default_styles.get(style, default_styles['normal'])

    spacing = selected_style['spacing']
    branch = selected_style['branch']

    if depth > 0:
        tree_str += prefix + (branch[1] if is_last else branch[0]) + os.path.basename(startpath) + branch[3] + '\n'

    prefix += spacing if is_last else branch[2] + spacing
    if ingore_errors:
        try:
            items = os.listdir(startpath)
            for i, item in enumerate(items):
                path = os.path.join(startpath, item)
                if os.path.isdir(path):
                    tree_str += get_directory_tree(path, depth + 1, max_depth, prefix, i == len(items) - 1, style, custom_style)
                else:
                    if style == 'box':
                        if i == len(items) - 1:
                            tree_str += prefix + branch[1] + item + '\n'
                        else:
                            tree_str += prefix + '┃━ ' + item + '\n'
                    else:
                        tree_str += prefix + (branch[1] if i == len(items) - 1 else branch[0]) + item + '\n'
        except:
            pass
    else:
        items = os.listdir(startpath)
        for i, item in enumerate(items):
            path = os.path.join(startpath, item)
            if os.path.isdir(path):
                tree_str += get_directory_tree(path, depth + 1, max_depth, prefix, i == len(items) - 1, style, custom_style)
            else:
                if style == 'box':
                    if i == len(items) - 1:
                        tree_str += prefix + branch[1] + item + '\n'
                    else:
                        tree_str += prefix + '┃━ ' + item + '\n'
                else:
                    tree_str += prefix + (branch[1] if i == len(items) - 1 else branch[0]) + item + '\n'


    return tree_str




class _Tools:
    def __init__(self):
        pass

    @staticmethod
    def control_file(file_name):
        return os.path.exists(file_name)



    @staticmethod
    def upload_image(image_path):
        try:
            url = "https://catbox.moe/user/api.php"
            payload = {
                'reqtype': 'fileupload'
            }
            files = {
                'fileToUpload': open(image_path, 'rb')
            }
            response = requests.post(url, data=payload, files=files)

            if response.status_code == 200:
                return response.text.strip()
            else:
                return None
        except:
            return None


    @staticmethod
    def url_check(url):
        try:
            response = requests.head(url, allow_redirects=True)
            if response.status_code == 200:
                return True
            else:
                return False
        except requests.exceptions.RequestException as e:
            return False

    @staticmethod
    def image_to_base64(image_path):
        with open(image_path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string


class TokenIsNotWork(Exception):
    pass

class Discord:

    class Embed:
        def __init__(self, title=None, description=None, color=0x3498db):
            self.embed = {
                "title": title,
                "description": description,
                "color": color,
                "fields": [],
                "author": {},
                "footer": {},
                "thumbnail": {},
                "image": {},
                "timestamp": None
            }

        def set_author(self, name, icon_url_or_path=None, url=None):
            icon_url = None
            if icon_url_or_path:
                if icon_url_or_path.startswith("http"):
                    if _Tools.url_check(icon_url_or_path):
                        icon_url = icon_url_or_path
                    else:
                        raise ValueError("URL is not valid.")
                else:
                    if _Tools.control_file(icon_url_or_path):
                        icon_url = _Tools.upload_image(icon_url_or_path)
                        if icon_url is None:
                            raise Exception("An issue occurred during the upload. Please try again using a URL instead of the file path.", icon_url_or_path)
                    else:
                        raise FileNotFoundError(f"File not found: {icon_url_or_path}")

            self.embed["author"] = {"name": name, "icon_url": icon_url, "url": url}

        def add_field(self, name, value, inline=True):
            self.embed["fields"].append({"name": name, "value": value, "inline": inline})

        def set_footer(self, text, icon_url_or_path=None):
            icon_url = None
            if icon_url_or_path:
                if icon_url_or_path.startswith("http"):
                    if _Tools.url_check(icon_url_or_path):
                        icon_url = icon_url_or_path
                    else:
                        raise ValueError("URL is not valid.")
                else:
                    if _Tools.control_file(icon_url_or_path):
                        icon_url = _Tools.upload_image(icon_url_or_path)
                        if icon_url is None:
                            raise Exception("An issue occurred during the upload. Please try again using a URL instead of the file path.", icon_url_or_path)
                    else:
                        raise FileNotFoundError(f"File not found: {icon_url_or_path}")

            self.embed["footer"] = {"text": text, "icon_url": icon_url}

        def set_thumbnail(self, url_or_path):
            url = None
            if url_or_path:
                if url_or_path.startswith("http"):
                    if _Tools.url_check(url_or_path):
                        url = url_or_path
                    else:
                        raise ValueError("URL is not valid.")
                else:
                    if _Tools.control_file(url_or_path):
                        url = _Tools.upload_image(url_or_path)
                        if url is None:
                            raise Exception("An issue occurred during the upload. Please try again using a URL instead of the file path.", url_or_path)
                    else:
                        raise FileNotFoundError(f"File not found: {url_or_path}")

            self.embed["thumbnail"] = {"url": url}

        def set_image(self, url_or_path):
            url = None
            if url_or_path:
                if url_or_path.startswith("http"):
                    if _Tools.url_check(url_or_path):
                        url = url_or_path
                    else:
                        raise ValueError("URL is not valid.")
                else:
                    if _Tools.control_file(url_or_path):
                        url = _Tools.upload_image(url_or_path)
                        if url is None:
                            raise Exception("An issue occurred during the upload. Please try again using a URL instead of the file path.", url_or_path)

                    else:
                        raise FileNotFoundError(f"File not found: {url_or_path}")
            else:
                raise ValueError("URL or path must be specified.")

            self.embed["image"] = {"url": url}

        def set_timestamp(self, timestamp=None):
            self.embed["timestamp"] = timestamp if timestamp else datetime.datetime.utcnow().isoformat()

        def to_dict(self):
            return self.embed

    class Author:
        def __init__(self, token):
            self.token = str(token)
            response = requests.get('https://discord.com/api/v9/users/@me', headers={'Authorization': self.token})
            if response.status_code != 200:
                raise TokenIsNotWork('Token : \'{}\' is not working!'.format(self.token))

        def send_message(self, Channel_id, Message, files=None):
            not_files = []

            if files:
                for file in files:
                    if not _Tools.control_file(file):
                        not_files.append(file)

            if not_files:
                raise FileNotFoundError(f"Files not found: {', '.join(not_files)}")

            payload = {'content': str(Message)}
            headers = {'Authorization': self.token}


            if files is not None and isinstance(files, list):
                files_data = {}
                for file_name in files:
                    if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
                        with open(file_name, "rb") as file:
                            files_data[os.path.basename(file_name)] = file.read()


                if files_data:
                    response = requests.post(f'https://discord.com/api/v9/channels/{Channel_id}/messages', data=payload, files=files_data, headers=headers)
                else:
                    response = requests.post(f'https://discord.com/api/v9/channels/{Channel_id}/messages', data=payload, headers=headers)
            else:
                response = requests.post(f'https://discord.com/api/v9/channels/{Channel_id}/messages', data=payload, headers=headers)

            return response.status_code

        def send_reply_message(self, channel_id, message, reply_message_id, files=None):
            not_files = []

            if files:
                not_files = [file for file in files if not _Tools.control_file(file)]

            if not_files:
                raise FileNotFoundError(f"Files not found: {', '.join(not_files)}")

            payload = {
                'content': str(message),
                'message_reference': {'message_id': reply_message_id}
            }
            headers = {'Authorization': self.token}

            if files and isinstance(files, list):
                files_data = {}
                for file_name in files:
                    if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
                        with open(file_name, "rb") as file:
                            files_data[os.path.basename(file_name)] = file.read()

                if files_data:
                    response = requests.post(
                        f'https://discord.com/api/v9/channels/{channel_id}/messages',
                        data=payload,
                        files=files_data,
                        headers=headers
                    )
                else:
                    response = requests.post(
                        f'https://discord.com/api/v9/channels/{channel_id}/messages',
                        data=payload,
                        headers=headers
                    )
            else:
                response = requests.post(
                    f'https://discord.com/api/v9/channels/{channel_id}/messages',
                    data=payload,
                    headers=headers
                )

            return response.status_code

        def delete_message(self, Channel_id, Message_id):
            headers = {'Authorization': self.token}
            response = requests.delete(f'https://discord.com/api/v9/channels/{Channel_id}/messages/{Message_id}', headers=headers)
            return response.status_code

        def edit_message(self, Channel_id, Message_id, Message_Content):
            headers = {'Authorization': self.token}
            payload = {'content': str(Message_Content)}
            response = requests.patch(f'https://discord.com/api/v9/channels/{Channel_id}/messages/{Message_id}', json=payload, headers=headers)
            return response.status_code

        def get_channel_messages(self, channel_id, limit=50):
            headers = {'Authorization': self.token}
            all_messages = []
            last_message_id = None

            while len(all_messages) < limit:
                params = {'limit': min(50, limit - len(all_messages))}
                if last_message_id:
                    params['before'] = last_message_id

                response = requests.get(f'https://discord.com/api/v9/channels/{channel_id}/messages', headers=headers, params=params)
                if response.status_code != 200:
                    try:
                        return response.status_code, response.json()
                    except:
                        return response.status_code, response.text

                messages = response.json()
                if not messages:
                    break

                all_messages.extend(messages)
                last_message_id = messages[-1]['id']

                if len(messages) < 50:
                    break

            return 200, all_messages


        def get_channel_message(self, Channel_id, Message_id):
            headers = {'Authorization': self.token}
            response = requests.get(f'https://discord.com/api/v9/channels/{Channel_id}/messages/{Message_id}', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def add_reaction(self, Channel_id, Message_id, emoji):
            headers = {'Authorization': self.token}
            emoji = requests.utils.quote(emoji)
            response = requests.put(f'https://discord.com/api/v9/channels/{Channel_id}/messages/{Message_id}/reactions/{emoji}/@me', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def remove_reaction(self, Channel_id, Message_id, emoji):
            headers = {'Authorization': self.token}
            emoji = requests.utils.quote(emoji)
            response = requests.delete(f'https://discord.com/api/v9/channels/{Channel_id}/messages/{Message_id}/reactions/{emoji}/@me', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def get_channel_info(self, Channel_id):
            headers = {'Authorization': self.token}
            response = requests.get(f'https://discord.com/api/v9/channels/{Channel_id}', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def get_guild_channels(self, Guild_id):
            headers = {'Authorization': self.token}
            response = requests.get(f'https://discord.com/api/v9/guilds/{Guild_id}/channels', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def change_user_nickname(self, Guild_id, Nickname):
            headers = {'Authorization': self.token}
            payload = {'nick': str(Nickname)}
            response = requests.patch(f'https://discord.com/api/v9/guilds/{Guild_id}/members/@me/nick', json=payload, headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def get_author_info(self):
            headers = {'Authorization': self.token}
            response = requests.get('https://discord.com/api/v9/users/@me', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def get_author_relationships(self):
            headers = {'Authorization': self.token}
            response = requests.get('https://discord.com/api/v9/users/@me/relationships', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def send_friend_request(self, User_id):
            headers = {'Authorization': self.token}
            response = requests.put(f'https://discord.com/api/v9/users/@me/relationships/{User_id}', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def remove_friend(self, User_id):
            headers = {'Authorization': self.token}
            response = requests.delete(f'https://discord.com/api/v9/users/@me/relationships/{User_id}', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def block_user(self, User_id):
            headers = {'Authorization': self.token}
            response = requests.put(f'https://discord.com/api/v9/users/@me/relationships/{User_id}/block', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def unblock_user(self, User_id):
            headers = {'Authorization': self.token}
            response = requests.delete(f'https://discord.com/api/v9/users/@me/relationships/{User_id}/block', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def get_author_channels(self):
            headers = {'Authorization': self.token}
            response = requests.get('https://discord.com/api/v9/users/@me/channels', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def get_author_guilds(self):
            headers = {'Authorization': self.token}
            response = requests.get('https://discord.com/api/v9/users/@me/guilds', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def get_author_settings(self):
            headers = {'Authorization': self.token}
            response = requests.get('https://discord.com/api/v9/users/@me/settings', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def get_author_connections(self):
            headers = {'Authorization': self.token}
            response = requests.get('https://discord.com/api/v9/users/@me/connections', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def get_user_info(self, User_id):
            headers = {'Authorization': self.token}
            response = requests.get(f'https://discord.com/api/v9/users/{User_id}', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def get_all_guilds(self):
            headers = {'Authorization': self.token}
            response = requests.get('https://discord.com/api/v9/users/@me/guilds', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def get_guild(self, Guild_id):
            headers = {'Authorization': self.token}
            response = requests.get(f'https://discord.com/api/v9/guilds/{Guild_id}', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def kick_member(self, Guild_id, Member_id):
            headers = {'Authorization': self.token}
            response = requests.delete(f'https://discord.com/api/v9/guilds/{Guild_id}/members/{Member_id}', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def ban_member(self, Guild_id, Member_id, delete_message_days=0):
            headers = {'Authorization': self.token}
            data = {'delete_message_days': delete_message_days}
            response = requests.put(f'https://discord.com/api/v9/guilds/{Guild_id}/bans/{Member_id}', headers=headers, json=data)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def unban_member(self, Guild_id, Member_id):
            headers = {'Authorization': self.token}
            response = requests.delete(f'https://discord.com/api/v9/guilds/{Guild_id}/bans/{Member_id}', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def get_guild_bans(self, Guild_id):
            headers = {'Authorization': self.token}
            response = requests.get(f'https://discord.com/api/v9/guilds/{Guild_id}/bans', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def get_guild_channels(self, Guild_id):
            headers = {'Authorization': self.token}
            response = requests.get(f'https://discord.com/api/v9/guilds/{Guild_id}/channels', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def get_guild_members(self, Guild_id):
            headers = {'Authorization': self.token}
            response = requests.get(f'https://discord.com/api/v9/guilds/{Guild_id}/members', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def get_guild_roles(self, Guild_id):
            headers = {'Authorization': self.token}
            response = requests.get(f'https://discord.com/api/v9/guilds/{Guild_id}/roles', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def get_user_connections(self, id):
            headers = {'Authorization': self.token}
            response = requests.get(f'https://discord.com/api/v9/users/{id}/connections', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def join_channel(self, Channel_id):
            headers = {'Authorization': self.token}
            response = requests.put(f'https://discord.com/api/v9/channels/{Channel_id}/call/join', headers=headers)
            return response.status_code

        def leave_channel(self, Channel_id):
            headers = {'Authorization': self.token}
            response = requests.delete(f'https://discord.com/api/v9/channels/{Channel_id}/call', headers=headers)
            return response.status_code

        def delete_guild(self, Guild_id):
            headers = {'Authorization': self.token}
            response = requests.delete(f'https://discord.com/api/v9/guilds/{Guild_id}', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def leave_guild(self, Guild_id):
            headers = {'Authorization': self.token}
            response = requests.delete(f'https://discord.com/api/v9/users/@me/guilds/{Guild_id}', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def get_webhooks(self, Channel_id):
            headers = {'Authorization': self.token}
            response = requests.get(f'https://discord.com/api/v9/channels/{Channel_id}/webhooks', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def create_webhook(self, Channel_id, Name, Avatar_path=None):
            headers = {'Authorization': self.token}
            data = {'name': Name}
            Avatar = None

            if _Tools.control_file(Avatar_path):
                encoded_avatar = _Tools.image_to_base64(Avatar_path)
                if encoded_avatar:
                    Avatar = encoded_avatar
                else:
                    raise Exception("An issue occurred during the upload. Please try again using a URL instead of the file path.", Avatar_path)
            else:
                raise FileNotFoundError(f"File not found: {Avatar_path}")

            if Avatar is not None:
                data['avatar'] = Avatar

            response = requests.post(f'https://discord.com/api/v9/channels/{Channel_id}/webhooks', headers=headers, json=data)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def delete_webhook(self, webhook_id):
            headers = {'Authorization': self.token}
            response = requests.delete(f'https://discord.com/api/v9/webhooks/{webhook_id}', headers=headers)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text



    class Webhook:
        def __init__(self, webhook_url):
            self.WebhookUrl = str(webhook_url)

        def send_webhook(self, Content='', embeds=[], files=None):
            not_files = []

            if files:
                for file in files:
                    if not _Tools.control_file(file):
                        not_files.append(file)

            if not_files:
                raise FileNotFoundError(f"Files not found: {', '.join(not_files)}")


            data = {'content': Content}
            data['embeds'] = []
            if isinstance(embeds, list) or isinstance(embeds, tuple):
                for embed in embeds:
                    if embed:
                        if hasattr(embed, 'embed'):
                            data['embeds'].append(embed.embed)
                        else:
                            data['embeds'].append(embed)
            else:
                if embeds:
                    if hasattr(embeds, 'embed'):
                        data['embeds'].append(embeds.embed)
                    else:
                        data['embeds'].append(embeds)

            if files and isinstance(files, list):
                files_data = {os.path.basename(file_name): open(file_name, "rb").read() for file_name in files if os.path.getsize(file_name) > 0}
                response = requests.post(self.WebhookUrl, data=data, files=files_data)
            else:
                response = requests.post(self.WebhookUrl, json=data)

            return response.status_code


        def delete_message(self, Message_id):
            response = requests.delete(f'{self.WebhookUrl}/messages/{Message_id}')
            return response.status_code

        def get_message(self, Message_id):
            response = requests.get(f'{self.WebhookUrl}/messages/{Message_id}')
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def get_webhook_info(self):
            response = requests.get(self.WebhookUrl)
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def get_messages(self):
            response = requests.get(f'{self.WebhookUrl}/messages')
            try:
                return response.status_code, response.json()
            except:
                return response.status_code, response.text

        def edit_message(self, Message_id, Content='', embeds=[]):
            data = {'content': Content}
            data['embeds'] = []

            if isinstance(embeds, list) or isinstance(embeds, tuple):
                for embed in embeds:
                    if embed:
                        if hasattr(embed, 'embed'):
                            data['embeds'].append(embed.embed)
                        else:
                            data['embeds'].append(embed)
            else:
                if embeds:
                    if hasattr(embeds, 'embed'):
                        data['embeds'].append(embeds.embed)
                    else:
                        data['embeds'].append(embeds)

            response = requests.patch(f'{self.WebhookUrl}/messages/{Message_id}', json=data)
            return response.status_code


class Hotkey:
    def __init__(self, *key, target=None, args=()):
        self.key_combination = '+'.join(key)
        self.target = target
        self.args = args
        self.hotkey_id = None

    def start(self):
        def call():
            if self.target:
                self.target(*self.args)

        self.hotkey_id = keyboard.add_hotkey(self.key_combination, call)

    def stop(self):
        if self.hotkey_id is not None:
            keyboard.remove_hotkey(self.hotkey_id)
            self.hotkey_id = None