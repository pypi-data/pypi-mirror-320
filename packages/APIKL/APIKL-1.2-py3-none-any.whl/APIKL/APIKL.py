import os.path
from os import listdir
from os.path import isfile, join, splitext
from APIKL.Found import Found
import math
import re


def get_chance(password):
    chance = 0
    if re.match(r"[\w:!@.#$%&*(\[\])=\-+]+", password) and len(password) >= 8:
        byte_values = password.encode()
        frequency_array = [0] * 256

        for byte_val in byte_values[:-1]:
            frequency_array[byte_val] += 1

        ent = 0
        total_bytes = len(byte_values) - 1

        for freq in frequency_array:
            if freq != 0:
                prob_byte = freq / total_bytes
                ent -= prob_byte * math.log2(prob_byte)
        chance += (math.log(ent) * 10 % 10 * 1.9 + 1) if ent >= 3 else 0
        # in documentation this formula is a little different
        # l = Math.log(entropy);
        # q = Math.floor(l);
        # 19 * (l - q) + 1;
    return chance


class APIKL:
    def __init__(self, user_files=None, probability: int = 5):
        if user_files is None:
            user_files = ['.']
        self._found = []
        self._user_files = self.__get_files_to_check(user_files)
        self._probability = probability

    @property
    def probability(self):
        return self._probability

    @probability.setter
    def probability(self, probability):
        self._probability = probability

    @property
    def user_files(self):
        return self._user_files

    @user_files.setter
    def user_files(self, user_files):
        self._user_files = user_files

    def __get_files_to_check(self, user_files):
        files_to_check = []
        for file in [file.replace('\\', '/') for file in user_files]:
            if not isfile(file):
                files_to_check += self.__rec_file(file)
            else:
                files_to_check.append(file)
        return files_to_check

    def __rec_file(self, directory):
        files = []
        # Проверяем, является ли directory директорий
        if not isfile(directory):
            # Получаем список всех файлов и поддиректорий внутри текущей директории
            contents = [join(directory, f) for f in listdir(directory)]
            # Рекурсивный обход поддиректорий
            for item in contents:
                if isfile(item):
                    files.append(item.replace('\\', '/'))
                else:
                    files.extend(self.__rec_file(item))
        else:
            # Если это файл, добавляем его в список
            files.append(directory)

        return files

    def __check_file(self, file_path):
        try:
            _, extension = splitext(file_path)
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = [line.lower().strip() for line in file]

            if extension == '.xml':
                for i, line in enumerate(lines):
                    self.__check_xml_pass(line, i, file_path)
            else:
                for i, line in enumerate(lines):
                    self.__check_pass(line, i, file_path)

        except FileNotFoundError as e:
            raise RuntimeError from e

    def __check_pass(self, line, i, file):
        if '"' in line:
            sign = '"'
        elif "'" in line:
            sign = "'"
        else:
            return

        pass_to_add = ""
        chance = 0
        self.__match_and_add(line, i, file, sign, pass_to_add, chance)

    def __match_and_add(self, line, i, file, sign, pass_to_add, chance):
        pattern = rf"{sign}(.*?){sign}"
        matches = re.findall(pattern, line)

        for match in matches:
            password = match.strip()
            current_chance = get_chance(password)

            if current_chance > chance:
                chance = current_chance
                pass_to_add = password

        if chance >= 1:
            # Добавляем найденную информацию в список 'found'

            self._found.append(Found(str(file), i + 1, chance, pass_to_add))

    def __check_xml_pass(self, line, i, file):
        count = line.count('<')

        if count >= 1:
            if '"' in line:
                sign = '"'
            elif "'" in line:
                sign = "'"
            else:
                sign = None

            pass_to_add = ""
            chance = 0

            if count == 2:
                password = line[line.find('>') + 1:line.rfind('<')].strip()
                current_chance = get_chance(password)

                if current_chance > chance:
                    chance = current_chance
                    pass_to_add = password

            if sign:
                self.__match_and_add(line, i, file, sign, pass_to_add, chance)
        else:
            password = line.strip()
            chance = get_chance(password)

            if chance >= 1:
                # Добавить в список 'found'
                self._found.append(Found(str(file), i + 1, chance, password))

    def find_keys(self, user_files: list = None):
        self._found = []
        files_to_check = self._user_files if user_files is None else self.__get_files_to_check(user_files)
        for file in files_to_check:
            self.__check_file(file)
        found = sorted(self._found, key=lambda x: x.get_output_key_chance(), reverse=True)

        if len(found) == 0:
            print('Nothing found')
        else:
            print('Found:')
            for f in found:
                if f.get_output_key_chance() >= self._probability:
                    print(
                        f"      {f.password if len(f.password) <= 32 else f.password[0:32] + '...'} at "
                        f"{os.path.relpath(f.file_name).replace('\\', '/')}:"
                        f"{f.line} with probability "
                        f"{int(f.get_output_key_chance())}")
