import os


def read_input(file_path='', file_url='', source_type=''):
    if file_path:
        if not os.path.isfile(file_path):
            raise AssertionError(f'source {file_path} is not a valid file path')