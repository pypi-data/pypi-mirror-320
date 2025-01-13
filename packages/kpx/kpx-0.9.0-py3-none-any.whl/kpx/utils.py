import os
from datetime import datetime, timezone


def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0

    return f"{num:.1f}Yi{suffix}"


def calculate_age(date_time_string: datetime):
    current_time = datetime.now(timezone.utc)
    delta = int((current_time - date_time_string).total_seconds())

    return convert_seconds_to_age(delta)


def convert_seconds_to_age(delta):
    output = ''
    enough_info = 0

    # show weeks
    if delta >= (3600 * 24 * 7):
        new_delta = delta / (3600 * 24 * 7)
        delta = delta % (3600 * 24 * 7)
        output += f'{int(new_delta)}w'
        enough_info += 1
    # show days
    if delta >= (3600 * 24):
        new_delta = delta / (3600 * 24)
        delta = delta % (3600 * 24)
        output += f'{int(new_delta)}d'
        enough_info += 1
        if enough_info >= 2:
            return output
    # show hours
    if delta >= 3600:
        new_delta = delta / 3600
        delta = delta % 3600
        output += f'{int(new_delta)}h'
        enough_info += 1
        if enough_info >= 2:
            return output
    # show minutes
    if delta >= 60:
        new_delta = delta / 60
        delta = delta % 60
        output += f'{int(new_delta)}m'
        enough_info += 1
        if enough_info >= 2:
            return output

    if delta > 0:
        output += f'{int(delta)}s'

    return output


def expand_filters(name_filter):
    if name_filter == '' or name_filter is None:
        return {}

    elements = name_filter.split(',')
    filters = {}
    for element in elements:
        key, value = element.split('=')
        filters[str(key).lower()] = value

    return filters


class IniUtils:
    @staticmethod
    def check_directory_exists(file_path):
        os.makedirs(file_path, exist_ok=True)


class Output:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def header(text):
        print(f'{Output.HEADER}{text}{Output.ENDC}')

    @staticmethod
    def success(text):
        print(f'{Output.OKGREEN}{text}{Output.ENDC}')

    @staticmethod
    def error(text):
        print(f'{Output.FAIL}{text}{Output.ENDC}')
