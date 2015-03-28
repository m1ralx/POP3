import sys
import poplib
import encodings.utf_8
import base64
import quopri
from email.parser import Parser
import re
import getpass
parser = Parser()
pop = poplib.POP3_SSL('pop.yandex.ru', port=995)
user = getpass.getuser()
psw = getpass.getpass(prompt="Password: ")
# pop.user(user)
# pop.pass_(psw)
# pop.user('lyceum0960@yandex.ru')
# pop.pass_('vbauvbui')
# # print(pop.retr(16))
#
#
def decode_subject(inp):
    found = re.findall(r'=\?([a-zA-Z0-9-]+)\?([bqBQ])\?([a-zA-Z0-9/+=]{4,})={0,2}\?', inp.decode('utf8', 'ignore'))
    try:
        found = list(filter(bool, found[0]))
    except IndexError:
        return inp  # В случае если декодировать нечего (тема была написана латиницей)
    if found[1].upper() == 'B':
        text = base64.b64decode(found[2]).decode(found[0], 'replace')
    else:
        text = quopri.decodestring(found[2]).decode(found[0], 'replace')
    return 'Subject: {}'.format(text)
# print((pop.retr(16)))
msg = b""
for i in pop.retr(18)[1]:
    print(i.decode())
    # print(decode_subject(i))
    # msg += i + b" "
# print(msg)
# print(decode_subject(msg))
# # string = ''.join((bytes(x).decode() for x in pop.retr(3)))
# # print(pop.retr(3))
# # a = base64.b32encode(str.encode('qwerty'))
# # print(a)
# # print(bytes.decode(base64.b64decode(a)))


# import poplib
# import base64
# import quopri
# import re
#
#
# def convert(data):
#     """Преобразует нужным образом строку и возвращает её. В data[0] указана кодировка строки,
#     в data[1] как закодирована строка, а в data[2] содержится сама закодированная строка."""
#     if data[1].upper() == 'B':
#         text = base64.b64decode(data[2].replace(' ', '')).decode(data[0], 'replace')  #fixme Удалять пробелы не везде надо
#     else:
#         text = quopri.decodestring(data[2].replace(' ', '')).decode(data[0], 'replace')
#     return text
#
#
# def decode_mail(inp):
#     """Принимает строку с закодированными данными, из неё извлекает данные о кодировке, каким
#     образом закодированы данные и строка конвертируется в пригодный для чтения человеком вид."""
#     string = inp
#     found = re.findall(r'=\?([a-zA-Z0-9-]+)\?([bqBQ])\?([a-zA-Z0-9/+=_.?!@ <>]{2,})\?=', string)
#
#     if len(found) == 1:
#         decode_str = convert(found[0])
#         result = re.sub(r'=\?([a-zA-Z0-9-]+)\?([bqBQ])\?([a-zA-Z0-9/+=_.?!@ <>]{2,})\?=', decode_str, string)
#     elif len(found) > 1:  # Если в строке темы, записано несколько тем, то обрабатываем по особому
#         result = string
#         for i in found:
#             decode_str = convert(i)
#             result = re.sub(r'=\?([a-zA-Z0-9-]+)\?([bqBQ])\?([a-zA-Z0-9/+=_.?!@ <>]{2,})\?=', decode_str, result, count=1)
#     elif not found:  # Если тема написана латиницей, то декодировать нечего
#         return string
#
#     return result


# server = "pop.yandex.ru"
# port = "995"
# user = 'lyceum0960@yandex.ru'
# password = 'vbauvbui'
#
#
# mServer = poplib.POP3_SSL(server, port)
# mServer.user(user)
# mServer.pass_(password)
#
# messages = []
# senders = []
# from_ = []
#
# temp = ''
# flag = 0  # Сингнализирует о начале Темы письма и когда она заканчивается
# for index in range(1, len(mServer.list()[1]) + 1):
#     for i in mServer.top(index, 0)[1]:
#         i = i.decode('utf8')
#         # print(i)
#         if not re.match('\s', i):
#             flag = 0
#         if i.startswith('Subject'):
#             temp += i.strip()
#             flag = 1
#         if flag and re.match('\s', i):
#             temp += i.strip()
#
#         if i.startswith('Return-path'):
#             senders.append(i)
#
#         if i.startswith('From:'):
#             from_.append(i)
#
#     messages.append(temp)
#     temp = ''
#
# # for i in messages:
# #     print(decode_mail(i))
#
# print('\n')
# for i in from_:
#     found = re.findall(r'([a-z0-9_.-]+@[a-z0-9._-]+)>{0,1}', i)
#     # print(len(found))
#     if found:
#         email = found[-1] if len(found) > 1 else found[0]
#         # print('From:', email)
# # print(senders)
#
# mServer.quit()