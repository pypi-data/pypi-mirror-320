import time
from datetime import datetime
import os
import requests
import socket
import json
import itertools
from collections import Counter
import random
import math
import shutil
def write (text):
    print(text)

def get_lenth(text):
    return len(text)

def create_file (filename):
    open(filename, "x")

def write_to_file(filename, text):
    open(filename, "a").write(text)

def read_file(filename):
    x = open(filename, "r")
    print(x.read())

def close_file(filename):
    filename.close()

def ask(text):
    input(text)

def convert_to_upper(text):
    return text.upper()

def convert_to_lower(text):
    return text.lower()

def trim(text):
    return text.strip()

def replace_text(text, old, new):
    return text.place(old,new)

def split_text(text, sep=None):
    return text.split(sep)

def add_item(lst, item):
    lst.append(item)

def remove_item(lst, item):
    lst.remove(item)

def find_index(lst, item):
    return lst.index(item)

def count_item(lst, item):
    return lst.count(item)

def sort_list(lst):
    lst.sort()

def get_value(d, key, defult=None):
    return d.get(key, defult)

def add_key_value(d, key, value):
    d[key] = value

def remove_key(d, key):
    return d.pop(key)

def get_keys(d):
    return list(d.values())

def absolute(x):
    return abs(x)

def power(x, y):
    return pow(x, y)

def round_number(x , n = 0):
    return round(x, n)

def minimum(*args):
    return min(*args)

def maximum(*args):
    return max(*args)

def is_number(x):
    return isinstance(x, (int, float))

def is_text(x):
    return isinstance(x, str)

def is_list(x):
    return isinstance(x, list)

def is_dict(x):
    return isinstance(x, dict)

def create_set(iterable=None):
    return set(iterable)if iterable else set()

def add_to_set(s, item):
    s.add(item)

def remove_from_set(s, item):
    s.remove(item)

def check_in_set(s, item):
    return item in s

def set_length(s):
    return len(s)

def get_current_time():
    return time.time()

def sleep_for(secs):
    time.sleep(secs)

def get_current_datetime():
    return datetime.now()

def format_datetime(dt, format):
    return dt.strftime(format)

def parse_datetime(string, format):
    return datetime.strptime(string, format)

def apply_function(function, iterable):
    return list(map(function, iterable))

def filter_items(function, iterable):
    return list(filter(function, iterable))

def generate_range(start, stop=None, step=1):
    return list(range(start, stop, step)) if stop else list(range(start))

def enumerate_items(iterable, start=0):
    return list(enumerate(iterable, start))

def zip_items(*iterables):
    return list(zip(*iterables))

def try_except(try_block, except_block, exception_type=Exception):
    try:
        return try_block()
    except exception_type as e:
        return except_block(e)

def raise_error(message):
    raise Exception(message)

def assert_condition(condition, massage = "Assertion failed"):
    if not condition:
        raise AssertionError(massage)

def get_type(x):
    return type(x)

def is_instance(x, type):
    return isinstance(x, type)

def get_id(x):
    return id(x)

def show_help(x):
    return help(x)

def list_attributes(x):
    return dir(x)

def create_directory(path):
    os.mkdir(path)

def remove_directory(path):
    os.rmdir(path)

def list_directory(path):
    return os.listdir(path)

def check_file_exists(path):
    return os.path.exists(path)

def delete_file(path):
    os.remove(path)

def get_environment_variable(name):
    return os.getenv(name)

def set_environment_variable(key, value):
    os.environ[key] = value

def execute_command(command):
    return os.system(command)

def get_current_directory():
    return os.getcwd()

def change_directory(path):
    os.chdir(path)

def fetch_url(url):
    return requests.get(url).text

def download_file(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as file:
        file.write(response.content)

def send_post_request(url, data):
    return requests.post(url, data=data).text

def check_internet_connection():
    try:
        requests.get("https://google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False

def get_ip_address(hostname):
    return socket.gethostbyname(hostname)

def parse_json(json_string):
    return json.loads(json_string)

def convert_to_json(data):
    return json.dumps(data)

def read_json_file(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def write_json_file(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file)

def pretty_print_json(data):
    return json.dumps(data, indent=4)

def flatten_list(nested_list):
    return list(itertools.chain.from_iterable(nested_list))

def unique_items(lst):
    return list(set(lst))

def reverse_list(lst):
    return list[::-1]

def find_duplicates(lst):
    return [item for item, count in Counter(lst).items() if count > 1]

def shuffle_list(lst):
    random.shuffle(lst)
    return lst

def capitalize_first_letter(text):
    return text.capitalize()

def swap_case(text):
    return text.swapcase()

def count_substring(text, substring):
    return text.count(substring)

def starts_with(text, frefix):
    return text.startswith(frefix)

def ends_with(text, suffix):
    return text.endswith(suffix)

def is_even(x):
    return x % 2 == 0

def is_odd(x):
    return x % 2 != 0

def factorial(x):
    return math.factorial(x)

def gcd(a, b):
    return math.gcd(a, b)

def lcm(a, b):
    return math.lcm(a,b)

def merge_dicts(dict1, dict2):
    return {**dict1 , **dict2}

def invert_dict(d):
    return {v: k for k, v in d.items()}

def get_nested_value(d, keys):
    for key in keys:
        d = d.get(key)
        if d is None:
            return None
    return d

def filter_dict(d, condition):
    return {k : v for k, v in d.items() if condition(k, v)}

def sort_dict_by_key(d):
    return dict(sorted(d.items()))

def read_lines(filename):
    with open(filename, 'r') as file:
        return file.readlines()

def write_lines(filename, lines):
    with open(filename, 'w') as file:
        file.writelines(lines)

def append_to_file(filename, text):
    with open(filename, 'a') as file:
        file.write(text)

def copy_file(src, dst):
    shutil.copy(src, dst)

def move_file(src, dst):
    shutil.move(src, dst)