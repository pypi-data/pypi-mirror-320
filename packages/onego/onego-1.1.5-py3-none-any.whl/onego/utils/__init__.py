import time
import random
import requests
import threading

from onego import logger

try: from bs4 import BeautifulSoup
except ModuleNotFoundError as e:
    logger.danger('To use onego.utils "BeautifulSoup4" module is required', e)

def random_sleep(min: int = 1, max: int = 5): time.sleep(random.randint(min, max))

def create_thread_groups(list_: list, number_of_groups: int = 4):
    groups = []
    for _ in range(number_of_groups): groups.append([])
    n = 0
    for item in list_:
        groups[n].append(item)
        if n >= number_of_groups - 1: n = 0
        else: n += 1
    return groups

def make_threads(func, args: list[tuple]) -> list[threading.Thread]:
    threads = []
    for args_ in args: threads.append(threading.Thread(target=func, args=args_))
    return threads

def start_thread_groups(threads: list[threading.Thread]):
    for t in threads: t.start()

def join_thread_groups(threads: list[threading.Thread]):
    for t in threads: t.join()

def parse(res: requests.Response | str):
    if type(res) == str: return BeautifulSoup(res, 'html.parser')
    return BeautifulSoup(res.text, 'html.parser')

def str_contains_any(text: str, items: list[str]):
    for e in items:
        if str(e) in text: return True
    return False

def analyze_form(form: BeautifulSoup):
    form_data = { 'powrot': '1' }

    # Zbieranie wszystkich pól input, textarea, select z formularza
    for input_field in form.find_all(['input', 'textarea', 'select']):
        name = input_field.get('name')
        
        # Sprawdź, czy pole ma atrybut 'name', jeśli nie, to je pomijamy
        if not name:
            continue
        
        # Dla inputów sprawdzamy typ
        if input_field.name == 'input':
            input_type = input_field.get('type', 'text')  # Domyślnie 'text', jeśli typ nie jest podany

            if input_type in ['text', 'hidden', 'password', 'email', 'number', 'radio', 'submit', 'button', 'image']:
                # Dla input typu radio wybieramy tylko zaznaczone pole
                if input_type == 'radio':
                    if input_field.has_attr('checked'):
                        form_data[name] = input_field.get('value', '')
                else:
                    # Dla innych typów input pobieramy wartość
                    form_data[name] = input_field.get('value', '')

            elif input_type == 'checkbox':
                # Dla checkboxów zbieramy wszystkie zaznaczone wartości
                if input_field.has_attr('checked'):
                    if name in form_data:
                        if isinstance(form_data[name], list):
                            form_data[name].append(input_field.get('value', 'on'))
                        else:
                            form_data[name] = [form_data[name], input_field.get('value', 'on')]
                    else:
                        form_data[name] = input_field.get('value', 'on')

            elif input_type == 'file':
                # Dla plików wartość będzie zazwyczaj pusta, ponieważ pliki są przesyłane osobno
                form_data[name] = input_field.get('value', '')

        # Obsługa textarea
        elif input_field.name == 'textarea':
            form_data[name] = input_field.text

        # Obsługa select
        elif input_field.name == 'select':
            if input_field.has_attr('multiple'):
                # Zbieramy wszystkie zaznaczone opcje w select z multiple
                selected_options = [[option.get('value', ''), option.text] for option in input_field.find_all('option')] # selected=True
                form_data[name] = selected_options
            else:
                # Zbieramy tylko jedną wybraną opcję w select bez multiple
                selected_option = input_field.find('option', selected=True)
                if selected_option:
                    form_data[name] = selected_option.get('value', '')
                else:
                    first_option = input_field.find('option')
                    if first_option:
                        form_data[name] = first_option.get('value', '')

    return form_data

def calculate_time(func):
    def wrapper(*args, **kwargs):
        s = time.time()
        res = func(*args, **kwargs)
        e = time.time()
        logger.info(f'Execution time for function {func.__name__}: {round(e - s, 2)}s')
        return res
    return wrapper

class WaitFlag:

    def __init__(self, initial_value: bool = True) -> None:
        self.flag = initial_value
        self.initial_value = initial_value

    def reset(self): self.flag = self.initial_value

    def wait(self, interval_in_seconds: int = 1):
        while self.flag: time.sleep(interval_in_seconds)
    
    def stop(self): self.flag = not self.initial_value