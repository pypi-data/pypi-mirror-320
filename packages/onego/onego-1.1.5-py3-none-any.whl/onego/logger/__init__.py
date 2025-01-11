import os
from datetime import datetime

os.system("") #

def remove_colors_from_str(text: str):
    all_colors = [
        "\033[0m" , "\033[1m", "\033[3m", "\033[4m" , "\033[30m\033[47m", "\033[31m", "\033[32m", "\033[33m", "\033[34m",
        "\033[35m", "\033[36m", "\033[37m", "\033[90m", "\033[91m", "\033[92m", "\033[93m", "\033[94m", "\033[95m", "\033[96m",
        "\033[97m", "\033[40m", "\033[41m", "\033[42m", "\033[43m", "\033[44m", "\033[45m", "\033[46m", "\033[47m"
    ]
    for c in all_colors: text = text.replace(c, '')
    return text

class colors:

    RESET = "\033[0m"

    BOLD = "\033[1m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    BLACK = "\033[30m\033[47m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    PURPLE = "\033[35m"
    AQUA = "\033[36m"
    WHITE = "\033[37m"
    #GRAY = "\033[90m"

    LIGHT_RED = "\033[91m"
    LIGHT_GREEN = "\033[92m"
    LIGHT_YELLOW = "\033[93m"
    LIGHT_BLUE = "\033[94m"
    LIGHT_PURPLE = "\033[95m"
    LIGHT_AQUA = "\033[96m"
    LIGHT_WHITE = "\033[97m"

    BLACK_BG = "\033[40m"
    RED_BG = "\033[41m"
    GREEN_BG = "\033[42m"
    YELLOW_BG = "\033[43m"
    BLUE_BG = "\033[44m"
    PURPLE_BG = "\033[45m"
    CYAN_BG = "\033[46m"
    WHITE_BG = "\033[47m"

def _values_to_string(*values: object, sep: str = ' '): return sep.join([str(v) for v in values])

class Logger:

    def __init__(self, prefix: str = '', logs_path: str = '.logs') -> None:
        self.prefix = f'({prefix})' if prefix else ''
        self.logs_path = logs_path
        self.colors = colors()

    def save_today_log(self, text: str):
        now_date = datetime.now().strftime("%d-%m-%Y")
        path = os.path.join(self.logs_path, now_date)
        os.makedirs(path, exist_ok=True)
        path = os.path.join(path, 'logs.log')
        with open(path, 'a', encoding='utf-8') as file: file.write(text)

    def log(self, text: str, color: str = colors.RESET, save: bool = False):
        log_time = datetime.now().strftime("%H:%M:%S")
        if save: self.save_today_log(log_time + ' > ' + remove_colors_from_str(text) + '\n')
        print(f'{color}{text}{colors.RESET}')

    def __error(self, text: str):
        log_time = datetime.now().strftime("%H:%M:%S")
        self.save_today_log('(error) -> ' + log_time + ' > ' + text + '\n')
        print(f'{colors.RED}(error) -> {colors.LIGHT_RED}' + text + f'{colors.RESET}')

    def error(self, *values: object, sep: str = ' ', save: bool = False): self.log(f'(ERROR) {self.prefix} {_values_to_string(*values, sep)}', colors.LIGHT_RED, save)

    def info(self, *values: object, sep: str = ' ', save: bool = False): self.log(f'(INFO) {self.prefix} {_values_to_string(*values, sep)}', colors.LIGHT_AQUA, save)
    def success(self, *values: object, sep: str = ' ', save: bool = False): self.log(f'(INFO) {self.prefix} {_values_to_string(*values, sep)}', colors.LIGHT_GREEN, save)
    def primary(self, *values: object, sep: str = ' ', save: bool = False): self.log(f'(INFO) {self.prefix} {_values_to_string(*values, sep)}', colors.LIGHT_PURPLE, save)
    def warning(self, *values: object, sep: str = ' ', save: bool = False): self.log(f'(WARNING) {self.prefix} {_values_to_string(*values, sep)}', colors.LIGHT_YELLOW, save)
    def danger(self, *values: object, sep: str = ' ', save: bool = False): self.log(f'(ERROR) {self.prefix} {_values_to_string(*values, sep)}', colors.LIGHT_RED, save)

def save_today_log(text: str):
    path = os.path.join('.polinv-logs', 'today.log')
    with open(path, 'a', encoding='utf-8') as file: file.write(text)

def log(text: str, color: str = colors.RESET, save: bool = False):
    log_time = datetime.now().strftime("%H:%M:%S")
    if save: save_today_log(log_time + ' > ' + text + '\n')
    print(f'{color}{text}{colors.RESET}')

def error(text: str):
    log_time = datetime.now().strftime("%H:%M:%S")
    save_today_log('(error) -> ' + log_time + ' > ' + text + '\n')
    print(f'{colors.RED}(error) -> {colors.LIGHT_RED}' + text + f'{colors.RESET}')

def info(*values: object, sep: str = ' ', save: bool = False): log(f'(INFO) {_values_to_string(*values, sep)}', colors.LIGHT_AQUA, save)
def success(*values: object, sep: str = ' ', save: bool = False): log(f'(INFO) {_values_to_string(*values, sep)}', colors.LIGHT_GREEN, save)
def primary(*values: object, sep: str = ' ', save: bool = False): log(f'(INFO) {_values_to_string(*values, sep)}', colors.LIGHT_PURPLE, save)
def warning(*values: object, sep: str = ' ', save: bool = False): log(f'(WARNING) {_values_to_string(*values, sep)}', colors.LIGHT_YELLOW, save)
def danger(*values: object, sep: str = ' ', save: bool = False): log(f'(ERROR) {_values_to_string(*values, sep)}', colors.LIGHT_RED, save)

def info_profile(profile: str, *values: object, sep: str = ' ', save: bool = False): info(f'({profile}) -> {_values_to_string(*values, sep)}', sep=sep, save=save)
def success_profile(profile: str, *values: object, sep: str = ' ', save: bool = False): success(f'({profile}) -> {_values_to_string(*values, sep)}', sep=sep, save=save)
def primary_profile(profile: str, *values: object, sep: str = ' ', save: bool = False): primary(f'({profile}) -> {_values_to_string(*values, sep)}', sep=sep, save=save)
def warning_profile(profile: str, *values: object, sep: str = ' ', save: bool = False): warning(f'({profile}) -> {_values_to_string(*values, sep)}', sep=sep, save=save)
def danger_profile(profile: str, *values: object, sep: str = ' ', save: bool = False): danger(f'({profile}) -> {_values_to_string(*values, sep)}', sep=sep, save=save)
