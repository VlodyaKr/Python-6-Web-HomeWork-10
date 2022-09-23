import re
from abc import ABC, abstractmethod

PAGINATOR_NUMBER = 3  # кількість записів для представлення
STRING_WIDTH = 80


class AbstractPaginator(ABC):

    @abstractmethod
    def get_view(self):
        pass


class Paginator(AbstractPaginator):
    def __init__(self, data):
        self.data = data

    def get_view(self, func):
        index, print_block = 1, '=' * STRING_WIDTH + '\n'
        is_empty = True
        data_values = self.data
        for record in data_values:
            is_empty = False
            print_block += func(record) + '\n' + '-' * STRING_WIDTH + '\n'
            if index < PAGINATOR_NUMBER:
                index += 1
            else:
                yield print_block
                index, print_block = 1, '=' * STRING_WIDTH + '\n'
        if is_empty:
            yield None
        else:
            yield print_block


def hyphenation_string(text) -> str:
    result, line = '', ''
    text_list = text.split()
    for word in text_list:
        if not line:
            line = word
        elif len(line) + len(word) > STRING_WIDTH + 1:
            result += line + '\n'
            line = word
        else:
            line += ' ' + word
    if line:
        result += line
    return result

