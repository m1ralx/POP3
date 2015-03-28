import os
import os.path
import sys
import itertools


def get_extension(filename):
    """ Вернуть расширение файла """
    index = str(filename).rindex('.')
    return filename[index:]


def iterator_file_names(path):
    """
    Итератор по именам файлов в дереве.
    """
    for root, directories, files in os.walk(path):
        for name in files:
            yield os.path.join(root, name)


def with_extensions(extensions, file_names):
    """
    Оставить из итератора ``file_names`` только
    имена файлов, у которых расширение - одно из ``extensions``.
    """
    func = lambda x: get_extension(x) not in extensions
    result = itertools.filterfalse(func, file_names)
    for name in result:
        yield name


def project_stats(path, extensions):
    """
    Вернуть число строк в исходниках проекта.
    Файлами, входящими в проект, считаются все файлы
    в папке ``path`` (и подпапках), имеющие расширение
    из множества ``extensions``.
    """
    file_names = with_extensions(extensions, iterator_file_names(path))
    return total_number_of_lines(file_names)


def total_number_of_lines(file_names):

    """
    Вернуть общее число строк в файлах ``file_names``.
    """
    total_number = 0
    for file_name in file_names:
        total_number += number_of_lines(file_name)
    return total_number


def number_of_lines(file_name):
    """
    Вернуть число строк в файле.
    """
    number = 0
    with open(file_name, 'r', encoding='utf_8') as file:
        for _ in file:
            number += 1
    return number


def print_usage():
    print("Usage: python project_source_stats_3.py <project_path>")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print_usage()
        sys.exit(1)
    project_path = sys.argv[1]
    print(str(project_stats(project_path, {'.py'})))
